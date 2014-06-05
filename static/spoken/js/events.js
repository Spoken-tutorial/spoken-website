/*
$(document).ready(function(){
	$acstate = $('.statedsss');
	$ac_university = $(".university");
	$ac_district = $(".districtss");
	$ac_city = $(".city");
	$ac_location = $(".location");
	$ac_pincode = $(".pincode");
	$acstate.attr("disabled");
	$acstate.change(function() {
		$("#similar-link").hide();
		var state = $(this).val();
		$.ajax({
			url: "/software-training/ajax-ac-state/",
			type: "POST",
			data: {
				state: state,
				fields: {'city':'city', 'district':'disable','university':'university'},
			},
			success: function(data) {
				console.log(data.city);
				if(data.university){
					$ac_university.html(data.university);
					$ac_university.removeAttr("disabled");
					$ac_university.trigger("chosen:updated");
				}else{
					$ac_university.html('<option>-- None -- </option>')
					$ac_university.attr("disabled", "disabled");
					$ac_university.trigger("chosen:updated");
					alert('No University found for this State!!');
				}
				if(data.district){
					$ac_district.html(data.district);
					$ac_district.trigger("chosen:updated");
					$ac_district.removeAttr("disabled");
				}else{
					$ac_district.html('<option>-- None -- </option>')
					$ac_district.trigger("chosen:updated");
					$ac_district.attr("disabled", "disabled");
					alert('No District found for this State!!');
				}
				if(data.city){
					$ac_city.html(data.city);
					$ac_city.trigger("chosen:updated");
					$ac_city.removeAttr("disabled");
				}else{
					$ac_city.html('<option>-- None -- </option>')
					$ac_city.trigger("chosen:updated");
					$ac_city.attr("disabled", "disabled");
					alert('No City found for this State!!');
				}
				//console.log("University = " + data[0]);
				//console.log("District = " + data[1]);
				//console.log("City = " + data[2]);
			}
		});
	});
	
	$ac_district.change(function(){
		var district = $(this).val();
		$.ajax({
			url: "/software-training/ajax-ac-location/",
			type: "POST",
			data: {
				district: district
			},
			success: function(data) {
				if(data){
					$ac_location.html(data);
					$ac_location.trigger("chosen:updated");
					$ac_location.removeAttr("disabled");
				}else{
					$ac_location.html('<option>-- None -- </option>')
					$ac_location.trigger("chosen:updated");
					$ac_location.attr("disabled", "disabled");
					alert('No Location found for this District!!');
				}
				//console.log(data);
			}
		});
	});
	
	$ac_location.change(function(){
		var location = $(this).val();
		$.ajax({
			url: "/software-training/ajax-ac-pincode/",
			type: "POST",
			data: {
				location: location
			},
			success: function(data) {
				if(data){
					$ac_pincode.val(data);
					$ac_pincode.removeAttr("disabled");
				}else{
					//$ac_pincode.attr("disabled", "disabled");
					alert('No pincode found for this Location!!');
				}
				//console.log(data);
			}
		});
	});
});
/*
/* choosen update */
$(".chosen").chosen({width: "100%"});


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
	$.ajax({
		url: "/software-training/ajax-ac-state/",
		type: "POST",
		data: {
			state: state,
			fields: fields,
		},
		success: function(data) {
			console.log(data);
			if(data.university){
				$ac_university.html(data.university);
				$ac_university.removeAttr("disabled");
				$ac_university.trigger("chosen:updated");
			}else{
				$ac_university.html('<option>-- None -- </option>')
				$ac_university.attr("disabled", "disabled");
				$ac_university.trigger("chosen:updated");
				//alert('No University found for this State!!');
			}
			if(data.district){
				$ac_district.html(data.district);
				$ac_district.trigger("chosen:updated");
				$ac_district.removeAttr("disabled");
			}else{
				$ac_district.html('<option>-- None -- </option>')
				$ac_district.trigger("chosen:updated");
				$ac_district.attr("disabled", "disabled");
				//alert('No District found for this State!!');
			}
			if(data.city){
				$ac_city.html(data.city);
				$ac_city.trigger("chosen:updated");
				$ac_city.removeAttr("disabled");
			}else{
				$ac_city.html('<option>-- None -- </option>')
				$ac_city.trigger("chosen:updated");
				$ac_city.attr("disabled", "disabled");
				//alert('No City found for this State!!');
			}
		}
	});
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
		success: function(data) {
			if(data.institute){
				$ac_institute.html(data.institute);
				$ac_institute.trigger("chosen:updated");
				$ac_institute.removeAttr("disabled");
			}else{
				$ac_institute.html('<option>-- None -- </option>')
				$ac_institute.trigger("chosen:updated");
				$ac_institute.attr("disabled", "disabled");
				//alert('No City found for this State!!');
			}
			if(data.location){
				$ac_location.html(data.location);
				$ac_location.trigger("chosen:updated");
				$ac_location.removeAttr("disabled");
			}else{
				$ac_location.html('<option>-- None -- </option>')
				$ac_location.trigger("chosen:updated");
				$ac_location.attr("disabled", "disabled");
				//alert('No Location found for this District!!');
			}
			console.log(data);
		}
	});
}

//ajaxDistrictFillDatas('', 'institute');
