<?php
/*
MMD Study - VARK
Enamul Hoque
*/

$questions = array("You have to make an important speech at a conference or special occasion. You would:",
				"Do you prefer a teacher or a presenter who uses:",
				"You want to learn a new program, skill or game on a computer. You would:",
				"I like websites that have:",
				"A group of tourists wants to learn about the parks or wildlife reserves in your area. You would:",
				"Remember a time when you learned how to do something new. Avoid choosing a physical skill, eg. riding a bike. You learned best by:",
				"You are helping someone who wants to go to your airport, the center of town or railway station. You would:",
				"You are using a book, CD or website to learn how to take photos with your new digital camera. You would like to have:",
				"You are planning a vacation for a group. You want some feedback from them about the plan. You would:",
				"You are going to choose food at a restaurant or cafe. You would:",
				"You are about to purchase a digital camera or mobile phone. Other than price, what would most influence your decision?",
				"You are going to cook something as a special treat. You would:",
				"A website has a video showing how to make a special graph. There is a person speaking, some lists and words describing what to do and some diagrams. You would learn most from:",
				"Other than price, what would most influence your decision to buy a new non-fiction book?",
				"You have finished a competition or test and would like some feedback. You would like to have feedback:",
				"You have a problem with your heart. You would prefer that the doctor:");

$answers = array
			(
			array("write out your speech and learn from reading it over several times.", "make diagrams or get graphs to help explain things.", "write a few key words and practice saying your speech over and over.", "gather many examples and stories to make the talk real and practical."),
			array("question and answer, talk, group discussion, or guest speakers.", "handouts, books, or readings.", "demonstrations, models or practical sessions.", "diagrams, charts or graphs."),				
			array("read the written instructions that came with the program.", "use the controls or keyboard.", "follow the diagrams in the book that came with it.", "talk with people who know about the program."),			
			array("things I can click on, shift or try.", "audio channels where I can hear music, radio programs or interviews.", "interesting design and visual features.", "interesting written descriptions, lists and explanations."),			
			array("take them to a park or wildlife reserve and walk with them.", "give them a book or pamphlets about the parks or wildlife reserves.", "show them maps and internet pictures.", "talk about, or arrange a talk for them about parks or wildlife reserves."),			
			array("written instructions – e.g. a manual or book.", "diagrams, maps, and charts - visual clues.", "watching a demonstration.", "listening to somebody explaining it and asking questions."),			
			array("tell her the directions.", "draw, or show her a map, or give her a map.", "go with her.", "write down the directions."),
			array("clear written instructions with lists and bullet points about what to do.", "a chance to ask questions and talk about the camera and its features.", "many examples of good and poor photos and how to improve them.", "diagrams showing the camera and what each part does."),
			array("use a map to show them the places.", "phone, text or email them.", "give them a copy of the printed itinerary.", "describe some of the highlights they will experience."),
			array("choose from the descriptions in the menu.", "look at what others are eating or look at pictures of each dish.", "choose something that you have had there before.", "listen to the waiter or ask friends to recommend choices."),	
			array("It is a modern design and looks good.", "The salesperson telling me about its features.", "Trying or testing it.", "Reading the details or checking its features online."),				
			array("ask friends for suggestions.", "use a cookbook where you know there is a good recipe.", "look on the Internet or in some cookbooks for ideas from the pictures.", "cook something you know without the need for instructions."),				
			array("listening.", "watching the actions.", "reading the words.", "seeing the diagrams."),				
			array("Quickly reading parts of it.", "It has real-life stories, experiences and examples.", "The way it looks is appealing.", "A friend talks about it and recommends it."),				
			array("using examples from what you have done.", "using a written description of your results.", "using graphs showing what you had achieved.", "from somebody who talks it through with you."),
			array("showed you a diagram of what was wrong.", "gave you something to read to explain what was wrong.", "described what was wrong.", "used a plastic model to show what was wrong.")
			);

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
		
		$f = fopen($dir."VARK_P".$uid."_".$date.".txt", "w");
		fwrite($f, $uid.",".$score.",".$answers.";\n");
		fclose($f);

		$f = fopen($dir."VARK_all.txt", "a");
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

<form id="testform" action="VARK.php<?php if(isset($_GET['uid'])) print "?uid=".addslashes(htmlentities($_GET['uid']));  ?>" method="POST">
    <div>
		<p>User ID: <input type='text' name='uid' size='3'  value="<?php if(isset($_GET['uid'])) print addslashes(htmlentities($_GET['uid']));  ?>"></input><br /></p>
        <p>
            <h3><b>Choose the answer which best explains your preference and click the box next to it. Please click more than one if a single answer does not match your perception. Leave blank any question that does not apply.</b></h3>
        </p>
    </div>
    <div>
<?php
	for($i=0; $i<count($questions); $i++){
		print "<p>".($i+1).". ".$questions[$i]."<br />";
		
		for($j=0; $j<=3; $j++){
			$checked = isset($_POST['Q'.$i]) && $_POST['Q'.$i] == ($j-2) ? "checked" : "";
			print "<input type='checkbox' name='Q".$i."' value='".($j-2)."' ".$checked.">".$answers[$i][$j]."</input><br />";
		}
		print "</p>";
	}
?>

        <p><br /><input type='submit' name="submitted" value="Submit" /><br /></p>
    </div>
</form>
</body>
</html>