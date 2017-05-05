<?php
if(isset($_POST['max_words']) && isset($_POST['max_words']) && isset($_POST['max_length']) && isset($_POST['score_maths']) && isset($_POST['score_word'])  && isset($_POST['longest_sequence_correct']) && isset($_POST['partial_span_score_word']) && isset($_POST['avg_time_maths'])){
	
	$dir = "./data/";
	date_default_timezone_set("America/Vancouver");
	$date = date("Y-m-j-G-i-s");
	$uid = htmlspecialchars($_POST['uid']);
	$max_words = htmlspecialchars($_POST['max_words']);
	$max_length = htmlspecialchars($_POST['max_length']);
	$score_maths = htmlspecialchars($_POST['score_maths']);
	$score_word = htmlspecialchars($_POST['score_word']);
	$longest_sequence_correct = htmlspecialchars($_POST['longest_sequence_correct']);
	$partial_span_score_word = htmlspecialchars($_POST['partial_span_score_word']);
	$avg_time_maths= htmlspecialchars($_POST['avg_time_maths']);
	
	$f = fopen($dir."OSPAN_P".$uid."_".$date.".txt", "w");
	fwrite($f, $uid.",".$max_words.",".$max_length.",".$score_maths.",".$score_word.",".$longest_sequence_correct.",".$partial_span_score_word.",".$avg_time_maths.";\n");
	fclose($f);

	$f = fopen($dir."OSPAN_all.txt", "a");
	fwrite($f, $uid.",".$date.",".$max_words.",".$max_length.",".$score_maths.",".$score_word.",".$longest_sequence_correct.",".$partial_span_score_word.",".$avg_time_maths.";\n");
	fclose($f);
	
	print "Done";
}
?>