<head>
    <link rel="stylesheet" href="view.css">
</head>
<?php
/*
Metroquest Study - Needcognition
S�bastien Lall�
2014/11/29
*/

$questions = array("I would prefer complex to simple problems.", 
				"I like to have the responsibility of handling a situation that requires a lot of thinking.", 
				"Thinking is not my idea of fun.",
				"I would rather do something that requires little thought than something that is sure to challenge my thinking abilities.", 
				"I try to anticipate and avoid situations where there is likely a chance I will have to think in depth about something.",
				"I find satisfaction in deliberating hard and for long hours.", 
				"I only think as hard as I have to.", 
				"I prefer to think about small, daily projects to long-term ones.",
				"I like tasks that require little thought once I�ve learned them.", 
				"The idea of relying on thought to make my way to the top appeals to me.",
				"I really enjoy a task that involves coming up with new solutions to problems.", 
				"Learning new ways to think doesn�t excite me very much.",
				"I prefer my life to be filled with puzzles that I must solve.", 
				"The notion of thinking abstractly is appealing to me.", 
				"I would prefer a task that is intellectual, difficult, and important to one that is somewhat important but does not require much thought.",
				"I feel relief rather than satisfaction after completing a task that required a lot of mental effort.",
				"It�s enough for me that something gets the job done; I don�t care how or why it works.",
				"I usually end up deliberating about issues even when they do not affect me personally.");

$answers = array("extremely uncharacteristic", "somewhat uncharacteristic", " uncertain", " somewhat characteristic", " extremely characteristic");

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
		
		$f = fopen($dir."NeedCognition_P".$uid."_".$date.".txt", "w");
		fwrite($f, $uid.",".$score.",".$answers.";\n");
		fclose($f);

		$f = fopen($dir."NeedCognition_all.txt", "a");
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

<form id="testform" class="appnitro" action="NC.php<?php if(isset($_GET['uid'])) print "?uid=".addslashes(htmlentities($_GET['uid']));  ?>" method="POST">
    <input type="hidden" name="uid" value="<?php  if(isset($_GET['uid'])) echo addslashes(htmlentities($_GET['uid'])); ?>" />
    <ul id = 'questionList'>

    <div>
		<p>User ID: <label><b><?php if(isset($_GET['uid'])) {print addslashes(htmlentities($_GET['uid'])); $_POST['uid'] = (htmlentities($_GET['uid']));} ?></b></label><br /></p>
        <p>
            <h3><b>For each of the statements below, please indicate to what extent the statement is characteristic of you.</b></h3>
        </p>
    </div>
    <div>
<?php

	for($i=0; $i<count($questions); $i++){
      print "<li>"." <label class=\"description\">".($i+1).". ".$questions[$i]."</label>";
      print "<span>";

		for($j=0; $j<=4; $j++){
			$checked = isset($_POST['Q'.$i]) && $_POST['Q'.$i] == ($j-2) ? "checked" : "";
			print "<input type='radio' class='element radio' name='Q".$i."' value='".($j-2)."' ".$checked.">"."<label class=\"choice\">".$answers[$j]."</label></input>";
		}
      print "</span>";
      print "</li>";
	}
?>

        <p><br /><input type='submit' name="submitted" value="Submit" /><br /></p>
    </div>
</form>
</body>
</html>