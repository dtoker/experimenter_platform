<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Metroquest study test OP</title>

<style type="text/css">
body
{
	text-align: center;
	margin-top: 100px;
	font-size: 1.1em
} 

#instruction{
	margin-top: -80px;
}

#word_block{
  -ms-user-select:none;
  -moz-user-select: none;
  -webkit-user-select: none;
} 
</style>
<script src="jquery.js"></script>

<script type="text/javascript">
var MAX_WORDS = 60; //should be coherent with the number of REPETITION_SEQUENCE and MIN/MAX_LENGTH_SEQUENCE
var MAX_SEQUENCE = 15; //same
var REPETITION_SEQUENCE = 3;
var MIN_LENGTH_SEQUENCE = 2;
var MAX_LENGTH_SEQUENCE = 6;
var MAX_MUST_BE_VIEWED = true;
var DURATION_WORD_DISPLAYED_MS = 1000;

var nb_sequence_viewed = 0;
var nb_words_viewed = 0;
var length_sequence;
var current_iter = 0;
var current_maths_correctness = -1;
var practice = true;

var list_words = ["above", "after", "again", "air", "along", "also", "always", "any", "around", "away", "back", "bad", "before", "behind", "below", "big", "bike", "both", "bus", "bring", "bye", "came", "car", "close", "come", "cook", "cross", "day", "during", "eat", "end", "even", "every", "few", "find", "fire", "food", "form", "friend", "future", "get", "give", "good", "great", "hear", "help", "here", "home", "house", "keep", "know", "large", "last", "later", "left", "less", "like", "line", "look", "men", "might", "much", "must", "name", "near", "never", "new", "next", "nice", "number", "off", "old", "our", "own", "part", "past", "place", "put", "right", "same", "send", "set", "show", "sleep", "sooner", "sound", "speak", "still", "such", "table", "take", "tell", "think", "three", "too", "under", "until", "want", "week", "well", "went", "while", "why", "work", "women", "world", "write", "yet"]; //list of possible words in the study
var current_words = new Array()
var sequences_order = new Array()

var uid = "";
var score_maths = 0;
var score_word = 0;
var partial_span_score_word = 0;
var longest_sequence_viewed = 0;
var longest_sequence_correct = 0;
var avg_time_maths = 0;

var start_maths = 0;

//randomly generate an integer
function randint(min, max) {
  return Math.round(Math.random() * (max - min), 0) + min;
}

//check if needle is in the array haystack
function inArray(needle, haystack) {
    var length = haystack.length;
    for(var i = 0; i < length; i++) {
        if(haystack[i] == needle) return true;
    }
    return false;
}

//Randomize array element order in-place, using Fisher-Yates shuffle algorithm.
function shuffleArray(array) {
    for (var i = array.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        var temp = array[i];
        array[i] = array[j];
        array[j] = temp;
    }
    return array;
}

//generate a new words sequences
function generate_new_sequences(){
	if(practice){ //if practice, minimum length
		length_sequence = 2;
	}
	else{
		length_sequence = sequences_order[nb_sequence_viewed];
	}

	current_iter = 0;
	current_words = []
	if(!practice){
		nb_words_viewed += length_sequence;	
		nb_sequence_viewed++;
		
		if(longest_sequence_viewed < length_sequence){
			longest_sequence_viewed = length_sequence;
		}
	}
}	

//generate a new random equation, correct or incorrect
//Form: (nb1 [*/] nb2) [+-] nb3 = result   (all numbers are integer)
function generate_equation(){
	var eq = "";
	var nb1 = randint(0,7);
	var nb2 = randint(0,5);
	var nb3 = randint(1,7);
	var op1 = randint(0,1);
	var op2 = randint(0,1);
	var correctness = randint(0,1);
	var nbres = 0;
	var sign1 = "";
	var sign2 = "";
	
	if(op1 == 0){ //op1 = x
		nbres = nb1*nb2;
		sign1 = "x"
	}
	else{ // op1 = /
		if(nb2 == 0) //division by 0
			nb2+=randint(1,5);
		while(nb1%nb2 != 0) //the result of the division must be an integer
			nb1++;
		nbres = nb1/nb2
		sign1 = "/"
	}
		
	if(op2 == 0 || nbres < 2){ //op2 = +
		nbres += nb3;
		sign2 = "+";
	}
	else{ //op2 = -
		while(nbres<nb3) //result must be positive
			nb3--;
		nbres -= nb3;
		sign2 = "-";
	}
		
	if(correctness == 0){ //generate incorrect equation
		if (nbres <= 0 || randint(0,1) == 0)
			nbres += randint(1, 6);
		else
			nbres -= randint(1, nbres);
	}
	
	eq = "("+nb1+" "+sign1+" "+nb2+") "+sign2+" "+nb3+" = "+nbres
	//eq = "("+nb1+" "+sign1+" "+nb2+") "+sign2+" "+nb3+" = "+nbres+"   --  "+correctness;
	current_maths_correctness = correctness;
	return eq;
}

//randomly select a new word for the current sequences
function generate_word(){
	var idw =  randint(0, list_words.length-1);
	
	if(current_words.length == list_words.length)
		current_words = [];
	
	while ( inArray(idw, current_words))
		idw =  randint(0, list_words.length-1);
	
	current_words[current_words.length] = idw;
	return list_words[idw];
}

//display a word for 1s
function show_word(a){
	var duration = new Date().getTime() - start_maths;
	avg_time_maths += duration;

	if(!practice){
		if(current_maths_correctness == a){
			score_maths++;
		}
	}

	document.getElementById("maths_block").style.display = "none";
	document.getElementById("word_block").innerHTML = generate_word();
	current_iter++;
	setTimeout(do_transition, DURATION_WORD_DISPLAYED_MS);
}

//display the formular to enter word sequences
function show_words_inputs(){
	var inputs = ""
	for(var i=0; i<length_sequence; i++){
		inputs += "<input type=\"text\" id=\"answer"+i+"\" />&nbsp;"
	}
	inputs += "<br /><br /><button onclick =\"collect_answers()\">Continue</button>"

	document.getElementById("maths_block").style.display = "none"
	document.getElementById("answers").innerHTML = inputs
	document.getElementById("answers").style.display = "block"
}

//last instruction before starting the test
function show_end_practice(){
	document.getElementById("practice").innerHTML += "<p>You have finish the practice session.<br /><br />Remember to enter the words in the correct order. You can leave fields blank.<br />Please try to answer correctly and as fast as possible the arithematic operations.<br /><br /><button onclick=\"init()\">Click here to start the main task</button>";
}

//compute word score and span
function collect_answers(){
	if(!practice){
		var score = 0
		for(var i=0; i<length_sequence; i++){
			var a = document.getElementById("answer"+i).value;
			a = a.toLowerCase();
			if(a == list_words[current_words[i]]){
				score_word++;
				score++;
				partial_span_score_word++;
			}
			else{
				for(var j=0; j<length_sequence; j++){
					if(i != j && a == list_words[current_words[j]]){
						partial_span_score_word++;
					}
				}
			}
		}
		if(score == length_sequence && score>longest_sequence_correct){
			longest_sequence_correct = score;
		}
	}
	
	document.getElementById("answers").style.display = "none";
	
	if(practice){
		practice=false;
		show_end_practice();
		return;
	}
	else{
		if(nb_words_viewed >= MAX_WORDS){
			terminate();
			return;
		}
		else{
			if(avg_time_maths/nb_words_viewed > 6000){ //the user take too long to answer arithmetic questions
				alert("You took too long to answer arithmetic questions. Please try to answer (True or False) as fast as possible.");
			}
			generate_new_sequences();
			do_transition();
		}
	}
}

//display the next mathematical operation
function do_transition(){
	document.getElementById("word_block").innerHTML = ""
	document.getElementById("maths_block").style.display = "block"
	
	if(current_iter == length_sequence){
		show_words_inputs();
	}
	else{
		document.getElementById("calcul_block").innerHTML = generate_equation();
		start_maths = new Date().getTime();
	}
}

//init the test
function init(){
	if(practice){
		document.getElementById("practice").style.display = "block";
	}
	else{
		document.getElementById("practice").style.display = "none";
		
		var beginning = new Array();
		var next = new Array();
		var number_beginning_sequence = Math.min(MAX_LENGTH_SEQUENCE, MIN_LENGTH_SEQUENCE+2);
		for(var i=MIN_LENGTH_SEQUENCE; i<=number_beginning_sequence; i++){ //easy task at the beginning
			beginning.push(i);
		}
		for(var i=number_beginning_sequence+1; i<=MAX_LENGTH_SEQUENCE; i++){ //easy task at the beginning
			next.push(i);
		}
		for(var i=MIN_LENGTH_SEQUENCE; i<=MAX_LENGTH_SEQUENCE; i++){
			for (var j=0; j<REPETITION_SEQUENCE-1; j++){
				next.push(i);
			}
			shuffleArray(next); //then random order
			sequences_order = beginning.concat(next);
		}
	}
	
	if(uid == "" && document.getElementById("uid").value != ""){
		uid = document.getElementById("uid").value;
		uid = uid.trim();
	}
	
	generate_new_sequences();
	document.getElementById("instruction").style.display = "none";
	document.getElementById("answers").style.display = "none";
	document.getElementById("maths_block").style.display = "block";

	document.getElementById("calcul_block").innerHTML = generate_equation();
	start_maths = new Date().getTime();
}

//end of the script, write results
function terminate(){
	document.getElementById("answers").style.display = "none";
	document.getElementById("maths_block").style.display = "none";
	document.getElementById("word_block").style.display = "none";
	document.getElementById("final_scores").style.display = "block";
	
	avg_time_maths = avg_time_maths / MAX_WORDS;
	
	//save results
	$.post("saveOP.php",
    {
		uid: uid,
        max_words: MAX_WORDS,
        max_length: MAX_LENGTH_SEQUENCE,
        score_maths: score_maths,
        score_word: score_word,
        longest_sequence_correct: longest_sequence_correct,
		partial_span_score_word: partial_span_score_word,
        avg_time_maths: avg_time_maths
    },
    function(data, status){
        //alert(data+" -- "+status);
    });
	
	document.getElementById("final_scores").innerHTML = "<p>Thanks for taking the task. It is completed now. You scored:</p>";
	document.getElementById("final_scores").innerHTML += "<ul><li>Participant number: "+uid+"<li>Correct Arithmetic Operation (out of "+MAX_WORDS+"): "+score_maths+"<li> Total Word Correctly Recalled (out of "+MAX_WORDS+"): "+score_word+"<li> Word Span In Working Memory (max is "+MAX_LENGTH_SEQUENCE+"): "+longest_sequence_correct+"<li>Partial Correct Memory Span: "+partial_span_score_word+"<li> Average time (milli-seconds): "+Math.round(avg_time_maths,0)+"</ul>";
}
</script>

</head>

<body >

<div id="instruction" style="    margin: auto;width: 900px">
<h1>Instruction for Online Operation-Word Task</h1>
<p>Thanks for taking this task. It consists of 60 trials. In every trial there is a pair of an arithmetic operation and a word.  e.g.<br />
<br />
             (8 / 4) + 3 = 10  &nbsp;&nbsp;&nbsp;&nbsp;   <em>bone</em><br />
<br />
First you will be shown the operation: <br />
<br />
            (8 / 4) + 3 = 10<br />
<br />
and you need to click the <strong>correct</strong> button (True or False) <strong>as fast as you can</strong>.<br />
<br />
After you click the button, the word "<em>bone</em>" will appear for a while. Try to <strong>remember</strong> the word. <br />
<br /><br />
The operation-word pair will be repeated between 2-6 times. For example:<br />
<br />
             (8 / 4) + 3 = 10 &nbsp;&nbsp;&nbsp;&nbsp;     <em>bone</em><br />
             (3 X 2) + 4 = 5  &nbsp;&nbsp;&nbsp;&nbsp;    <em>rose</em><br />
             (4 / 1) + 0 = 4    &nbsp;&nbsp;&nbsp;&nbsp;    <em>pet</em><br />
<br />
At the end of these 3 operation-word pairs, you will be asked to type in the 3 words <strong>in the right order</strong> they were shown, i.e.&nbsp;&nbsp;<em>bone&nbsp;&nbsp;rose&nbsp;&nbsp;pet</em><br />
<br />
No pen/paper or other tools are allowed in the test (<strong>time is recorded and speed matters</strong>). Please do not rehearse the words aloud at any point during the test. Please follow the instructions carefully, since otherwise your score will not adequately measure your abilities.<br />
<br /><br />
You are suggested to avoid any disturbance during the task as it will only take about 10min.<br />
<br /><br />
    <input type="hidden" id = "uid" name="uid" value="<?php  if(isset($_GET['uid'])) echo addslashes(htmlentities($_GET['uid'])); ?>" />
    <p>User ID: <label><b><?php if(isset($_GET['uid'])) print addslashes(htmlentities($_GET['uid']));  ?></b></label><br /></p>
<br /><br />
<button onclick="init()" style="font-size : 20px;"> Click here to start the task once you have read and understood the instruction.</button>
</p>
</div>

<div id="practice"><h1>Practice session</h1></div>

<div id="maths_block">
	<div id="calcul_block"></div>

	<br />Is it: &nbsp;&nbsp;
	<button onclick = "show_word(1)">True</button>&nbsp;&nbsp;
	<button onclick = "show_word(0)">False</button>
</div>

<div id="word_block"></div>

<div id="answers"></div>

<div id="final_scores"></div>

<script type="text/javascript">
	document.getElementById("maths_block").style.display = "none"
	document.getElementById("practice").style.display = "none"
	document.getElementById("final_scores").style.display = "none"
</script

</body>
</html>
