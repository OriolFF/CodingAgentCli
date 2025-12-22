
const hamburger = document.querySelector('.topbar-toggleBtn');
hamburger.addEventListener('click', function(e) {
  e.preventDefault();
  this.parentElement.toggleAttribute('active');
});