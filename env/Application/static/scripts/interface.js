//window.onscroll = function() {myFunction()};

//var navbar = document.getElementById("mainNav");
var popup = document.getElementById("popup-container");

// Get the offset position of the navbar
//var sticky = navbar.offsetTop;

$(document).ready(function() {
  $('.error-message').each(function(i, obj) {
      obj.style.display = 'none';
  });
});

$( document ).ready(function() {
  $('#toggle-button').each(function(i, obj) {
      obj.style.display = 'none';
  });

});

$(document).ready(function(){
  var stars = document.getElementsByClassName('selection-star');
  var count = 1;
  $( ".selection-star").on( "click", function() {
    for(var i = 0; i < stars.length; ++i) {
      if (((window.getComputedStyle($(this)[0]).color) == 'rgb(255, 202, 40)') && (stars[i] == $(this)[0])) {
        $(stars[i]).css("color", "rgb(255, 202, 40)");
        for(var y = i ; y < stars.length; ++y) {
          $(stars[y + 1]).css("color", "rgb(175, 175, 177)");
        }
        break;
      }
      else {
        $(stars[i]).css("color", "rgb(255, 202, 40)");

        if (stars[i] == $(this)[0]) {
          break;
        }
      }
    }
});
});

function menubuttonclick () {
  //$('#mainNav').toggle('slow');
  header = document.getElementById("loginsignin-header");
  console.log('header '+ window.getComputedStyle(header).height + 'navbar' + window.getComputedStyle(navbar).height);
  //alert('header ' + header.height + 'Nav:' + navbar.height);
}

function select_star() {

}

window.onscroll = function () {
  var header = document.querySelector('#welcome-header');
  var navbar = document.querySelector("#mainNav");
  var isOut = isOutOfBound(header);
  var bouncing = header.getBoundingClientRect();
  if (bouncing.top <= -378) {
    console.log('out of bound');
    navbar.style.background = 'rgba(33, 37, 41, 0.7)';
    console.log(navbar);
  }
  else {
    navbar.style.background = 'transparent';
  }
}

function isOutOfBound (elem) {

	// Get element's bounding
	var bounding = elem.getBoundingClientRect();

	// Check if it's out of the viewport on each side
	var out = {};
	out.top = bounding.top < 0;
	out.left = bounding.left < 0;
	out.bottom = bounding.bottom > (window.innerHeight || document.documentElement.clientHeight);
	out.right = bounding.right > (window.innerWidth || document.documentElement.clientWidth);
	out.any = out.top || out.left || out.bottom || out.right;

	return out;

};
