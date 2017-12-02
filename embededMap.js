
var API_KEY = "AIzaSyBDNKsAYHGJ6V_5KpSMhq21aJC5B44KN5Q";
var map;
var markers = []
var mapCircles = [];
var placesMaxDist = 160;
function initMap() {
  // init map
  map = new google.maps.Map(document.getElementById('map'), {
    center: {lat: 39.045753, lng: -76.641273},
    zoom: 7
  });

  // places markers
  map.addListener('click', function(e) {
    placeNewMarker(e.latLng, map);
  });

  // add clean all markers button
  map.controls[google.maps.ControlPosition.LEFT_TOP].push($('#clearMap')[0]);
  $('#clearMap').click(function () {
    removeAllCircles();
    while (markers.length > 0)
      markers.pop().setMap(null);
    reloadDisplayMarkers();
  });

  //add search bar
  var searchBox = new google.maps.places.SearchBox($('#pac-input')[0]);
  map.controls[google.maps.ControlPosition.TOP_LEFT].push($('#pac-input')[0]);
  addSearchBoxListener(searchBox)
}
async function placeNewMarker(latLng, map) {
  // add geocoding places
  disableResultsButton();
  findNearestRoad(latLng, function(nearRoad, error) {
    if (error) return disableResultsButton(false);
    getPlaces(latLng, function(nearby, error) {
      if (error) return disableResultsButton(false);
      // add a new marker at that lat/long
      var m = new google.maps.Marker({
        position: latLng,
        map: map
      });
      m['nearby'] = nearby;
      m['road'] = nearRoad;
      // push it to the global array
      markers.push(m);
      reloadDisplayMarkers();
      // add a remove on click event
      google.maps.event.addListener(m, 'click', function() {
        removeMarker(this);
      });
      disableResultsButton(false);
    });
  });
}

async function removeMarker(marker) {
  removeMarkerByIndex(markers.indexOf(marker));
}

async function removeCircle(marker) {
  mapCircles.map(function(c, i, obj) {
    if (c.marker == marker) {
      c.circle.setMap(null);
      obj.splice(i, 1);
    }
  });
}

async function removeAllCircles() {
  while (mapCircles.length > 0)
    mapCircles.pop().circle.setMap(null);
}

async function removeMarkerByIndex(index) {
  markers[index].setMap(null);
  removeCircle(markers[index]);
  if (index >= 0) markers.splice(index, 1);
  reloadDisplayMarkers();
}

function addSearchBoxListener(searchBox) {
  searchBox.addListener('places_changed', function() {
    var places = searchBox.getPlaces();
    if (places.length == 0)
      return;

    // For each place, get the icon, name and location.
    places.forEach(function(place) {
      if (!place.geometry) {
        toastr.error('Place has no Geometry', "Error");
        return;
      }
      panToMapPlace(place);
    });
  });
}

async function panToMapPlace(place) {
  var bounds = new google.maps.LatLngBounds();
  if (place.geometry.viewport) {
    // Only geocodes have viewport.
    bounds.union(place.geometry.viewport);
  } else {
    bounds.extend(place.geometry.location);
  }
  map.fitBounds(bounds);
}

function panToMarkerIndex(i) {
  map.setZoom(15);      // This will trigger a zoom_changed on the map
  map.setCenter(markers[i].position);
}

function getPlaces(latlng, callback) {
  var service = new google.maps.places.PlacesService(map);
      service.nearbySearch({
        location: latlng,
        radius: placesMaxDist
      }, function (places, status) {
        if (status != google.maps.places.PlacesServiceStatus.OK) {
          toastr.error("Error Retreving Nearby Places.", "Error");
          return callback(null, true);
        }
        if (places.length <= 0 ) {
          toastr.error("No Nearby Places Not Found.", "Error");
          return callback(null, true);
        }
        places.forEach(function(p) {
          p.lat = p.geometry.location.lat();
          p.lng = p.geometry.location.lng()
          delete p.scope;
          delete p.id;
          delete p.icon;
          delete p.name;
          delete p.photos;
          delete p.vicinity;
          delete p.reference;
          delete p.html_attributions;
          delete p.geometry;
          delete p.place_id;
          delete p.opening_hours;
        });
        return callback(places);
      });
}

function getGeocoding(params, callback) {
  var geocoder = new google.maps.Geocoder;
  geocoder.geocode(params, function(results, status) {
    if (status !== 'OK') {
      toastr.error('Geocoder failed due to: ' + status, "Error");
      return callback(null, true);
    }
    return callback(results[0]);
  });
}

function findNearestRoad(latlng, callback) {
  var lng = latlng.lng, lat = latlng.lat;
  if (typeof(lat) === 'function') lat = lat()
  if (typeof(lng) === 'function') lng = lng()
  $.get('https://roads.googleapis.com/v1/nearestRoads?'+
  'points=' + lat + "," + lng +
  '&key=' + API_KEY,
  function(roadData) {
    if (!roadData.snappedPoints || roadData.snappedPoints.length <= 0) {
      toastr.error("Road not found nearby.", "Error");
      return callback(null, true);
    }
    getGeocoding({'placeId': roadData.snappedPoints[0].placeId}, function(geocode, error) {
      if (error) {
        toastr.error("Error getting road name.", "Error");
        return callback(null, true);
      }
      var returnObj = {};
      returnObj.name = geocode.formatted_address;

      geocode.address_components.forEach(function(addr) {
        if ($.inArray("route", addr.types) > -1)
          returnObj.roadname = addr.short_name;
        if ($.inArray("administrative_area_level_1", addr.types) > -1)
          returnObj.state = addr.short_name;
      });
      if (returnObj.roadname === undefined) returnObj.roadname = "Unknown";
      if (returnObj.state === undefined) returnObj.state = "";
      callback(returnObj);
    });
  });
}

var displayLoadingFun = null;
async function reloadDisplayMarkers() {
  if (displayLoadingFun != null)
    displayLoadingFun.stop();
  displayLoadingFun = this;
  var markerString = "";
  markers.forEach(function(m, i) {
    markerString += "<div class='displayedMarker'> <span onclick='panToMarkerIndex(" + i + ")'>" + (i+1) + ": " + m.road.name +
      "</span> <span class='fa fa-times close-marker' aria-hidden='true' onclick='removeMarkerByIndex(" + i + ")'></span></div>";
  });
  $('#displayMarkers').empty();
  $('#displayMarkers').html(markerString);
  displayLoadingFun = null;
}

