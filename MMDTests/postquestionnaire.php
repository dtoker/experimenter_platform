<?php
/*
Metroquest Study - Post-questionnaire
Sébastien Lallé
2014/11/29
*/

if(isset($_POST['submitted'])){
	if(isset($_POST['uid']) && isset($_POST['conficence']) && isset($_POST['satisfaction']) && isset($_POST['userfull_informed']) && isset($_POST['useful_decision']) &&
		isset($_POST['useful_informed_chart']) && isset($_POST['useful_decision_chart']) && isset($_POST['useful_informed_map']) && isset($_POST['useful_decision_map']) &&
		isset($_POST['useful_compare']) && isset($_POST['useful_progress']) && isset($_POST['easy_interface']) && 
		isset($_POST['easy_priorities']) && isset($_POST['easy_rate']) && isset($_POST['easy_comment']) &&
		isset($_POST['easy_chart']) && isset($_POST['easy_map']) && isset($_POST['easy_compare']) &&
		isset($_POST['noise_recall']) && isset($_POST['time_recall']) && isset($_POST['cost_recall']) && isset($_POST['pollution_recall']) && 
		isset($_POST['stops_recall']) && isset($_POST['access_recall']) && isset($_POST['wait_recall']) && isset($_POST['comments_recall']) 	){
		
		$dir = "./data/";
		date_default_timezone_set("America/Vancouver");
		$date = date("Y-m-j-G-i-s");
		$uid = intval(htmlspecialchars($_POST['uid']));
		
		$conficence = htmlspecialchars($_POST['conficence']);
		$satisfaction = htmlspecialchars($_POST['satisfaction']);
		$userfull_informed = htmlspecialchars($_POST['userfull_informed']);
		$useful_decision = htmlspecialchars($_POST['useful_decision']);
		$useful_informed_chart = htmlspecialchars($_POST['useful_informed_chart']);
		$useful_decision_chart = htmlspecialchars($_POST['useful_decision_chart']);
		$useful_informed_map = htmlspecialchars($_POST['useful_informed_map']);
		$useful_decision_map = htmlspecialchars($_POST['useful_decision_map']);
		$useful_compare = htmlspecialchars($_POST['useful_compare']);
		$useful_progress = htmlspecialchars($_POST['useful_progress']);
		$easy_interface = htmlspecialchars($_POST['easy_interface']);
		$easy_priorities = htmlspecialchars($_POST['easy_priorities']);
		$easy_rate = htmlspecialchars($_POST['easy_rate']);
		$easy_comment = htmlspecialchars($_POST['easy_comment']);
		$easy_chart = htmlspecialchars($_POST['easy_chart']);
		$easy_map = htmlspecialchars($_POST['easy_map']);
		$easy_compare = htmlspecialchars($_POST['easy_compare']);
		$comments_usability = htmlspecialchars($_POST['comments_usability']);
		
		$noise_recall = htmlspecialchars($_POST['noise_recall']);
		$time_recall = htmlspecialchars($_POST['time_recall']);
		$cost_recall = htmlspecialchars($_POST['cost_recall']);
		$pollution_recall = htmlspecialchars($_POST['pollution_recall']);
		$stops_recall = htmlspecialchars($_POST['stops_recall']);
		$access_recall = htmlspecialchars($_POST['access_recall']);
		$wait_recall = htmlspecialchars($_POST['wait_recall']);
		$comments_recall = htmlspecialchars($_POST['comments_recall']);

		$text_usability = $uid.",".$date.",".$conficence.",".$satisfaction.",".$userfull_informed.",".$useful_decision.",".$useful_informed_chart.",".$useful_decision_chart.",".
			$useful_informed_map.",".$useful_decision_map.",".$useful_compare.",".$useful_progress.",".$easy_interface.",".$easy_priorities.",".$easy_rate.",".$easy_comment.",".
			$easy_chart.",".$easy_map.",".$easy_compare.",".$comments_usability.";\n";
		$text_recall = $uid.",".$date.",".$noise_recall.",".$time_recall.",".$cost_recall.",".$pollution_recall.",".$stops_recall.",".$access_recall.",".$wait_recall.",".$comments_recall.";\n";
		
		$f = fopen($dir."Postquestionnaire_P".$uid."_".$date.".txt", "w");
		fwrite($f, $text_usability);
		fclose($f);

		$f = fopen($dir."Postquestionnaire_all.txt", "a");
		fwrite($f, $text_usability);
		fclose($f);
		
		$f = fopen($dir."Recall_P".$uid."_".$date.".txt", "w");
		fwrite($f, $text_recall);
		fclose($f);

		$f = fopen($dir."Recall_all.txt", "a");
		fwrite($f, $text_recall);
		fclose($f);

		
		print "Done";
		print "<hr />
		<table border='0' cellspacing='0' cellpadding='0'>
			<tr><td>Noise and Vibration :&nbsp;</td><td>".$noise_recall."</td></tr>
			<tr><td>Travel time savings :&nbsp;</td><td>".$time_recall."</td></tr>
			<tr><td>Cost :&nbsp;</td><td>".$cost_recall."</td></tr>
			<tr><td>Reduction in auto trip/Pollution :&nbsp;</td><td>".$pollution_recall."</td></tr>
			<tr><td>Frequency of stops :&nbsp;</td><td>".$stops_recall."</td></tr>
			<tr><td>Physicall accessibility :&nbsp;</td><td>".$access_recall."</td></tr>
			<tr><td>Wait time :&nbsp;</td><td>".$wait_recall."</td></tr>
		</tr></table>";
		
		exit;
	}else{
		$missing_fields = TRUE;
	}
}
?>

<html>
<head>
<title>Metroquest study postquestionnaire</title>
</head>

<body>
<h1>Post-questionnaire</h1>

<?php
if(isset($missing_fields)){
	print "<p style=\"color:red\"><strong>Some fields are missing.</strong></p>";
}
?>

<form id="preform" action="postquestionnaire.php" method="POST">
	<p>User ID: <input type='text' name='uid' size='3'></input><br /></p>
	<p></p>
    <div>
        <p>
            <h3><b>Please rate how strongly you agree or disagree with each of the following statements with respect to the interface you have used.</b></h3>
        </p>
    </div>
    <div>
		<table border="0" cellspacing="0" cellpadding="0"><tr><td>
        <p>I am confident in the ratings I made.<br />
            <input type='radio' name='conficence' value='1'>Strongly disagree<br />
            <input type='radio' name='conficence' value='2'>Disagree<br />
            <input type='radio' name='conficence' value='3'>Neutral<br />
            <input type='radio' name='conficence' value='4'>Agreee<br />
            <input type='radio' name='conficence' value='5'>Strongly agree
		</p>
		<p><br />I would like to use this interface for giving input on similar choices in the future.<br />
            <input type='radio' name='satisfaction' value='1' >Strongly disagree<br />
            <input type='radio' name='satisfaction' value='2'>Disagree<br />
            <input type='radio' name='satisfaction' value='3'>Neutral<br />
            <input type='radio' name='satisfaction' value='4'>Agreee<br />
            <input type='radio' name='satisfaction' value='5'>Strongly agree<br />
        </p>
		</td><td><img src="images/interface_sample.png" style="margin-left:100px" /></td></tr>
		</table>
		<hr />
		<p><br />I found this interface to be useful for learning about the three transit scenarios.<br />
            <input type='radio' name='userfull_informed' value='1' >Strongly disagree<br />
            <input type='radio' name='userfull_informed' value='2'>Disagree<br />
            <input type='radio' name='userfull_informed' value='3'>Neutral<br />
            <input type='radio' name='userfull_informed' value='4'>Agreee<br />
            <input type='radio' name='userfull_informed' value='5'>Strongly agree<br />
        </p>
		<p><br />I found this interface to be useful for rating the three transit scenarios.<br />
            <input type='radio' name='useful_decision' value='1' >Strongly disagree<br />
            <input type='radio' name='useful_decision' value='2'>Disagree<br />
            <input type='radio' name='useful_decision' value='3'>Neutral<br />
            <input type='radio' name='useful_decision' value='4'>Agreee<br />
            <input type='radio' name='useful_decision' value='5'>Strongly agree<br />
        </p>
		<p style="margin-bottom:0px"><br />I found the <em>deviation chart</em> useful for learning about the three transit scenarios.<br /></p>
			<table border="0" cellspacing="0" cellpadding="0"><tr><td>
            <input type='radio' name='useful_informed_chart' value='1' >Strongly disagree<br />
            <input type='radio' name='useful_informed_chart' value='2'>Disagree<br />
            <input type='radio' name='useful_informed_chart' value='3'>Neutral<br />
            <input type='radio' name='useful_informed_chart' value='4'>Agreee<br />
            <input type='radio' name='useful_informed_chart' value='5'>Strongly agree<br />
			</td><td><img src="images/deviation_sample.png" style="margin-left:200px" /></td></tr>
			</table>
        </p>
		<p style="margin-bottom:0px"><br />I found the <em>deviation chart</em> useful for rating the three transit scenarios.<br /></p>
            <input type='radio' name='useful_decision_chart' value='1' >Strongly disagree<br />
            <input type='radio' name='useful_decision_chart' value='2'>Disagree<br />
            <input type='radio' name='useful_decision_chart' value='3'>Neutral<br />
            <input type='radio' name='useful_decision_chart' value='4'>Agreee<br />
            <input type='radio' name='useful_decision_chart' value='5'>Strongly agree<br />
        </p>
		<p style="margin-bottom:0px"><br />I found the <em>maps</em> useful for learning about the three transit scenarios.<br /></p>
			<table border="0" cellspacing="0" cellpadding="0"><tr><td>
            <input type='radio' name='useful_informed_map' value='1' >Strongly disagree<br />
            <input type='radio' name='useful_informed_map' value='2'>Disagree<br />
            <input type='radio' name='useful_informed_map' value='3'>Neutral<br />
            <input type='radio' name='useful_informed_map' value='4'>Agreee<br />
            <input type='radio' name='useful_informed_map' value='5'>Strongly agree<br />
			</td><td><img src="images/map_sample.png" style="margin-left:200px" /></td></tr>
			</table>
        </p>
		<p style="margin-bottom:0px"><br />I found the <em>maps</em> useful for rating the three transit scenarios.<br /></p>
            <input type='radio' name='useful_decision_map' value='1' >Strongly disagree<br />
            <input type='radio' name='useful_decision_map' value='2'>Disagree<br />
            <input type='radio' name='useful_decision_map' value='3'>Neutral<br />
            <input type='radio' name='useful_decision_map' value='4'>Agreee<br />
            <input type='radio' name='useful_decision_map' value='5'>Strongly agree<br />
        </p>
		<p><br />Between the <em>maps</em> and the <em>deviation chart</em>, which one was more useful? Choose one: <br />
            <input type='radio' name='useful_compare' value='chart'>Deviation chart<br />
            <input type='radio' name='useful_compare' value='map' >Map<br />
            <input type='radio' name='useful_compare' value='same'>Same<br />
        </p>
		<p><br />I found the <em>progress bar</em> useful.<br />
			<table border="0" cellspacing="0" cellpadding="0"><tr><td>
            <input type='radio' name='useful_progress' value='1' >Strongly disagree<br />
            <input type='radio' name='useful_progress' value='2'>Disagree<br />
            <input type='radio' name='useful_progress' value='3'>Neutral<br />
            <input type='radio' name='useful_progress' value='4'>Agreee<br />
            <input type='radio' name='useful_progress' value='5'>Strongly agree<br />
			</td><td><img src="images/progress_bar_sample.png" style="margin-left:200px" /></td></tr>
			</table>
        </p>
		<hr />
		<p><br />I found this interface easy to use.<br />
            <input type='radio' name='easy_interface' value='1' >Strongly disagree<br />
            <input type='radio' name='easy_interface' value='2'>Disagree<br />
            <input type='radio' name='easy_interface' value='3'>Neutral<br />
            <input type='radio' name='easy_interface' value='4'>Agreee<br />
            <input type='radio' name='easy_interface' value='5'>Strongly agree<br />
        </p>
		<p><br />I found it easy to rank my <em>priorities</em>.<br />
			<table border="0" cellspacing="0" cellpadding="0"><tr><td>
            <input type='radio' name='easy_priorities' value='1' >Strongly disagree<br />
            <input type='radio' name='easy_priorities' value='2'>Disagree<br />
            <input type='radio' name='easy_priorities' value='3'>Neutral<br />
            <input type='radio' name='easy_priorities' value='4'>Agreee<br />
            <input type='radio' name='easy_priorities' value='5'>Strongly agree<br />
			</td><td><img src="images/priorities_sample.png" style="margin-left:200px" /></td></tr>
			</table>
        </p>
		<p><br />I found it easy to <em>rate</em> the three scenarios.<br />
			<table border="0" cellspacing="0" cellpadding="0"><tr><td>
            <input type='radio' name='easy_rate' value='1' >Strongly disagree<br />
            <input type='radio' name='easy_rate' value='2'>Disagree<br />
            <input type='radio' name='easy_rate' value='3'>Neutral<br />
            <input type='radio' name='easy_rate' value='4'>Agreee<br />
            <input type='radio' name='easy_rate' value='5'>Strongly agree<br />
			</td><td><img src="images/rating_sample.png" style="margin-left:200px" /></td></tr>
			</table>
        </p>
		<p><br />I found it easy to add <em>comments</em>.<br />
			<table border="0" cellspacing="0" cellpadding="0"><tr><td>
            <input type='radio' name='easy_comment' value='1' >Strongly disagree<br />
            <input type='radio' name='easy_comment' value='2'>Disagree<br />
            <input type='radio' name='easy_comment' value='3'>Neutral<br />
            <input type='radio' name='easy_comment' value='4'>Agreee<br />
            <input type='radio' name='easy_comment' value='5'>Strongly agree<br />
			</td><td><img src="images/comment_sample.png" style="margin-left:200px" /></td></tr>
			</table>
        </p>
		<p><br />I found the <em>deviation chart</em> easy to understand.<br />
			<table border="0" cellspacing="0" cellpadding="0"><tr><td>
            <input type='radio' name='easy_chart' value='1' >Strongly disagree<br />
            <input type='radio' name='easy_chart' value='2'>Disagree<br />
            <input type='radio' name='easy_chart' value='3'>Neutral<br />
            <input type='radio' name='easy_chart' value='4'>Agreee<br />
            <input type='radio' name='easy_chart' value='5'>Strongly agree<br />
			</td><td><img src="images/deviation_sample.png" style="margin-left:200px" /></td></tr>
			</table>
        </p>
		<p><br />I found the <em>maps</em> easy to understand.<br />
			<table border="0" cellspacing="0" cellpadding="0"><tr><td>
            <input type='radio' name='easy_map' value='1' >Strongly disagree<br />
            <input type='radio' name='easy_map' value='2'>Disagree<br />
            <input type='radio' name='easy_map' value='3'>Neutral<br />
            <input type='radio' name='easy_map' value='4'>Agreee<br />
            <input type='radio' name='easy_map' value='5'>Strongly agree<br />
			</td><td><img src="images/map_sample.png" style="margin-left:200px" /></td></tr>
			</table>
        </p>
		<p><br />Between the <em>maps</em> and the <em>deviation chart</em>, which one was easier to use? Choose one: <br />
            <input type='radio' name='easy_compare' value='chart'>Deviation chart<br />
            <input type='radio' name='easy_compare' value='map' >Map<br />
            <input type='radio' name='easy_compare' value='same'>Same<br /><br />
        </p>
		<hr />
		<p><h3>Any additional comments about this interface?</h3>
			<textarea name='comments_usability' rows='10' cols='100'></textarea><br /><br />
        </p>
		
		<hr />
		<h3>Here is the list of factors involved in the study. Please for each factor, state if it was useful or not useful for your ratings, or if you don't remember.</h3>
		<table border="0" cellspacing="0" cellpadding="0">
			<tr><td>Noise and Vibration</td><td><input type='radio' name='noise_recall' value='useful'>Useful <input type='radio' name='noise_recall' value='not_useful' >Not useful <input type='radio' name='noise_recall' value='Dont_remember'>Don't remember</td></tr>
			<tr><td>Travel time savings</td><td><input type='radio' name='time_recall' value='useful'>Useful <input type='radio' name='time_recall' value='not_useful' >Not useful <input type='radio' name='time_recall' value='Dont_remember'>Don't remember</td></tr>
			<tr><td>Cost</td><td><input type='radio' name='cost_recall' value='useful'>Useful <input type='radio' name='cost_recall' value='not_useful' >Not useful <input type='radio' name='cost_recall' value='Dont_remember'>Don't remember</td></tr>
			<tr><td>Reduction in auto trip/Pollution</td><td><input type='radio' name='pollution_recall' value='useful'>Useful <input type='radio' name='pollution_recall' value='not_useful' >Not useful <input type='radio' name='pollution_recall' value='Dont_remember'>Don't remember</td></tr>
			<tr><td>Frequency of stops</td><td><input type='radio' name='stops_recall' value='useful'>Useful <input type='radio' name='stops_recall' value='not_useful' >Not useful <input type='radio' name='stops_recall' value='Dont_remember'>Don't remember</td></tr>
			<tr><td>Physicall accessibility</td><td><input type='radio' name='access_recall' value='useful'>Useful <input type='radio' name='access_recall' value='not_useful' >Not useful <input type='radio' name='access_recall' value='Dont_remember'>Don't remember</td></tr>
			<tr><td>Wait time</td><td><input type='radio' name='wait_recall' value='useful'>Useful <input type='radio' name='wait_recall' value='not_useful' >Not useful <input type='radio' name='wait_recall' value='Dont_remember'>Don't remember</td></tr>
		</tr></table>
		
		<p><h3>Any additional comments on the factors?</h3>
			<textarea name='comments_recall' rows='10' cols='100'></textarea><br /><br />
        </p>
        <p><br /><input type='submit' name="submitted" value="Submit" /></p>
    </div>
</form>
</body>
</html>