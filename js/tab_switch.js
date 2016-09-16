
$(document).ready(function() {
    /*
    $(".nav-tabs a").click(function(){
        window.stop();
        $(this).tab('show');
        //alert('end...');
    });
    */

    $("#li_1").click(function(){
        window.stop();
        window.location.href='/';
    });

    $("#li_2").click(function(){
        window.stop();
        window.location.href='/tab2';
    });

});

