var $ = django.jQuery;
$(document).ready(function(){
  $('#id_language').prop('disabled',true);

  $('#id_is_translation_allowed').change(function(){
    var is_translation_allowed = $('#id_is_translation_allowed').is(":checked");
    if(is_translation_allowed){
      $('#id_language').prop('disabled',false);
    }
    else{
     $('#id_language').prop('disabled',true);
    }
  });


  $("form").submit(function(){
    var lang = $('#id_language').val();
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
                  'lang'      : lang.toString(),
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
                  'lang'      : '',
                },
                });
  	}
  });
});
