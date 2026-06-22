var $ = django.jQuery;
$(document).ready(function(){
  $("#id_is_translation_allowed").change(function(){
  	var is_translation_allowed  = $('#id_is_translation_allowed').is(":checked");
  	var status  = $('#id_status').is(":checked");
  	var foss_name  = $('#id_foss').val();
  	if(is_translation_allowed && status)
  	{
  		$.ajax({
                type : "POST",
                url:"/creation/update_tutorials/",
                dataType : "json",
                data: {
                  'action' 		: 'add',
                  'foss_name'	: foss_name,
                },                
                });
  	}
  	else{
  		$.ajax({
                type : "POST",
                url:"/creation/update_tutorials/",
                dataType : "json",
                data: {
                  'action' 		: 'remove',
                  'foss_name'	: foss_name,
                },                
                });
  	}
  });
});
