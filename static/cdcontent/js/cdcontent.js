$(document).ready(function(){
    $('.create_zip').prop('disabled', true); 

    // announcement
    var stop = 1
    $('#slideshow').hover(function(){
        stop = 0
    }, function(){
        stop = 1
    });
    if($(".announcement").length > 1){
        $("#slideshow > div:gt(0)").hide();
        setInterval(function() {
          if(stop){
              $('#slideshow > div:first')
                .fadeOut(0)
                .next()
                .fadeIn(0)
                .end()
                .appendTo('#slideshow');
             }
        },  5000);
    }
    $('.close').click(function(){
        $(".navbar-fixed-top").css({'top' : '0px', 'position' : 'fixed'});
        $("#header-wrapper").css({'height' : '0px'});
    });
    // announcement end

    // rate card effect    
    var coll = document.getElementsByClassName("collapsible");
    var i;

    for (i = 0; i < coll.length; i++) {
      coll[i].addEventListener("click", function() {
        this.classList.toggle("active");
        var content = this.nextElementSibling;
        if (content.style.maxHeight){
          content.style.maxHeight = null;
        } else {
          content.style.maxHeight = content.scrollHeight + "px";
        } 
      });
    }

    $('#div-close').click(function(event){
        $("#info").hide();
    });

    var $el, $ps, $up, totalHeight;

    $(".sidebar-box .button").click(function() {
      totalHeight = 0
      $el = $(this);
      $p  = $el.parent();
      $up = $p.parent();
      $ps = $('#info');
      $ps.each(function() {
        totalHeight += $(this).outerHeight();
      });
            
      $up
        .css({
          // Set height = instant jumpdown on removing max height
          "height": $up.height(),
          "max-height": 9999
        })
        .animate({
          "height": totalHeight
        });
      // fade out read more text
      $p.fadeOut();
      // avoid jump down of chevron
      return false;
    });
    // rate card effect end

    // clear level & language field on selecting new foss
    $('.foss_category').on("change", function(){
                $('.level').val('');
                $('.language').html('');
                if($('.foss_category').val() == '') {
                    $('.level').attr("disabled", "disabled");
                    $('.language').attr("disabled", "disabled");
                }else {
                    $('.level').removeAttr('disabled');
                }
    });
    // clear level & language field on selecting new foss end

    $('.level').on("change", function(){
        var foss = $('.foss_category').val();
        var level = $(this).val();
        $('.language').html('');
        $('.language').attr("disabled", "disabled");
        if(foss && level) {
            $.ajax({
                url: "/cdcontent/ajax-fill-languages/",
                type: "POST",
                data: {
                    foss: foss,
                    level: level
                },
                beforeSend: function() {
                    $('.ajax-refresh-language').show();
                },
                success: function(data) {
                    // loading languages
                    if(data) {
                        $('.language').html(data);
                        $('.language').removeAttr('disabled');
                    }
                    $('.ajax-refresh-language').hide();
                }
            });
        }
    });

    $('.add_foss_lang').on("click", function(){
        $('.added-foss').show();
        foss = $('.foss_category').val();
        level = $('.level').val();
        langs = JSON.stringify($('.language').val());
        selectedfoss = $('.selected_foss').val();
        if(foss && langs && level) {
            $.ajax({
                url: "/cdcontent/ajax-add-foss/",
                type: "POST",
                data: {
                    foss: foss,
                    langs: langs,
                    level: level,
                    selectedfoss: selectedfoss,
                },
                beforeSend: function() {
                    $('.add_foss_lang').css('display', 'none');
                    $('.ajax-refresh-add-foss').show();
                },
                success: function(data) {
                    data = JSON.parse(data);
                    if(data) {
                        data = JSON.stringify(data);
                        if(data != '{}') {
                            $('.selected_foss').val(data);
                             selectedfoss = $('.selected_foss').val();
                        } else {
                            $('.selected_foss').val('');
                        }
                    }
                    selectedfoss: $('.selected_foss').val();
                    show_added_foss(selectedfoss);
                    $('.ajax-refresh-add-foss').hide();
                    $('.add_foss_lang').show();
                }
            });
            $('.add_foss_lang').show();
            $('.ajax-refresh-add-foss').hide();
        }
    });

    $(".cdcontentform").on( "submit", function(event) {
                event.preventDefault();
                var url = $(location).attr('href');
                $('.download-link').html('<i class="fa fa-circle-o-notch fa-spin fa-3x fa-fw"></i><span class="sr-only">Loading...</span> please do not refresh the page, we are preparing your download link');
                var posting = $.post(url, $(this).serialize());
                posting.done(function(data) {
                    if(data.status) {
                        var downloadLink = '<a href="' + data.path + '" title="Download CD Content Zip" id="download-zip-btn">Download CD Content</a>';
                        var message = 'You are part of our paid service.<br> Happy Downloading.'
                        $('.download-link').html(downloadLink);
                        $('.user-message').html(message);
                    } else {
                        var message = 'Somethings went wrong! please refresh the page and try again.'
                        $('.download-link').html(message);
                    }
                });
                posting.fail(function() {
                    var message = 'Something went wrong! please refresh the page and try again.'
                    $('.download-link').html(message);
                });
    });

    $('#otp_value').on('keyup',function(){
        var otp = $('#otp_value').val();
        var email = $('#id_email').val();

        if(otp.length>6){
        $.ajax({
            url:"/donate/validate",
            type:"POST",
            data:{
                "otp":otp,
                "email":email,
            },
            success: function(data) {
            if(data['validate']=='success'){
              $('#registered-success-msg').show();
        document.getElementById("otp_sent_msg").innerHTML = "Login Successfull";
        document.getElementById('otp_sent_msg').className = 'label label-success';
        $("#otp_sent_msg").show();
        document.getElementById("make_payment").disabled = false;

        }
            else {
        document.getElementById("otp_sent_msg").innerHTML = "Invalid OTP";
        document.getElementById('otp_sent_msg').className = 'label label-danger';
        $("#otp_sent_msg").show().delay(10000).fadeOut();
        }
        }

        });
        $("#otp_value").hide();
        $("#otp_value").show();
        }
    });


    $('#paymodal').on('show.bs.modal', function (event) {
        var foss_lang_obj = JSON.parse(selectedfoss);
        var foss_selected = [];
        var langs_selected = [];
        var level_selected = [];

        for(var key in foss_lang_obj) {
            var value = foss_lang_obj[key];
            var langs = value[0];
            l = String(langs);
            foss_selected.push(key);
            langs_selected.push(value[0]);
            level_selected.push(value[1]);
            langs_selected.push('|');
        }
        var amount = $('#amount_to_pay').val();

        var modal = $(this);
        modal.find('.modal-body input[name="amount"]').val(amount)
        modal.find('.modal-body input[name="amount"]').prop("readonly", true);

        if (foss_selected && langs_selected) {
            modal.find('.modal-body input[name="foss_id"]').val(foss_selected);
            modal.find('.modal-body input[name="language_id"]').val(langs_selected);
            modal.find('.modal-body input[name="level_id"]').val(level_selected);
            var row_count = document.getElementById("display-foss").rows.length;
        for (var i = 0 ;i < row_count; i++) {
            var x = document.getElementById("display-foss").rows[i].cells.length;
            if (x==5) {
                var row = document.getElementById("display-foss").rows[i];
                row.deleteCell(-1);
            }    
        }
    }        
});

    $('#download_btn').click(function() {
        $('#paymodal').modal('hide');
        $('#rate-div').hide();


    });
    
});

function delete_foss(elem){
    var foss_id = elem.parentNode.id;
    var foss_lang_obj = JSON.parse(selectedfoss);
    var foss_to_delete = foss_lang_obj[foss_id];
    var langs = foss_to_delete[0];
    var size = foss_to_delete[1];
    delete foss_lang_obj[foss_id];
    selectedfoss = JSON.stringify(foss_lang_obj);
    $('.selected_foss').val(selectedfoss);
    var add_foss_btn = document.getElementsByClassName("add_foss_lang");
    show_added_foss(selectedfoss);
    if (Object.keys(foss_lang_obj).length === 0) {
        $('.added-foss').hide();
        document.getElementById("amount_to_pay").value = '0';
    }
    $('.ajax-refresh-add-foss').hide();
    $('.add_foss_lang').show();
}

function send_otp(){
        $("#send_otp").show();
        document.getElementById("otp_sent_msg").innerHTML = "OTP sent";
        document.getElementById('otp_sent_msg').className = 'label label-success';
        $("#otp_value").show();
        $("#otp_sent_msg").show().delay(10000).fadeOut();
}

function show_added_foss(selected_foss){
    $.ajax({
        url: "/cdcontent/ajax-show-added-foss/",
        type: "POST",
        data: {
            selectedfoss : selected_foss,
        },
        beforeSend: function() {
            $('.add_foss_lang').css('display', 'none');
            $('.ajax-refresh-add-foss').show();
        },
        success: function(data) {
        header = '<caption class="col-left"><b>Selected FOSS List:<span class="pull-right"> ~ Total Size : '+data[1]+'</span></b></caption><tr ><th>FOSS</th><th>Level</th><th>Languages</th><th>Size</th>';
        if(data) {
            $('.added-foss').html(header + data[0]);
                                    
        var foss_table = document.getElementById("added-foss");
        var row_count = document.getElementById("added-foss").rows.length;
        for (var i = 0 ;i < row_count; i++) {
            var x = document.getElementById("added-foss").rows[i].cells.length;
            if (x==5) {
                var content = '<button type="button" class="btn delete-btn" class="delete-foss" onclick="delete_foss(this)"><i class="fa fa-trash-o"></i></button>'
                var td = document.getElementById("added-foss").rows[i].cells[4];
                td.innerHTML = content;   
            }    
        }
        if(data[2][0]=='UR') {
        var message = ''
         $('.create_zip').prop('disabled', true);
         $('.user-message').html(message);
         $('.download-a').html("Download");
         $("#rate-div").show();
         // $("#user_file_size").html("Foss Purchase (INR)");
        document.getElementById("amount_to_pay").value = data[2][1];
        }
        if(data[2][0]=='RP') {
        var message = 'You are part of our paid service.<br> Happy Downloading.<br> Please click on <b>Create Zip file</b> to proceed.'
         $('.create_zip').prop('disabled', false);
         $('.user-message').html(message);
         $('.download-a').html("Download");
         $("#rate-div").hide();
         $('.user-message').addClass("user-message-highlight");
        }
        else {
         $('.create_zip').prop('disabled', true);
         $('.user-message').html(message);
         $('.download-a').html("Download");

         $("#rate-div").show();
         // $("#user_file_size").html("Foss Purchase (INR)");
         document.getElementById("amount_to_pay").value = data[2][1];
        }
        if (Object.keys(JSON.parse(selectedfoss)).length === 0) {
            document.getElementById("amount_to_pay").value = '0';
        }
        }
        $('.ajax-refresh-add-foss').hide();
        }
    });
}






