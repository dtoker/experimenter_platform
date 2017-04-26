<?php
/*
Metroquest Study - Pupil calibration
Sébastien Lallé
2014/11/29
*/
if(!empty($_GET['start']) && !empty($_GET['end'])){
		
	$dir = "./data/";
	date_default_timezone_set("America/Vancouver");
	$date = date("Y-m-j-G-i-s");
	$uid = intval(addslashes(htmlentities($_GET['uid'])));
	$start = intval(addslashes(htmlentities($_GET['start'])));
	$end = intval(addslashes(htmlentities($_GET['end'])));
	
	$f = fopen($dir."PupilSize_P".$uid."_".$date.".txt", "w");
	fwrite($f, $uid.",".$start.",".$end."\n");
	fclose($f);

	$f = fopen($dir."PupilSize_all.txt", "a") ;
	fwrite($f, $uid.",".$date.",".$start.",".$end."\n");
	fclose($f);

		
	print "Done";
	exit;
}
?>

<html>
<head>
<title>Metroquest study prequestionnaire</title>
<script src="//code.jquery.com/jquery-1.10.2.js"></script>
</head>

<body>
<div><img src="images/blank_cross.jpg" /></div>

<script>
var start_time = 0;
var end_time = 0;
var uid = <?php echo $_GET['uid'] ?>;
$( "html" ).click(function() {
	if(start_time == 0)
		start_time = new Date().getTime();
	else if(end_time == 0){
		end_time = new Date().getTime();
		window.location.replace("?uid="+uid+"&start="+start_time+"&end="+end_time);
	}	
});
</script>

</body>
</html>