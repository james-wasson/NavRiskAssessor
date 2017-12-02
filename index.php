<?php

$htmlIncludes = file_get_contents(__DIR__."/includes.html");
$htmlHeader = file_get_contents(__DIR__."/header.html");
$cssHeader = file_get_contents(__DIR__."/header.css");
$htmlBody = file_get_contents(__DIR__."/body.html");
$cssBody = file_get_contents(__DIR__."/body.css");
$htmlMap = file_get_contents(__DIR__."/embededMap.html");
$jsMap = file_get_contents(__DIR__."/embededMap.js");
$cssMap = file_get_contents(__DIR__."/embededMap.css");
$htmlResults = file_get_contents(__DIR__."/results.html");
$jsResults = file_get_contents(__DIR__."/results.js");

echo "<html>
  <head>
  $htmlIncludes
  <style>$cssHeader</style>
  <style>$cssBody</style>
  <style>$cssMap</style>
  <script>$jsMap</script>
  <script>$jsResults</script>
  </head>
  <body>
  $htmlHeader
  $htmlBody
  <div class='container'>
  <div class='row'>
  <div class='col-md-6 map-overlay'>
  $htmlMap
  </div>
  <div class='col-md-6'>
  $htmlResults
  </div>
  </div>
  </div>
  </body>
</html>";


?>
