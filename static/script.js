
$(document).ready(function() {
	if ("geolocation" in navigator) {
		navigator.geolocation.getCurrentPosition(function(position) {
			set_address_coords(position.coords.latitude, position.coords.longitude);
		});

		setTimeout(function(){
		navigator.geolocation.getCurrentPosition(function(position) {
			set_address_coords(position.coords.latitude, position.coords.longitude);
		});
		},10000)
	}

	function set_address_coords(lat, lng) {
		geocoder = new google.maps.Geocoder();
		coordinates = new google.maps.LatLng(lat, lng);

		geocoder.geocode({'latLng': coordinates}, function(results, status) {
		      if (status == google.maps.GeocoderStatus.OK) {
		        if (results[1]) {
		         	$('input#from_address').val(results[1].formatted_address);
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
});