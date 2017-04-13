<?php
/*
Metroquest Study - locus
Sébastien Lallé
2014/11/29
*/
$missing_fields = FALSE;

if(isset($_POST['submitted'])){
	$nb_q = 29;
	$test_results = array();
	for($i=1; $i<=$nb_q; $i++){
		if(isset($_POST[$i])){
			$test_results[] = htmlspecialchars($_POST[$i]);
		}
		else{
			$missing_fields = TRUE;
			break;
		}
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
		$external_gold = array("",  "a",  "b",  "b",  "b",  "a",  "a",  "",  "a",  "b",  "b",  "b",  "b",  "",  "b",  "a",  "a",  "a",  "",  "a", "a",  "b",  "a",  "",  "a",  "b",  "",  "b",  "a");
		for($i=0; $i<$nb_q; $i++){
			$score += $external_gold[$i] == $test_results[$i] ? 1 : 0;
		}
		
		$f = fopen($dir."Locus_P".$uid."_".$date.".txt", "w");
		fwrite($f, $uid.",".$score.",".$answers.";\n");
		fclose($f);

		$f = fopen($dir."Locus_all.txt", "a");
		fwrite($f, $uid.",".$date.",".$score.",".$answers.";\n");
		fclose($f);
		
		print "Done";
		exit;
	}
}
?>

<html>
<head>
<title>Metroquest study test LC</title>
</head>

<body>

<?php
if($missing_fields){
	print "<p style=\"color:red\"><strong>Some fields are missing.</strong></p>";
	$missing_fields = FALSE;
}
?>

<form id="testform" action="LC.php<?php if(isset($_GET['uid'])) print "?uid=".addslashes(htmlentities($_GET['uid']));  ?>" method="POST">
    <div>
		<p>User ID: <input type='text' name='uid' size='3'  value="<?php if(isset($_GET['uid'])) print addslashes(htmlentities($_GET['uid'])); ?>"></input><br /></p>
        <p>
            <h3><b>Please select the statement for each question that best describes how you feel.</b></h3>
        </p>
    </div>
    <div>
        1.<p><input type='radio' name='1' value='a'>Children get into trouble because their parents punish them too much.</input><br /></p>
        <p><input type='radio' name='1' value='b'>The trouble with most children nowadays is that their parents are too easy with them.</input><br /></p><br />
        2. <p><input type='radio' name='2' value='a'>Many of the unhappy things in people's lives are partly due to bad luck.</input><br /></p>
         <p><input type='radio' name='2' value='b'>People's misfortunes result from the mistakes they make.</input><br /></p><br />
        3. <p><input type='radio' name='3' value='a'>One of the major reasons why we have wars is because people don't take enough interest in politics.</input><br /></p>
         <p><input type='radio' name='3' value='b'>There will always be wars, no matter how hard people try to prevent them.</input><br /></p><br />
        4. <p><input type='radio' name='4' value='a'>In the long run people get the respect they deserve in this world.</input><br /></p>
        <p><input type='radio' name='4' value='b'>Unfortunately, an individual's worth often passes unrecognized no matter how hard he tries.</input><br /></p><br />
        5. <p><input type='radio' name='5' value='a'>The idea that teachers are unfair to students is nonsense.</input><br /></p>
        <p><input type='radio' name='5' value='b'>Most students don't realize the extent to which their grades are influenced by accidental happenings.</input><br /></p><br />
        6. <p><input type='radio' name='6' value='a'>Without the right breaks one cannot be an effective leader.</input><br /></p>
        <p><input type='radio' name='6' value='b'>Capable people who fail to become leaders have not taken advantage of their opportunities.</input><br /></p><br />
        7. <p><input type='radio' name='7' value='a'>No matter how hard you try some people just don't like you.</input><br /></p>
        <p><input type='radio' name='7' value='b'>People who can't get others to like them don't understand how to get along with others.</input><br /></p><br />
        8. <p><input type='radio' name='8' value='a'>Heredity plays the major role in determining one's personality.</input><br /></p>
        <p><input type='radio' name='8' value='b'>It is one's experiences in life which determine what they're like.</input><br /></p><br />
        9. <p><input type='radio' name='9' value='a'>I have often found that what is going to happen will happen.</input><br /></p>
        <p><input type='radio' name='9' value='b'>Trusting to fate has never turned out as well for me as making a decision to take a definite course of action.</input><br /></p><br />
        10. <p><input type='radio' name='10' value='a'>In the case of the well prepared student there is rarely if ever such a thing as an unfair test.</input><br /></p>
        <p><input type='radio' name='10' value='b'>Many times exam questions tend to be so unrelated to course work that studying in really useless.</input><br /></p><br />
        11. <p><input type='radio' name='11' value='a'>Becoming a success is a matter of hard work, luck has little or nothing to do with it.</input><br /></p>
        <p><input type='radio' name='11' value='b'>Getting a good job depends mainly on being in the right place at the right time.</input><br /></p><br />
        12. <p><input type='radio' name='12' value='a'>The average citizen can have an influence in government decisions.</input><br /></p>
        <p><input type='radio' name='12' value='b'>This world is run by the few people in power, and there is not much the little guy can do about it.</input><br /></p><br />
        13. <p><input type='radio' name='13' value='a'>When I make plans, I am almost certain that I can make them work.</input><br /></p>
        <p><input type='radio' name='13' value='b'>It is not always wise to plan too far ahead because many things turn out to be a matter of good or bad fortune anyhow.</input><br /></p><br />
        14. <p><input type='radio' name='14' value='a'>There are certain people who are just no good.</input><br /></p>
        <p><input type='radio' name='14' value='b'>There is some good in everybody.</input><br /></p><br />
        15. <p><input type='radio' name='15' value='a'>In my case getting what I want has little or nothing to do with luck.</input><br /></p>
        <p><input type='radio' name='15' value='b'>Many times we might just as well decide what to do by flipping a coin.</input><br /></p><br />
        16. <p><input type='radio' name='16' value='a'>Who gets to be the boss often depends on who was lucky enough to be in the right place first.</input><br /></p>
        <p><input type='radio' name='16' value='b'>Getting people to do the right thing depends upon ability, luck has little or nothing to do with it.</input><br /></p><br />
        17. <p><input type='radio' name='17' value='a'>As far as world affairs are concerned, most of us are the victims of forces we can neither understand, nor control.</input><br /></p>
        <p><input type='radio' name='17' value='b'>By taking an active part in political and social affairs the people can control world events.</input><br /></p><br />
        18. <p><input type='radio' name='18' value='a'>Most people don't realize the extent to which their lives are controlled by accidental happenings.</input><br /></p>
        <p><input type='radio' name='18' value='b'>There really is no such thing as "luck."</input><br /></p><br />
        19. <p><input type='radio' name='19' value='a'>One should always be willing to admit mistakes.</input><br /></p>
        <p><input type='radio' name='19' value='b'>It is usually best to cover up one's mistakes.</input><br /></p><br />
        20. <p><input type='radio' name='20' value='a'>It is hard to know whether or not a person really likes you.</input><br /></p>
        <p><input type='radio' name='20' value='b'>How many friends you have depends upon how nice a person you are.</input><br /></p><br />
        21. <p><input type='radio' name='21' value='a'>In the long run the bad things that happen to us are balanced by the good ones.</input><br /></p>
        <p><input type='radio' name='21' value='b'>Most misfortunes are the result of lack of ability, ignorance, laziness, or all three.</input><br /></p><br />
        22. <p><input type='radio' name='22' value='a'>With enough effort we can wipe out political corruption.</input><br /></p>
        <p><input type='radio' name='22' value='b'>It is difficult for people to have much control over the things politicians do in office.</input><br /></p><br />
        23. <p><input type='radio' name='23' value='a'>Sometimes I can't understand how teachers arrive at the grades they give.</input><br /></p>
        <p><input type='radio' name='23' value='b'>There is a direct connection between how hard 1 study and the grades I get.</input><br /></p><br />
        24. <p><input type='radio' name='24' value='a'>A good leader expects people to decide for themselves what they should do.</input><br /></p>
        <p><input type='radio' name='24' value='b'>A good leader makes it clear to everybody what their jobs are.</input><br /></p><br />
        25. <p><input type='radio' name='25' value='a'>Many times I feel that I have little influence over the things that happen to me.</input><br /></p>
        <p><input type='radio' name='25' value='b'>It is impossible for me to believe that chance or luck plays an important role in my life.</input><br /></p><br />
        26. <p><input type='radio' name='26' value='a'>People are lonely because they don't try to be friendly.</input><br /></p>
        <p><input type='radio' name='26' value='b'>There's not much use in trying too hard to please people, if they like you, they like you.</input><br /></p><br />
        27. <p><input type='radio' name='27' value='a'>There is too much emphasis on athletics in high school.</input><br /></p>
        <p><input type='radio' name='27' value='b'>Team sports are an excellent way to build character.</input><br /></p><br />
        28. <p><input type='radio' name='28' value='a'>What happens to me is my own doing.</input><br /></p>
        <p><input type='radio' name='28' value='b'>Sometimes I feel that I don't have enough control over the direction my life is taking.</input><br /></p><br />
        29. <p><input type='radio' name='29' value='a'>Most of the time I can't understand why politicians behave the way they do.</input><br /></p>
        <p><input type='radio' name='29' value='b'>In the long run the people are responsible for bad government on a national as well as on a local level.</input></p>
        <p><br /><input type='submit' name="submitted" value="Submit" /></p>
    </div>
</form>
</body>
</html>