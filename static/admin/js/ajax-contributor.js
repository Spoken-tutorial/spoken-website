var $ = django.jQuery;
$(document).ready(function(){
	
   	$('#id_user').change(function(){
   	var u_name  = $('#id_user').val();	
   	$.ajax({
                type : "POST",
                url:"/creation/get_languages/"+u_name,
                dataType : "json",
                success: function(data)
                {	
                    $('#id_language').html(data);
                }
              });
   	});

    $('#id_foss_category').change(function(){
    var fid  = $('#id_foss_category').val(); 
    $.ajax({
                type : "POST",
                url:"/creation/get_tutorials/"+fid,
                dataType : "json",                
                success: function(data)
                { 
                    $('#id_tutorial_detail').html(data);
                }
              });
    });
    
});