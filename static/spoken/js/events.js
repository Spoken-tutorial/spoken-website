/* choosen update */
function ajaxStrateFillDatas(district, city, university){
	$acstate = $('.state');
	$ac_university = $(".university");
	$ac_district = $(".district");
	$ac_city = $(".city");
	$ac_location = $(".location");
	$ac_pincode = $(".pincode");

	$district = district || "";
	$city = city || "";
	$university = university || "";
	fields = {};
	if($district) {
		fields['district'] = 'district';
	}
	if($city) {
		fields['city'] = 'city';
	}
	if($university) {
		fields['university'] = 'university';
	}
	state = $acstate.val();
	if (state) {
	    $.ajax({
		    url: "/software-training/ajax-ac-state/",
		    type: "POST",
		    data: {
			    state: state,
			    fields: fields,
		    },
		    beforeSend: function() {
		        if($district) {
		            $('.ajax-refresh-district').show();
		        }
		        if($city) {
		            $('.ajax-refresh-city').show();
		        }
		        if($university) {
		            $('.ajax-refresh-university').show();
		        }
            },
		    success: function(data) {
			    //console.log(data);
			    if(data.university){
				    $ac_university.html(data.university);
				    $ac_university.removeAttr("disabled");
				    $('.ajax-refresh-university').hide();
			    }else{
				    $ac_university.html('<option>-- None -- </option>')
				    $('.ajax-refresh-university').hide();
				    $ac_university.attr("disabled", "disabled");
				    //alert('No University found for this State!!');
			    }
			    if(data.district){
				    $ac_district.html(data.district);
				    $ac_district.removeAttr("disabled");
				    $('.ajax-refresh-district').hide();
			    }else{
				    $ac_district.html('<option>-- None -- </option>')
				    $ac_district.attr("disabled", "disabled");
				    $('.ajax-refresh-district').hide();
				    //alert('No District found for this State!!');
			    }
			    if(data.city){
				    $ac_city.html(data.city);
				    $ac_city.removeAttr("disabled");
				    $('.ajax-refresh-city').hide();
			    }else{
				    $ac_city.html('<option>-- None -- </option>')
				    $ac_city.attr("disabled", "disabled");
				    $('.ajax-refresh-city').hide();
				    //alert('No City found for this State!!');
			    }
		    }
	    });
	}
}

//ajaxStrateFillDatas('district');


function ajaxDistrictFillDatas(location, institute, district){
	$ac_institute = $(".institute");
	$ac_location = $(".location");
	$location = location || "";
	$institute = institute || "";
	fields = {}
	console.log("---> "+district);
	if($location) {
		fields['location'] = 'location';
	}
	if($institute) {
		fields['institute'] = 'institute';
	}
	/* see thread-user.js */
	$.ajax({
		url: "/software-training/ajax-district/",
		type: "POST",
		data: {
			district: district,
			fields: fields,
		},
		beforeSend: function() {
	        if($location) {
	            $('.ajax-refresh-location').show();
	        }
	        if($institute) {
	            $('.ajax-refresh-institute').show();
	        }
        },
		success: function(data) {
			if(data.institute){
				$ac_institute.html(data.institute);
				$ac_institute.removeAttr("disabled");
				$('.ajax-refresh-institute').hide();
			}else{
				$ac_institute.html('<option>-- None -- </option>')
				$ac_institute.attr("disabled", "disabled");
				$('.ajax-refresh-institute').hide();
				//alert('No City found for this State!!');
			}
			if(data.location){
				$ac_location.html(data.location);
				$ac_location.removeAttr("disabled");
				$('.ajax-refresh-location').hide();
			}else{
				$ac_location.html('<option>-- None -- </option>')
				$ac_location.attr("disabled", "disabled");
				$('.ajax-refresh-location').hide();
				//alert('No Location found for this District!!');
			}
			console.log(data);
		}
	});
}

//ajaxDistrictFillDatas('', 'institute');
