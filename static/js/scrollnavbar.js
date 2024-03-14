$(window).scroll(function(){
    if ($(this).scrollTop() > 50) {
       $('#nav').addClass('nav_black');
    } else {
       $('#nav').removeClass('nav_black');
    }
});