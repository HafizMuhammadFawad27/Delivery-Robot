// Add smooth scrolling to menu category links
document.addEventListener('DOMContentLoaded', function() {
    const menuLinks = document.querySelectorAll('.list-group-item');

    menuLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);

            window.scrollTo({
                top: targetElement.offsetTop - 100,
                behavior: 'smooth'
            });
        });
    });
});

// Add to cart functionality
function updateQuantity(itemId, change) {
    const action = change > 0 ? 'increase' : 'decrease';
    fetch(`/update_cart/${itemId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        }
    });
}

function removeItem(itemId) {
    fetch(`/remove_from_cart/${itemId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        }
    });
}

// Add to order button functionality
document.querySelectorAll('.add-to-order').forEach(button => {
    button.addEventListener('click', function() {
        const itemId = this.getAttribute('data-item-id');
        fetch(`/add_to_cart/${itemId}`, {
            method: 'POST'
        })
        .then(() => {
            this.classList.remove('btn-primary');
            this.classList.add('btn-success');
            this.textContent = 'Added to Cart';

            setTimeout(() => {
                this.classList.remove('btn-success');
                this.classList.add('btn-primary');
                this.textContent = 'Add to Cart';
            }, 2000);
        });
    });
});