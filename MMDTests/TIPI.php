<?php
/*
Metroquest Study - Needcognition
S�bastien Lall�
2014/11/29
*/

$questions = array(" _____ Extraverted, enthusiastic.",
				"_____ Critical, quarrelsome.",
				"_____ Dependable, self-disciplined.",
				"_____ Anxious, easily upset.",
				"_____ Open to new experiences, complex.",
				"_____ Reserved, quiet.",
				"_____ Sympathetic, warm.",
				"_____ Disorganized, careless.",
				"_____ Calm, emotionally stable.",
				" _____ Conventional, uncreative.");

$answers = array("Disagree strongly", "Disagree moderately", " Disagree a little", " Neither agree nor disagree", " Agree a little", " Agree moderately", " Agree strongly");

$missing_fields = FALSE;
$UID_missing = FALSE;
$missing_q = "";
				
if(isset($_POST['submitted'])){
	$nb_q = count($questions);
	$test_results = array();
	for($i=0; $i<$nb_q; $i++){
		if(isset($_POST['Q'.$i])){
			$test_results[] = intval(htmlspecialchars($_POST['Q'.$i]));
		}
		else{
			$missing_fields = TRUE;
			$missing_q = $missing_q == "" ? ($i+1) : $missing_q.", ".($i+1);
		}
	}
	if(empty($_POST['uid'])){
		$UID_missing = TRUE;
	}
	if(!$missing_fields && isset($_POST['uid'])){
	
		$dir = "./data/";
		date_default_timezone_set("America/Vancouver");
		$date = date("Y-m-j-G-i-s");
		$uid = intval(htmlspecialchars($_POST['uid']));
		
		//store answers
		$answers = $test_results[0];
		for($i=1; $i<$nb_q; $i++){
			$answers .= ",".$test_results[$i];
		}

		//compute the score
		$score = 0;
		for($i=0; $i<$nb_q; $i++){
			$score += $test_results[$i];
		}
		
		$f = fopen($dir."TIPI_P".$uid."_".$date.".txt", "w");
		fwrite($f, $uid.",".$score.",".$answers.";\n");
		fclose($f);

		$f = fopen($dir."TIPI_all.txt", "a");
		fwrite($f, $uid.",".$date.",".$score.",".$answers.";\n");
		fclose($f);
		
		print "Done";
		exit;
	}
}

?>

<html>
<head>
<title>Metroquest study test NC</title>
</head>

<body>

<?php
if($missing_fields){
	print "<p style=\"color:red\"><strong>The following questions are missing : ".$missing_q."</strong></p>";
	$missing_fields = FALSE;
	$missing_q = "";
}
if($UID_missing){
	print "<p style=\"color:red\"><strong>Please enter your user ID (participant number).</strong></p>";
	$UID_missing = FALSE;
}
?>

<form id="testform" action="TIPI.php<?php if(isset($_GET['uid'])) print "?uid=".addslashes(htmlentities($_GET['uid']));  ?>" method="POST">
    <div>
		<p>User ID: <input type='text' name='uid' size='3'  value="<?php if(isset($_GET['uid'])) print addslashes(htmlentities($_GET['uid']));  ?>"></input><br /></p>
        <p>
            <h3><b>For each of the statements below, please indicate to what extent the statement is characteristic of you.</b></h3>
        </p>
    </div>
    <div>
<?php
	print "<p>I see myself as:</p>";
	for($i=0; $i<count($questions); $i++){
		print "<p>".($i+1).". ".$questions[$i]."<br />";
		
		for($j=0; $j<=6; $j++){
			$checked = isset($_POST['Q'.$i]) && $_POST['Q'.$i] == ($j-2) ? "checked" : "";
			print "<input type='radio' name='Q".$i."' value='".($j-2)."' ".$checked.">".$answers[$j]."</input><br />";
		}
		print "</p>";
	}
?>

        <p><br /><input type='submit' name="submitted" value="Submit" /><br /></p>
    </div>
</form>
</body>
</html>