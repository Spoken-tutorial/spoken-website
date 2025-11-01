$(document).ready(function(){
    //$('.banner-img').css({'width': $( window ).width()});
    setGoImageWith();
    $('.video-lists .video-item .thump').hover(function(){
        //console.log($(this).find('.video-item-playlist'));
        $(this).find('.video-item-playlist').slideToggle();
    });
    
});
$(window).bind("load", function() {
   setGoImageWith();
});
function setGoImageWith(){
    imgWidth = (10*$('.banner-img').height())/ 100
    $('.go-image').css({'width' : imgWidth});
}
$( window ).resize(function() {
    setGoImageWith();
});
function caller(){
    event.preventDefault();
    location.href = "https://ai.googleblog.com/2015/03/announcing-google-mooc-focused-research.html";
}

$(function(){
    // catch all a clicks
    $('a').click(function(){
        // check if has hash
        if(this.hash){
            // get rid of the # sign
            var hash  = this.hash.substr(1);
            console.log(hash);
            // get the position of the <a name>
            var $toElement = $("div[id="+hash+"]");
            console.log($toElement);
            var toPosition = $toElement.offset().top;
            
            //scroll / animate to that element
            $("body, html").animate({
                scrollTop : toPosition
            }, 2000, "easeOutExpo");
            
            // don't to the jump'
            return false;
        }
    });
    if(location.hash){
        var hash = location.hash;
        console.log(hash);
        window.scroll(0,0);
        $("a[href="+hash+"]").click();
    }
    
    //callback handler for form submit
    $("#ajaxform").submit(function(e)
    {
        var postData = $(this).serializeArray();
        var formURL = $(this).attr("action");
        console.log(postData[0].value);
        var error = 1
        if (postData[0].value == ''){
            error = 0
            $('.feedback-name').addClass('has-error');
            
        }else{
            $('.feedback-name').removeClass('has-error');
        }
        if (postData[1].value == ''){
            error = 0
            $('.feedback-email').addClass('has-error');
            
        }else{
            $('.feedback-email').removeClass('has-error');
        }
        if (postData[2].value == ''){
            error = 0
            $('.feedback-message').addClass('has-error');
            
        }else{
             $('.feedback-message').removeClass('has-error');
        }
        if(error) {
            $.ajax(
            {
                url : formURL,
                type: "POST",
                data : postData,
                success:function(data, textStatus, jqXHR)
                {
                    if(data){
                        //data: return data from server
                        $('.alert-success').remove();
                        message = '<div class="alert alert-success alert-dismissable"><button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button> Thank you for your valuable feedback.</div>';
                        $('#page4 .contact-container h2').after(message);
                        document.getElementById("ajaxform").reset();
                        //location.reload();
                    } else{
                        $('.alert-danger').remove();
                        message = '<div class="alert alert-danger alert-dismissable"><button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button> Something went wrong, will get back soon..</div>';
                        $('#page4 .contact-container h2').after(message);
                        document.getElementById("ajaxform").reset();
                    }
                        
                },
                error: function(jqXHR, textStatus, errorThrown)
                {
                    //if fails     
                }
            });
        }
        e.preventDefault(); //STOP default action
    });
});
