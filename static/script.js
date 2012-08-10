
$(document).ready(function() {
	if ("geolocation" in navigator) {
		navigator.geolocation.getCurrentPosition(function(position) {
			set_address_coords(position.coords.latitude, position.coords.longitude);
		});

		/* setTimeout(function(){
		navigator.geolocation.getCurrentPosition(function(position) {
			set_address_coords(position.coords.latitude, position.coords.longitude);
		});
		},10000) */
	}

	function set_address_coords(lat, lng) {
		geocoder = new google.maps.Geocoder();
		coordinates = new google.maps.LatLng(lat, lng);

		geocoder.geocode({'latLng': coordinates}, function(results, status) {
		      if (status == google.maps.GeocoderStatus.OK) {
		        if (results[1]) {
		        	if($('input#from_address'))
		        	{
		         		$('input#from_address').val(results[1].formatted_address);
		        	}
		        }
		      } else {
		       	console.log('Geocoding failed')
		      }
		    });
	}

	var autocomplete = new google.maps.places.Autocomplete(document.getElementById('to_address'), {types:['geocode'], componentRestrictions: {'country': 'GB'}});

	google.maps.event.addListener(autocomplete, 'place_changed', function() {
		var place = autocomplete.getPlace();
	});

	var autocomplete = new google.maps.places.Autocomplete(document.getElementById('from_address'), {types:['geocode'], componentRestrictions: {'country': 'GB'}});

	google.maps.event.addListener(autocomplete, 'place_changed', function() {
		var place = autocomplete.getPlace();
	});

	var init_step_val = $('input#step_count').val();
	var init_current_step = 1;

	function check_steps()
	{
		if(init_current_step > 1)
		{
			$('div#prev_step').show();
		}
		else
		{
			$('div#prev_step').hide();
		}

		if(init_current_step == init_step_val)
		{
			$('div#next_step').hide();
		}
		else
		{
			$('div#next_step').show();
		}
	}

	$('div#next_step').click(function(){

		$('div#step-'+init_current_step).hide();
		init_current_step += 1;
		$('div#step-'+init_current_step).show();

		check_steps();

	});

	$('div#prev_step').click(function(){
		$('div#step-'+init_current_step).hide();
		init_current_step -= 1;
		$('div#step-'+init_current_step).show();

		check_steps();

	});

});