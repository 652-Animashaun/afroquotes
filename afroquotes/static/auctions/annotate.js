document.addEventListener('DOMContentLoaded', function() {
    const BASE_URL = `http://localhost:8000/`
    // document.querySelector('#submit-suggestion').addEventListener('click', writeSuggestion);
    const upvote_elem = document.querySelectorAll('.upvote')
    const up_annotation = [upvote_elem]
    console.log(up_annotation[0])
    up_annotation[0].forEach(function(upvote_ann){
        upvote_ann.addEventListener('click', function(){
            upvote(upvote_ann)
        })
    })
    const elements = document.querySelectorAll('.view-annotation')
    const annotations = [elements]
    console.log(annotations[0])

    annotations[0].forEach(function(annotation){
    annotation.addEventListener('click', function(){
        get_annotate_helper(annotation)
    })

    })
    const suggestion_form_elements = document.querySelectorAll('#suggestion_form')
    console.log(`${suggestion_form_elements}`)
    console.log(suggestion_form_elements.length)
    const suggestion_forms = [suggestion_form_elements]
    console.log(suggestion_forms[0].length)
    console.log(`${suggestion_forms[0]}`)
    suggestion_forms[0].forEach(function(suggestion){
    suggestion.addEventListener('submit', function(event){
        console.log(suggestion)
        event.preventDefault()
        writeSuggestion(suggestion)

        })
    })
    var dismiss_annnotation = document.querySelectorAll('.dismiss-annotation')
    dismiss_annnotation.forEach(function(dis_ann){
        dis_ann.addEventListener('click', function(){
            document.querySelector(`#anno_${dis_ann.dataset.link}`).style.display = 'none'
        })
    })

    var approve_annotation_elem = document.querySelectorAll('.approve-annotation')
    // var approve_annotation = [approve_annotation_elems]
    console.log(approve_annotation_elem)

    approve_annotation_elem.forEach(function(app_ann){
        var annotation_id = app_ann.dataset.link
        app_ann.addEventListener('click', function(){
            approve_annotation(annotation_id)
            document.querySelector(`#anno_${annotation_id}`).style.display = 'none'
        })
    })
     
})

function upvote(upvote_ann){
    var annotation_id = upvote_ann.dataset.link
    fetch(`${BASE_URL}upvote/${annotation_id}`)
    .then(response=>response.json())
    .then(data=>{
        console.log(data)
        if (data.Unauthorized){
            // alert(`Need to login to perform action.`)
            console.log("Need to login to perform action.")
            window.location.href = "/login"

        }
        else{

            upvote_ann_first_child_elem = upvote_ann.firstElementChild

            upvote_ann_first_child_elem.innerHTML = ""
            upvote_ann_first_child_elem.innerHTML = data.upvotes
        }

    })

}
function get_annotate_helper(annotation){
    var annotation_id = annotation.dataset.link
    var quote_element_id = annotation.dataset.target
    var clicked = annotation.dataset.clicked
    if (annotation_id){
        console.log(`fetch annotation ${annotation_id}`)
        var collapsible_block = document.querySelector(quote_element_id)
        console.log(collapsible_block)
        if (clicked=='false'){
            annotation.dataset.clicked='true'
            getAnnotate(annotation)
        } 
        else{
            annotation.dataset.clicked='false'
        }

    }

}

function load_quotes(page, url){
    // alert(`clicked-home`)
    if(url != null){
        var url = url
    }

    else{

        var url = `quotes`
    }

    fetch(`${url}?page=${page}`)
    .then(response=>response.json())
    .then(data=>{
        console.log(data)
        display_quotes(data, url)
    })
    
}

function display_quotes(data, url){
    console.log(data, url)
    const q_elem = document.querySelector('#q_block')
        q_elem.innerHTML=""
        // start loading quotes
        data.quotes.forEach(function(q){
            const element = document.createElement('blockquote')
            q_elem.className='row justify-content-center col-4'
            const quote = q.quote
            const id = q.id
            const image_url = q.image
            const song = q.song
            const contributor = q.contributor
            const created = q.date 
            const artist = q.artist
            element.className = 'blockquote row'
            
            element.innerHTML=`  <p class="lead text-center"> <mark><a class="quote_selector" data-link=${id}>${quote}</a></mark> </p><br><footer class="blockquote-footer"><a href="#">${artist} </a><cite title="Source Title"><a href="#">${song} </a></cite></footer>`

            q_elem.append(element)
        })

        _quote_block = document.querySelectorAll('.quote_selector')
        _quote_block.forEach(function(q_b){
            q_b.addEventListener('click', () => getAnnotate(q_b.getAttribute('data-link')));
            })
        

        const pagination_elem= document.createElement('div')
        pagination_elem.className= 'pagination'
        pagination_elem.innerHTML= `
            <span class="step-links">
                <button id="prev" data-link="${data.links.prev}">${data.links.prev}</button>
            </span>
            <span class="step-links">
                <button id="next" data-link="${data.links.next}">${data.links.next}</button>
            </span>`
        q_elem.append(pagination_elem)


        const prev_butt = document.querySelector('#prev')
        const next_butt = document.querySelector('#next')

        
        prev_butt.addEventListener('click', function(){
            load_quotes(document.querySelector('#prev').innerHTML, url)
        })
        next_butt.addEventListener('click', function(){
        load_quotes(document.querySelector('#next').innerHTML, url)
        })
}


function search(query, page=1){
    const url = `search`


    fetch(`${url}?q=${query}&page=${page}`)

    .then(response=>response.json())
    .then(data =>{
        console.log(data)
        if (data.NotFound){
            alert(data.NotFound)
        }
        else{
            display_quotes(data, `${url}`)
        }
        
    } )

}

function approve_annotation(annotation_id, approve=true){
    if (approve === true){
        fetch(`approve_annotation/${annotation_id}`)
        .then(response=> {
            if (response.ok) {
                return response.json()
            }
            else if(response.status===401){
        
                return response.json()
            }
            else {
                return Promise.reject('Error:' + response.status)
            }
        } )

    }

}


function writeSuggestion(suggestion_form){
    
    var suggestion = suggestion_form['comment'].value
    var annoID = suggestion_form['comment_anno_id'].value
    const csrftoken = getCookie('csrftoken')
    console.log(suggestion)
    if(suggestion.length < 10){
        data = {}
        data.Error = "You've written a suggestion of less than 10 characters?"
        errorHandler(data)
        // alert("You've written a suggestion of less than 10 characters?")
    }

    else {

        fetch(`submit_suggestion/${annoID}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': `${csrftoken}`,
        },
        body: JSON.stringify({
            submitedSugg:`${suggestion}`,
            annotationID: `${annoID}`
            })
        })
        .then(response=> {
            if (response.ok) {
                return response.json()
            }
            else if(response.status>=400){
                return response.json()
            }
            else{
                return Promise.reject('there was an error: ' + response.json())
            }
        })
        .then(data=>{
            if (data.Unauthorized){
                alert(`${data.Unauthorized}. You will be redirected to login.`)
                window.location.href = "/login"

            }
            else{
                console.log(`${data.suggested}`)
            }
        })

    }
}

function errorHandler(response){
    console.log(response.Error)
    var error_block = document.getElementById('error_display')
    console.log(error_block.children)
    message_board = error_block.children[0]
    if (response.Error){
        message_board.innerHTML = response.Error
        error_block.scrollIntoView({behavior:'smooth'}, true)

    }


}


function getAnnotate(obj){

    var target_elem = obj.dataset.target
    var annotation_id = obj.dataset.link
    var parent_elem = obj.parentElement
    var child_elem = parent_elem.children
    console.log(annotation_id)
    fetch(`/get_annotation/${annotation_id}`)
    .then(response=> {
        if (response.ok) {
            return response.json()
        }
        else if(response.status===404){
    
            return response.json()
        }
        else {
            return Promise.reject('some other shit you never thought of went down:' + response.status)
        }
    } )
    
}
function create_element(obj){
    if (obj==`accordion_comment`){
        const comment_block = document.createElement('div')
        comment_block.className='row justify-content-center'
        comment_block.innerHTML=`<div class="accordion" id="accordionExample">
                      <div class="accordion-item">
                        <h2 class="accordion-header" id="headingOne">
                          <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
                            View Comments
                          </button>
                        </h2>
                        <div id="collapseOne" class="accordion-collapse collapse show" aria-labelledby="headingOne" data-bs-parent="#accordionExample">
                          <div class="accordion-body">
                          <ul class="list-group comments-section list-group-flush">
                          </ul>

                          </div>
                        </div>
                      </div>
                    </div>`
    return comment_block
    }

    else if (obj==`comment_item`){
        const create_comment_item=document.createElement('li')
        create_comment_item.className='list-group-item'
    }
    else if (obj==`submit_quote`){
        return document.createElement('div')
    }

    else{
        return 
    }
    
}


function upvote(annotation_id){

    fetch(`/upvote/${annotation_id}`)
    .then(response=> {
        if (response.ok) {
            return response.json()
        }
        else if(response.status===400){
            return response.json()
        }
        else {
            return Promise.reject('some other shit you never thought of went down:' + response.status)
        }
    } )
    .then(data=>{

        
        const upvote_form_element= document.querySelector('.up_form')
        if (data.upvoted==true){
                upvote_form_element.innerHTML=`<i class="fa-solid fa-thumbs-up"><span class="up_count">${data.upvotes}</span></i>`
            }
            else {
                upvote_form_element.innerHTML=`<i class="fa fa-thumbs-o-up"><span class="up_count">${data.upvotes}</span></i>`
            }
    })

}



function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
