var updateBtns = document.getElementsByClassName('update-cart')

for (i = 0; i < updateBtns.length; i++) {
	updateBtns[i].addEventListener('click', function(){
		var productId = this.dataset.product
		var action = this.dataset.action
		console.log('productId:', productId, 'Action:', action)
		console.log('USER:', user)

		if (user === 'AnonymousUser'){
			console.log('User is not authenticated')
            alert('Please login to add items to cart')
		}else{
			updateUserOrder(productId, action)
		}
	})
}

function updateUserOrder(productId, action){
	console.log('User is authenticated, sending data...')

		var url = '/update_item/'

		fetch(url, {
			method:'POST',
			headers:{
				'Content-Type':'application/json',
				'X-CSRFToken':csrftoken,
			}, 
			body:JSON.stringify({'productId':productId, 'action':action})
		})
		.then((response) => {
		   return response.json();
		})
		.then((data) => {
		    location.reload()
		});
}

// Favorites Logic
var favBtns = document.getElementsByClassName('toggle-fav')

for (i = 0; i < favBtns.length; i++) {
    favBtns[i].addEventListener('click', function(e){
        e.preventDefault(); // Prevent default link behavior
        var productId = this.dataset.product
        console.log('Toggle Favorite:', productId)

        if (user === 'AnonymousUser'){
            alert('Please login to manage favorites')
        }else{
            toggleFavorite(productId, this)
        }
    })
}

function toggleFavorite(productId, btnElement){
    var url = '/toggle_favorite/'

    fetch(url, {
        method:'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken,
        }, 
        body:JSON.stringify({'productId':productId})
    })
    .then((response) => {
       return response.json();
    })
    .then((data) => {
        console.log('Success:', data);
        if(data.status === 'success'){
            // Toggle the heart icon style
            var icon = btnElement.querySelector('i');
            if(data.action === 'added'){
                icon.classList.remove('far');
                icon.classList.add('fas');
                icon.style.color = 'red';
            } else {
                icon.classList.remove('fas');
                icon.classList.add('far');
                icon.style.color = ''; // Reset color
            }
        }
    });
}
