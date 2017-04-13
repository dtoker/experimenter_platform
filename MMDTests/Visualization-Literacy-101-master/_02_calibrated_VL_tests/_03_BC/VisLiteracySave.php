<?php
$dir = "./data/";
$str_json = file_get_contents('php://input');
$uid=$_GET['q'];

date_default_timezone_set("America/Vancouver");
$date = date("Y-m-j-G-i-s");


$fp = fopen($dir.$uid."_vis_literacy"."_".$date.".txt", 'w');
fwrite($fp, $uid.",".$date.",".$str_json.";\n");
fclose($fp);

$fp = fopen($dir."vis_literacy_all.txt", 'a');
fwrite($fp, $uid.",".$date.",".$str_json.";\n");
fclose($fp);
?>