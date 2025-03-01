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

// Add to order button functionality
document.querySelectorAll('.btn-primary').forEach(button => {
    if (button.textContent === 'Add to Order') {
        button.addEventListener('click', function() {
            this.classList.remove('btn-primary');
            this.classList.add('btn-success');
            this.textContent = 'Added to Order';
            
            setTimeout(() => {
                this.classList.remove('btn-success');
                this.classList.add('btn-primary');
                this.textContent = 'Add to Order';
            }, 2000);
        });
    }
});
