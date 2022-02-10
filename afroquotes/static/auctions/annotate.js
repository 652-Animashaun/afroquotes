document.addEventListener('DOMContentLoaded', function() {

	const upelem = document.querySelector('#upvote')
	const form= document.querySelector("#upvote-form")
	upelem.addEventListener('click', function(){
		form.submit()

	})

	document.querySelector('#submit-suggestion').addEventListener('click', writeSuggestion)
})

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
		.then(response=> response.json())
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



function getAnnotate(obj){
	document.querySelector('#modquote').innerHTML=""
	document.querySelector('#artimage').innerHTML=""
	document.querySelector('#annotation').innerHTML=""
	document.querySelector('#modalTitle').innerHTML=""
	
	var quoteId = obj.getAttribute('data-link');
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
		if (data.annotation==undefined){
			elemAnno.innerHTML=`<em><strong>${data.Error}</strong></em>`
			document.querySelector('#annotation').append(elemAnno)

		}
		
		else {
				
			const Quote = data.annotated_quote
			const artist = data.annotated_quote_artist
			const song = data.annotated_quote_song
			const image = data.annotated_quote_image
			const annotation = data.annotation
			const annotator = data.annotator
			const annoSuggest = data.annotationSugg
			const annotation_view_count= data.annotation_view_count
			console.log(`${annotation_view_count}`)
			
			document.querySelector('#modalTitle').innerHTML= `Quote from ${song}`

			elemImg.innerHTML= `<img src="${image}" width="200px">`
			elem.innerHTML = `<blockquote class="blockquote"><p class="lead"> <mark>${Quote}</mark> </p><footer class="blockquote-footer"><a href="#">${song}</a><cite title="Source Title"><a href="#">${artist}</a></cite></footer> </blockquote>`
			elem_view_count=`<div>${annotation_view_count}</div>`
			
			elemAnno.innerHTML=`<p>${annotation}</p><p><span>Contributors: <em>${annotator}</em></span></p>`
			document.querySelector('#modquote').append(elem)
			document.querySelector('#artimage').append(elemImg)
			document.querySelector('#annotation').append(elemAnno)
			document.querySelector('#view_count').append(elem_view_count)
					
		}
		

	})
}