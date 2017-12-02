<?php
  $dataArry = $_GET['userData'];

  $r = shell_exec("python processData.py '" . json_encode($dataArry). "'");
  // Decode the result
  $processed = json_decode($r, true);

  if ($processed["status"] != "OK") {
    echo "python processData.py '" . json_encode($dataArry). "'\n";
    echo "Processing Error";
    return http_response_code (400);
  }

  $r = shell_exec("python normalize.py '" . json_encode($processed["data"]). "'");
  // Decode the result
  $normalized = json_decode($r, true);

  if ($normalized["status"] != "OK") {
    echo "Normalization Error";
    return http_response_code (400);
  }

  $r = shell_exec("python k-means.py '" . json_encode($normalized["data"]). "'");

  $kMeans = json_decode($r, true);

  if ($kMeans["status"] != "OK") {
    echo "K-means Processing Error";
    return http_response_code (400);
  }
  $scoresMap = array();
  for ($i = 0; $i < count($kMeans['data']['Scores']); $i++) {
    array_push ($scoresMap, array(
      "Score" => $kMeans['data']['Scores'][$i],
      "Origin" => $dataArry[$i]
    ));
  }
  $kMeans['data']['Scores'] = $scoresMap;
  echo json_encode($kMeans);
?>