window.onscroll = function() {myFunction()};

var navbar = document.getElementById("mainNav");
var popup = document.getElementById("popup-container");

// Get the offset position of the navbar
var sticky = navbar.offsetTop;

$( document ).ready(function() {
  $('.error-message').each(function(i, obj) {
      obj.style.display = 'none';
  });
});

$( document ).ready(function() {
  $('#toggle-button').each(function(i, obj) {
      obj.style.display = 'none';
  });

});

// Add the sticky class to the navbar when you reach its scroll position. Remove "sticky" when you leave the scroll position
function myFunction() {
  if (window.pageYOffset >= sticky) {
    navbar.classList.add("sticky");
    //alert('hey');
  } else {
    //navbar.classList.remove("sticky");
  }
}

function menubuttonclick () {
  //$('#mainNav').toggle('slow');
  header = document.getElementById("loginsignin-header");
  console.log('header '+ window.getComputedStyle(header).height + 'navbar' + window.getComputedStyle(navbar).height);
  //alert('header ' + header.height + 'Nav:' + navbar.height);
}
