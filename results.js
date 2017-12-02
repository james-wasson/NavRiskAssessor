var holdDisabledResult = false;
function disableResultsButton(dis=true) {
  if (!holdDisabledResult)
    if (dis)
      $("#runTheData").attr("disabled", true).css('opacity',0.5);
    else
      $("#runTheData").attr("disabled", false).css('opacity',1);
}
$().ready(function() {
  loadScores([]);
  $('#runTheData').click(function () {
    var Error = false;
    var carColor = $('#carColor').val().replace("#", "");
    if (carColor === undefined || parseInt(carColor, 16) < 0 || parseInt(carColor, 16) > parseInt("ffffff", 16)) {
      toastr.error("Car Color is Malformed", "Field Error");
      Error = true;
    }
    
    var carYear = $('#carYear').val();
    var year = (new Date()).getFullYear();
    if (carYear === undefined || carYear < 1900 || carYear > year + 2) {
      toastr.error("Car Year is Malformed, must be between 1900-"+(year + 2).toString(), "Field Error");
      Error = true;
    }
    
    var isComm = $('#isCommercial').is(":checked");
    if (isComm === undefined || isComm === null || (isComm != true && isComm != false)) {
      toastr.error("Commercial Vehicle is Malformed", "Field Error");
      Error = true;
    }
    
    var gender = $('#genderSelect').val();
    if (gender != 'F' && gender != 'M'  && gender != 'U') {
      toastr.error("Please Select Your Gender.", "Field Error");
      Error = true;
    }
    
    var state = $('#stateSelect').val();
    if (state === undefined || state === null || state == "") {
      toastr.error("Please Select Your State.", "Field Error");
      Error = true;
    }
    
    var race = $('#raceSelect').val();
    if (race === undefined || race === null || race == "") {
      toastr.error("Please Select Your Race.", "Field Error");
      Error = true;
    }
    
    if (markers.length <= 0) {
      toastr.error("Please pick some data point(s)", "Field Error");
      Error = true;
    }
    
    if (Error) return;
    
    removeAllCircles();

    var saveKeys = ["nearby", "lat", "lng", "road"]
    var buildObj = [];
    console.log(markers)
    markers.forEach(function(m) {
      obj = {}
      obj.Latitude = m.position.lat();
      obj.Longitude = m.position.lng();
      obj.nearby = m.nearby;
      for (var o in m.road)
        obj[o] = m.road[o];
      obj['Out Of State'] = state.toLowerCase() != m.road.state.toLowerCase()
      obj["Car Color"] = carColor;
      obj["Car Year"] = carYear;
      obj["Commercial Vehicle"] = isComm;
      obj["Gender"] = gender;
      obj["Race"] = race;
      buildObj.push(obj);
    });
    holdDisabledResult = true;
    $("#results-stats").hide();
    $("#results-spinner").fadeIn(1000);
    var onLoadFadeOut = function(){};
    disableResultsButton()
    var loadTime = new Date().getTime() / 1000;
    $.ajax({
      type: "GET",
      url: "./processData.php",
      data: { "userData": buildObj },
    }).done(function(res) {
      loadTime -= new Date().getTime() / 1000;
      data = jQuery.parseJSON(res).data
      toastr.success("Data Calculated!", "<h3 style='margin:0;padding:0;padding-left:10px;'>Success</h3>");
      loadStats(data)
      loadScores(data.Scores)
      data.Scores.forEach(function(s) {
        showMarkerScore(s)
      });
      onLoadFadeOut = function() {
        $("#results-stats").fadeIn(1000);
      }
    })
    .fail(function(data) {
      console.log(data.responseText)
      toastr.error(data.responseText, "<h3 style='margin:0;padding:0;padding-left:10px;'>Error</h3>");
    })
    .always(function() {
      holdDisabledResult = false;
      $("#results-spinner").fadeOut(1000, onLoadFadeOut);
      disableResultsButton(false);
    });
  });
  
  async function loadStats(scoreObj) {
    $("#avgRes").text(parseFloat(scoreObj["AverageScore"]).toFixed(4));
    $("#stdRes").text(parseFloat(scoreObj["StdDevScore"]).toFixed(4));
    $("#maxRes").text(parseFloat(scoreObj["MaxScore"]).toFixed(4));
    $("#minRes").text(parseFloat(scoreObj["MinScore"]).toFixed(4));
    $("#meanRes").text(parseFloat(scoreObj["MeanScore"]).toFixed(4));
  }
  
  async function loadScores(scores) {
    console.log(scores)
    var scoresString = "<div class='displayedScore'> <div class='row'>" + 
        "<div class='col-md-1'>" + "Index:" + "</div>" +
        "<div class='col-md-6'>" + "Name:" + " </div>" +
        "<div class='col-md-2'>" + "Score:"  + "</div>" +
        "<div class='col-md-3'>" + "Risk %:" + "</div></div>";
    scores.forEach(function (s, i) {
      scoresString += "<div class='row'>" + 
        "<div class='col-md-1'>" + (i+1) + "</div>" +
        "<div class='col-md-6'>" + s.Origin.name + " </div>" +
        "<div class='col-md-2'>" + parseFloat(s.Score.ScoreTrue).toFixed(2)  + "</div>" +
        "<div class='col-md-3'>" + parseFloat((1-s.Score.ScorePercent) * 100).toFixed(2) + "</div></div>";
    });
    $("#display-scores").html(scoresString + "</div>");
  }
  
  async function showMarkerScore(score) {
    var markerFound = false;
    // found a marker that matches, update that score
    var color = getCircleColor(score.Score.ScorePercent);
    var circle = new google.maps.Circle({
      strokeColor: color,
      strokeOpacity: 0.8,
      strokeWeight: 2,
      fillColor: color,
      fillOpacity: 0.3,
      map: map,
      center: new google.maps.LatLng(score.Origin.Latitude, score.Origin.Longitude),
      radius: 160
    });
    markers.forEach(function(m) {
      if(m.position.lat() == score.Origin.Latitude && m.position.lng() == score.Origin.Longitude) {
        markerFound = true;
        mapCircles.push({ "circle": circle, "marker": m });
      }
    });
    if (!markerFound) {
      mapCircles.push({ "circle": circle, "marker": null });
      circle.addListener('click', function () {
        this.setMap(null);
        var i = mapCircles.indexOf({ "circle": this, "marker": null });
        if (i > -1) mapCircles.splice(i, 1);
      });
    }
  }
  
  function getCircleColor(percentage) {
    var hue = (percentage * (120));
    return 'hsl(' + hue + ', 100%, 50%)';
  }
});
