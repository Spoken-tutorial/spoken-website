var $ = django.jQuery;
$(document).ready(function(){

   	$('#id_user').change(function(){
   	var u_name  = $('#id_user').val();
    var selected_tut = $('#id_tutorial_detail').disabled = true;
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
    var lang = $('#id_language').val();
    if (lang)
      {

      $.ajax({
                type : "POST",
                url:"/creation/get_tutorials/"+fid+"/"+lang,
                dataType : "json",
                success: function(data)
                {
                    $('#id_tutorial_detail').html(data);
                }
              });
      }
    });

    $('#id_grant_to_all').change(function(){
    var grant_to_all = $('#id_grant_to_all').is(":checked");
    var selected_tut = $('#id_tutorial_detail');
    if(grant_to_all)
    {
      selected_tut.prop('disabled',true)
    }
    else
    {
      selected_tut.prop('disabled',false)
    }
    });

    $("form").submit(function(){
    var grant_to_all  = $('#id_grant_to_all').is(":checked");
    var status  = $('#id_status').is(":checked");
    var lang = $('#id_language').val();
    var fid  = $('#id_foss_category').val();
    var u_name  = $('#id_user').val();
    if(lang != 22 )
    {
      if(grant_to_all && status)
      {
        event.preventDefault();
        alert("Grant facility is available only for English Language");
        
      }

    }
    else
    {
      
      
      if(grant_to_all)
      {
        event.preventDefault();
        if (status) {
            $.ajax({
                type : "POST",
                url:"/creation/grant_role/",
                dataType : "json",
                data: {
                  'action'    : 'add',
                  'foss_id' : fid,
                  'user_id' : u_name,
                },
                success: function(data){
                  location.reload();
                }
                });
          }
      else{
            $.ajax({
                type : "POST",
                url:"/creation/grant_role/",
                dataType : "json",
                data: {
                  'action'  : 'remove',
                  'foss_id' : fid,
                  'user_id' : u_name,
                },
                success: function(data){
                  location.reload();
                }
                });
    }
      
    }
    
  }
  });
});
