<head>
    <link rel="stylesheet" href="view.css">
</head>
    <?php
/*
MMD Study - VARK
Enamul Hoque
*/

$questions = array(
  "You are helping someone who wants to go to your airport, the center of town or railway station. You would:",
  "A website has a video showing how to make a special graph. There is a person speaking, some lists
and words describing what to do and some diagrams. You would learn most from:",
  "You are planning a vacation for a group. You want some feedback from them about the plan. You
would:",
  "You are going to cook something as a special treat. You would:",
  "A group of tourists want to learn about the parks or wildlife reserves in your area. You would:",
  "You are about to purchase a digital camera or mobile phone. Other than price, what would most
influence your decision?",
  "Remember a time when you learned how to do something new. Avoid choosing a physical skill, eg.
riding a bike. You learned best by:",
  "You have a problem with your heart. You would prefer that the doctor:",
  "You want to learn a new program, skill or game on a computer. You would:",
  "I like websites that have:",
  "Other than price, what would most influence your decision to buy a new non-fiction book?",
  "You are using a book, CD or website to learn how to take photos with your new digital camera. You
would like to have:",
  "Do you prefer a teacher or a presenter who uses:",
  "You have finished a competition or test and would like some feedback. You would like to have
feedback:",
  "You are going to choose food at a restaurant or cafe. You would:",
  "You have to make an important speech at a conference or special occasion. You would:");

$answers = array
(
  array("go with her.","tell her the directions.","write down the directions.","draw, or show her a map, or give her a map."),
  array("seeing the diagrams.","listening.","reading the words.","watching the actions."),
  array("describe some of the highlights they will experience.","use a map to show them the places.","give them a copy of the printed itinerary","phone, text or email them."),
  array("cook something you know without the need for instructions.","ask friends for suggestions.","look on the Internet or in some cookbooks for ideas from the pictures.","use a good recipe."),
  array("talk about, or arrange a talk for them about parks or wildlife reserves.","show them maps and internet pictures.","take them to a park or wildlife reserve and walk with them.","give them a book or pamphlets about the parks or wildlife reserves"),
  array("Trying or testing it.","Reading the details or checking its features online.","It is a modern design and looks good.","The salesperson telling me about its features."),
  array("watching a demonstration.","listening to somebody explaining it and asking questions.","diagrams, maps, and charts - visual clues.","written instructions - e.g., a manual or book."),
  array("gave you a something to read to explain what was wrong.","used a plastic model to show what was wrong.","described what was wrong.","showed you a diagram of what was wrong."),
  array("read the written instructions that came with the program.","talk with people who know about the program.","use the controls or keyboard.","follow the diagrams in the book that came with it."),
  array("things I can click on, shift or try.","interesting design and visual features.","interesting written descriptions, lists and explanations.","audio channels where I can hear music, radio programs or interviews."),
  array("The way it looks is appealing.","Quickly reading parts of it.","A friend talks about it and recommends it.","A friend talks about it and recommends it."),
  array("a chance to ask questions and talk about the camera and its features.","clear written instructions with lists and bullet points about what to do.","diagrams showing the camera and what each part does.","many examples of good and poor photos and how to improve them."),
  array("demonstrations, models or practical sessions.","question and answer, talk, group discussion, or guest speakers.","handouts, books, or readings.","diagrams, charts or graphs."),
  array("using examples from what you have done.","using a written description of your results.","from somebody who talks it through with you.","using graphs showing what you had achieved."),
  array("choose something that you have had there before.","listen to the waiter or ask friends to recommend choices.","choose from the descriptions in the menu.","look at what others are eating or look at pictures of each dish."),
  array("make diagrams or get graphs to help explain things.","write a few key words and practice saying your speech over and over.","write out your speech and learn from reading it over several times.","gather many examples and stories to make the talk real and practical")
);

$scoring_chart = array
(
    array("K","A","R","V"),
    array("V","A","R","K"),
    array("K","V","R","A"),
    array("K","A","V","R"),
    array("A","V","K","R"),
    array("K","R","V","A"),
    array("K","A","V","R"),
    array("R","K","A","V"),
    array("R","A","K","V"),
    array("K","V","R","A"),
    array("V","R","A","K"),
    array("A","R","V","K"),
    array("K","A","R","V"),
    array("K","R","A","V"),
    array("K","A","R","V"),
    array("V","A","R","K")
);


$missing_fields = FALSE;
$UID_missing = FALSE;
$missing_q = "";
				
if(isset($_POST['submitted'])){
	$nb_q = count($questions);
	$test_results = array();
	for($i=0; $i<$nb_q; $i++){

      if(!empty($_POST['Q'.$i])) {
        print $_POST['Q'.$i]."</br></br></br>";
        $checkboxValues = "";
        foreach($_POST['Q'.$i] as $check) {
            print $check."</br>";
          $checkboxValues .= htmlspecialchars($check)."";
        }
        $test_results[] = $checkboxValues;
      }
/*
		if(isset($_POST['Q'.$i])){
			$test_results[] = intval(htmlspecialchars($_POST['Q'.$i]));
		}*/
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
			#print "answers:".",".$test_results[$i]."</br>";
		}

		//compute the score
//		$score = 0;
//		for($i=0; $i<$nb_q; $i++){
//			$score += $test_results[$i];
//		}
		
		$f = fopen($dir."VARK_P".$uid."_".$date.".txt", "w");
		//fwrite($f, $uid.",".$score.",".$answers.";\n");
        fwrite($f, $uid.",".$answers.";\n");
		fclose($f);

		$f = fopen($dir."VARK_all.txt", "a");
		//fwrite($f, $uid.",".$date.",".$score.",".$answers.";\n");
        fwrite($f, $uid.",".$answers.";\n");
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

<form id="testform" class="appnitro" action="VARK.php<?php if(isset($_GET['uid'])) print "?uid=".addslashes(htmlentities($_GET['uid']));  ?>" method="POST">
    <ul id = 'questionList'>
    <div>
		<p>User ID: <input type='text' name='uid' size='3'  value="<?php if(isset($_GET['uid'])) print addslashes(htmlentities($_GET['uid']));  ?>"></input><br /></p>
        <p>
            <h3><b>Choose the answer which best explains your preference and click the box next to it. Please click more than one if a single answer does not match your perception. Leave blank any question that does not apply.</b></h3>
        </p>
    </div>
    <div>
<?php
	for($i=0; $i<count($questions); $i++){
		print "<li>"." <label class=\"description\">".($i+1).". ".$questions[$i]."</label>";
		print "<span>";
		for($j=0; $j<=3; $j++){
			$checked = isset($_POST['Q'.$i]) && $_POST['Q'.$i] == ($j+1) ? "checked" : "";
			print "<input type='checkbox' class='element checkbox' name='Q".$i."[]' value='".($scoring_chart[$i][$j])."' ".$checked.">"."<label class=\"choice\">".$answers[$i][$j]."</label></input>";
		}
        print "</span>";
		print "</li>";
	}
?>

        <p><br /><input type='submit' name="submitted" value="Submit" /><br /></p>
    </div>
    </ul>
</form>
</body>
</html>