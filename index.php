<?php

$htmlIncludes = file_get_contents(__DIR__."/includes.html");
$htmlHeader = file_get_contents(__DIR__."/header.html");
$cssHeader = file_get_contents(__DIR__."/header.css");
$htmlBody = file_get_contents(__DIR__."/body.html");
$cssBody = file_get_contents(__DIR__."/body.css");

echo "<html>
	<head>
	$htmlIncludes
	<style>$cssHeader</style>
	<style>$cssBody</style>
	</head>
	<body>
	$htmlHeader
	$htmlBody
	</body>
</html>";


?>
