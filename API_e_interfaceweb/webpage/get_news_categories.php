<?php

$query = http_build_query(array('text' => $_GET['text']));
$url = $_GET['endpoint'] . '?'. $query; 

$ch = curl_init();
$options = [
	CURLOPT_URL => $url,
	CURLOPT_HEADER => false
];
curl_setopt_array($ch, $options);

$response = curl_exec($ch);

curl_close($ch);