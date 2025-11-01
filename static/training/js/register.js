$(document).ready(function(){
$('#id_email').on('focusout',function(){
      var username = $('#id_name').val();
alert(username);
      var email = $('#id_email').val();
alert(email);
      $.ajax({
          url:'/donate/send_onetime/',
          type:"POST",
          data:{
              'username': username,
              'email': email,
              csrfmiddlewaretoken: '{{ csrf_token }}',
          },
        success: function(data) {
            if (data['valid_email']=='1') {
            $('#email-info').html('');
            if(data['message']=="active_user"){
                $("#send_otp").hide();
                $("#pwd").show();
                $("#forgot_pwd").show();
                $("#email-info").html('This Email Id is already registered with Spoken Tutorials. Please enter your password to proceed.');
                document.getElementById("email-info").style.color = "green";
            }
            else if(data['message']=='inactive_user'){
                document.getElementById("otp_sent_msg").innerHTML = "OTP Re-sent";
                document.getElementById('otp_sent_msg').className = 'label label-success';
                $("#otp_sent_msg").show().delay(10000).fadeOut();
            }
            else{
              $("#send_otp").show();
            }
            }else{
                $('#email-info').html(data['email_validation']);
            }      
        }
    });
    });


$('#pwd').on('focusout',function(){
        $('#invalid_credentials').html('');
        var username = $('#id_name').val();
        var email = $('#id_email').val();
        var password = $('#id_password').val();
        $.ajax({
            url:'/donate/validate_user/',
            type:'POST',
            data:{
                'username': username,
                'email': email,
                'password': password,
                csrfmiddlewaretoken: '{{ csrf_token }}',
            },
            success: function(data) {
              if (data['error_msg']=='') {
                var r = data['organizer_paid'];
                if (data['organizer_paid']=='1') {
                  $('#organizer_info').show();
                  $('#download_btn').show();
                  $('#make_payment').hide();
                  $('#id_amount').parent().hide();
                  $('#id_country').parent().hide();
                  $('#id_state').parent().hide();
                  $('#id_gender').parent().hide();
                  $('#id_gender').parent().hide();
                  $('#registered-success-msg').hide();
                  $('#otp_value').parent().hide();
                  $('#forgot_pwd').hide();
                  $("#email-info").hide();
                }
              }else{
                  $('#invalid_credentials').html(data['error_msg']);
              }       
            }
            });
        });
});
