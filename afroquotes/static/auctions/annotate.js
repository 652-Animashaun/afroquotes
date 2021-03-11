// document.addEventListener('DOMContentLoaded', function() {

//   document.querySelector('#annotate').addEventListener('click', getAnnotate);
  
// });


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
			document.querySelector('#modalTitle').innerHTML= `Quote from ${song}`

			elemImg.innerHTML= `<img src="${image}" width="200px">`
			elem.innerHTML = `<blockquote class="blockquote"><p class="lead"> <mark>${Quote}</mark> </p><footer class="blockquote-footer"><a href="#">${song}</a><cite title="Source Title"><a href="#">${artist}</a></cite></footer> </blockquote>`
			
			elemAnno.innerHTML=`<p>${annotation}</p><p><span>Contributors: <em>${annotator}</em></span></p>`
			document.querySelector('#modquote').append(elem)
			document.querySelector('#artimage').append(elemImg)
			document.querySelector('#annotation').append(elemAnno)
					
		}
		

	})
}

