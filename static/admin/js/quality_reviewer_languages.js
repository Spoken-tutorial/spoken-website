var $ = django.jQuery;
$(document).ready(function(){
	
   	$('#id_user').change(function(){
   	var u_name  = $('#id_user').val();	
   	$.ajax({
                type : "POST",
                url:"/creation/get_quality_languages/"+u_name,
                dataType : "json",
                success: function(data)
                {	
                    $('#id_language').html(data);
                }
              });
   	});

    });
