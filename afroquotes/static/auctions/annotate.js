document.addEventListener('DOMContentLoaded', function() {
    // document.querySelector('#submit-suggestion').addEventListener('click', writeSuggestion);
    // const upelem = document.querySelector('#upvote')
    // const form= document.querySelector("#upvote-form")
    // document.querySelector("#submit-quote").addEventListener('click', submitQuote);
     // document.querySelector('#annotate_buttton').addEventListener('click', ()=>submit_annotation() )
     document.querySelector('#search').addEventListener('click', function(){
        const query=document.querySelector('#query_term').value
        console.log(query)
        search(query)
     })



    document.querySelector('#home').addEventListener('click',()=>load_quotes(1, `quotes`));
    
})

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
            
            // element.innerHTML = `<a id= email  data-link="${email_id}" onclick="getEmail(this); return false;"><span>from: ${sender}</span> <span>subject: ${subject}</span> <span class="justify-right">${date}</span></a>`

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
    // console.log(query)
    // const data = {value: `${query}`}]
    // const url = `search/${query}`
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


function writeSuggestion(){
    
    var suggestion = document.querySelector('#anno-suggestion').value
    var annoID = document.querySelector('#anno-suggestion').getAttribute('data-link')
    if(suggestion.length < 10){
        alert("You've written a suggestion of less than 10 characters?")
    }

    else {

        fetch(`/submitSugg/${annoID}`, {
        method: 'POST',
        body: JSON.stringify({
            submitedSugg:`${suggestion}`,
            annotationID: `${annoID}`
            })
        })
        .then(response=> {
            if (response.ok) {
                return response.json()
            }
            else if(response.status===404){
                return response.json()
            }
            else{
                return Promise.reject('there was an error: ' + response.json())
            }
        })
        .then(data=>{
            if (data.message != null){
                alert(data.message)
            }
            else{
                console.log(`${data.suggested}`)
            }
        })

    }
}

function submit_annotation(quote_id, form_input){
    console.log(form_input)
    fetch(`/annotate/${quote_id}`,{
        method:"POST",
        body:JSON.stringify({
            annotation:`${form_input}`,
        }),
    })
    .then(response=> {
        if (response.ok) {
            return response.json()
        }
        else if(response.status===404){

            return response.json()
        }
        else{
            return Promise.reject('there was an error: ' + response.json())
        }
    })

    .then(data=>{
        if (data.AuthenticationError){

            alert(`you need to login first`)
            window.location = "/login"

        }
        else{
            alert(`annotation submitted`)
            getAnnotate(quote_id)
            console.log(data)

        }
        
    })
}

function getAnnotate(obj){
    // document.querySelector('#modquote').innerHTML=""
    // document.querySelector('#artimage').innerHTML=""
    // document.querySelector('#annotation').innerHTML=""

    document.querySelector('#q_block').innerHTML=""
    console.log(obj)
    
    // var quoteId = obj.getAttribute('data-link');
    var quoteId=obj
    console.log(quoteId)
    fetch(`/annotation/${quoteId}`)
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
    .then(data=>{
        console.log(data)

        const elem = document.createElement('div')
        const elemImg = document.createElement('div')
        const elemAnno = document.createElement('div')
        const elem_view_count=document.createElement('div')
        const upvote_form_element = document.createElement('form')
        const upvote_count_element=document.createElement('span')
        const comment_accordion= create_element(`accordion_comment`)
        const submit_annotation_accordion= create_element(`submit-annotation`)
        const Quote = data['quote']['quote']
        const quote_id = data['quote']['id']
        const artist = data['quote']['artist']
        const song = data['quote']['song']
        const image = data['quote']['image']
        const annotation_block = document.querySelector('#q_block')
        elem.className='modquote col justify-content-center'
        elemImg.className='artimage col text-center'
        elemAnno.className='annotation col card-body'
        elem_view_count.className='view_count'
        annotation_block.className='card justify-content-center col-6'
        elemImg.innerHTML= `<img src="${image}" width="200px" class="rounded">`
        elem.innerHTML = `<blockquote class="blockquote"><p class="lead"> <mark>${Quote}</mark> </p><footer class="blockquote-footer"><a href="#">${song}</a><cite title="Source Title"><a href="#">${artist}</a></cite></footer> </blockquote>`
        // elem_view_count.innerHTML=`<div>views: ${annotation_view_count}</div>`
        annotation_block.append(elemImg)
        annotation_block.append(elem)
        annotation_block.append(elem_view_count)


        if (data.annotation=="None"){

            // render annotation form

            const annotation_form= document.createElement('div')
            annotation_form.className='row justify-content-center col-12'
            annotation_block.append(elemImg)
            annotation_block.append(elem)
            annotation_block.append(elem_view_count)
            
            annotation_form.innerHTML=`
               
                <div class="row col-12">
                <label for="annotation" class="form-label">Annotate</label>
                <textarea class="form-control" id="annotation" rows="3"></textarea>
                </div>
                
                <div class="row">
                <button id="annotate_buttton" class="btn btn-dark">Submit Annotation</button>
                </div>
            `
            annotation_block.append(annotation_form)
            // const form_input = document.querySelector('#annotation').value
            // document.querySelector('#annotate_buttton').addEventListener('click', console.log(form_input))

            document.querySelector('#annotate_buttton').addEventListener('click', ()=>submit_annotation(quote_id, document.querySelector('#annotation').value))


        }
        
        else {
                
            // const Quote = data.annotated_quote
            // const artist = data.annotated_quote_artist
            // const song = data.annotated_quote_song
            // const image = data.annotated_quote_image
            const annotation = data['annotation']['annotation']
            const annotation_id = data['annotation']['id']
            const annotator = data['annotation']['annotator']
            const annotation_view_count= data['annotation']['annotation_view_count']
            const upvoted = data['annotation']['upvoted']
            const upvotes = data['annotation']['upvotes']
            const comments = data['annotation']['comments']

            elemImg.innerHTML= `<img src="${image}" width="200px" class="rounded">`
            elem.innerHTML = `<blockquote class="blockquote"><p class="lead"> <mark>${Quote}</mark> </p><footer class="blockquote-footer"><a href="#">${song}</a><cite title="Source Title"><a href="#">${artist}</a></cite></footer> </blockquote>`
            elem_view_count.innerHTML=`<div>view(s): ${annotation_view_count}</div>`
            if (upvoted){
                upvote_form_element.innerHTML=`<i class="fa-solid fa-thumbs-up"><span class="up_count">${upvotes}</span></i>`
            }
            else {
                upvote_form_element.innerHTML=`<i class="fa fa-thumbs-o-up"><span class="up_count">${upvotes}</span></i>`
            }

            upvote_form_element.className='up_form'
            
            elemAnno.innerHTML=`<h5 class="card-title">Annotation</h5><p>${annotation}</p><p><span>contributor(s): <em>${annotator}</em></span></p>`
            annotation_block.className='card justify-content-center col-6'
            elemAnno.append(comment_accordion)
            annotation_block.append(elemImg)
            annotation_block.append(elem)
            annotation_block.append(elem_view_count)
            annotation_block.append(elemAnno)
            annotation_block.append(upvote_form_element)
            if (comments>0){
                comments.forEach(function(comment){
                    const comment_item = comment
                    const list_item = create_element(`comment_item`)
                    list_item.append(comment)
            })
            }
            else{
                comment_accordion.style.display='none'
            }
            

            // load upvote form

            upvote_form_element.addEventListener('click', () => upvote(annotation_id))
        }
        
    })

    
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

function submitQuote(){
    document.querySelector('#q_block').innerHTML=""
    const submit_quote = create_element(`submit_quote`)
    const create_form = document.createElement('form')
    create_form.action =`/submitquote`
    create_form.method='POST'

    create_form.className=`row`

    submit_quote.innerHTML=`
                            <div class="row">
                               <label for="exampleFormControlTextarea1" class="form-label">Write Quote</label>
                               <textarea class="form-control" id="exampleFormControlTextarea1" name="quote" rows="3"></textarea>
                            </div>
                            <div class="row">
                           <label for="exampleFormControlInput1" class="form-label">Source</label>
                           <input type="text" class="form-control" id="exampleFormControlInput1" name="source"placeholder="">
                            </div>
                            <div class="row">
                           <label for="exampleFormControlInput1" class="form-label">Artist</label>
                           <input type="text" class="form-control" id="exampleFormControlInput1" name="artist" placeholder="">
                            </div>
                            <div class="row">
                           <label for="exampleFormControlInput1" class="form-label">Image</label>
                           <input type="url" class="form-control" id="exampleFormControlInput1" name="image" placeholder="">
                            </div>
                            <div class="row">
                            <button type="submit" name="submit" id="exampleFormControlInput1" class="btn btn-dark">SubmitQuote</button>
                            </div>

                        `
    create_form.append(submit_quote)
    document.querySelector("#q_block").append(create_form)

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
