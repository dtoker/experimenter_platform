<?php
/*
Metroquest Study - Pre-questionnaire
Sébastien Lallé
2014/11/29
*/
if(isset($_POST['submitted'])){
	if(isset($_POST['uid']) && isset($_POST['freq_pref_choice']) && isset($_POST['freq_vis_choice'])){
		
		$dir = "./data/";
		date_default_timezone_set("America/Vancouver");
		$date = date("Y-m-j-G-i-s");
		$uid = intval(htmlspecialchars($_POST['uid']));
		$freq_pref_choice = htmlspecialchars($_POST['freq_pref_choice']);
		$freq_vis_choice = htmlspecialchars($_POST['freq_vis_choice']);
		
		//create users
		$f = fopen($dir."Prequestionnaire_P".$uid."_".$date.".txt", "w");
		fwrite($f, $uid.",".$freq_pref_choice.",".$freq_vis_choice."\n");
		fclose($f);

		$f = fopen($dir."Prequestionnaire_all.txt", "a");
		fwrite($f, $uid.",".$date.",".$freq_pref_choice.",".$freq_vis_choice."\n");
		fclose($f);
		
		print "<html><head><meta http-equiv=\"refresh\" content=\"0; url=pupil_calibration.php?uid=".$uid."\" /></head><body></body></html>";
		exit;
	}else{
		$missing_fields = TRUE;
	}
}
?>

<html>
<head>
<title>Metroquest study prequestionnaire</title>
</head>

<body>
<h1>Pre-questionnaire</h1>

<?php
if(isset($missing_fields)){
	print "<p style=\"color:red\"><strong>Some fields are missing.</strong></p>";
}
?>

<form id="preform" action="prequestionnaire.php" method="POST">
    <div>
        <p>
            <h3><b>Please answer each of the following questions.</b></h3>
        </p>
    </div>
    <div>
        <p>User ID: <input type='text' name='uid' size='3'></input></p>
        <p>How often do you need to make preferential choice (e.g., buying a car or a cellphone, choosing a university, etc)?<br />
            <input type='radio' name='freq_pref_choice' value='never'>Never<br />
            <input type='radio' name='freq_pref_choice' value='rarely'>Rarely (few times a year)<br />
            <input type='radio' name='freq_pref_choice' value='occasionally'>Occasionally (several times a year)<br />
            <input type='radio' name='freq_pref_choice' value='frequently'>Frequently (several times a month)<br />
            <input type='radio' name='freq_pref_choice' value='very frequently'>Very frequently (several times a week)
		</p>
        <p>How often do you use visualization tool to make such preferential choice?  <br />
            <input type='radio' name='freq_vis_choice' value='never'>Never<br />
            <input type='radio' name='freq_vis_choice' value='rarely'>Rarely (few times a year)<br />
            <input type='radio' name='freq_vis_choice' value='occasionally'>Occasionally (several times a year)<br />
            <input type='radio' name='freq_vis_choice' value='frequently'>Frequently (several times a month)<br />
            <input type='radio' name='freq_vis_choice' value='very frequently'>Very frequently (several times a week)
		</p>

        <p><br /><input type='submit' name="submitted" value="Submit" /></p>
    </div>
</form>
</body>
</html>