var $ = django.jQuery;
$(document).ready(function(){
	
   	$('#id_user').change(function(){
   	var u_name  = $('#id_user').val();	
	alert(u_name);
   	
   	$.ajax({
                type : "POST",
                url:"/statistics/get_languages/"+u_name,
                dataType : "json",
                
                success: function(data)
                {	alert(data);
                    $('#id_language').html(data);
                }
              });
   	});
});