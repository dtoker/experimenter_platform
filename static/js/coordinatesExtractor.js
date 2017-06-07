/**
 * Created by enamul on 6/3/2017.
 */
function findCoordinatesofCharacters(textElementID) {
  var coordinatesChars = [];
  var newText =  "";
  var oldText = $(textElementID).text();
  //console.log($(textElementID).text());

  for (var i = 0, len = oldText.length; i < len; i++) {
    newText+= '<span>'+oldText[i]+ '</span>';
  }
  //console.log(newText);

  $(textElementID).html(newText);

  $spans = $(textElementID).find('span');
  $spans.each(function(){
    var $span = $(this),
        $offset = $span.offset();
    $offset.width = $span.innerWidth();
    $offset.height = $span.innerHeight();
    coordinatesChars.push($offset);
    console.log($offset);
  });
  $(textElementID).html(oldText);
  return coordinatesChars;
}


function findCoordinatesofSentences(textElementID, coordinatesofChar) {
  var sentSpanCoord = [], sentencePolygonCoordinates = [];
  var newText =  "";
  var oldText = $(textElementID).text();
  console.log($(textElementID).text());

  var result = oldText.match( /[^\.!\?]+[\.!\?]+/g ); // regular expression for splitting into sentences

  //put a span for each sentence
  for (var i = 0, len = result.length; i < len; i++) {
    newText+= '<span>'+result[i]+ '</span>';
  }
  $(textElementID).html(newText);

  $spans = $(textElementID).find('span');
  $spans.each(function(){
    var $span = $(this),
        $offset = $span.offset();
    $offset.width = $span.innerWidth();
    $offset.height = $span.innerHeight();
    $offset.sentence = $span.text();
    sentSpanCoord.push($offset);
    console.log($offset);
  });
  $(textElementID).html(oldText);

// loop over each sentence of the paragraph
  for(var i=0; i<sentSpanCoord.length;i++){
    var paragraphText = oldText;
    var sentenceStartPosition = paragraphText.indexOf(sentSpanCoord[i].sentence);
    var sentenceEndPosition = paragraphText.indexOf(sentSpanCoord[i].sentence)+sentSpanCoord[i].sentence.length-1;
    //console.log(sentenceStartPosition,sentenceEndPosition);
    var coordofSentStartPosition = coordinatesofChar[sentenceStartPosition];
    var coordofSentEndPosition = coordinatesofChar[sentenceEndPosition];

    // eight points needed to build the polygon
    sentencePolygonCoordinates.push([
      {"x":coordofSentStartPosition.left, "y":coordofSentStartPosition.top},
      {"x":coordofSentStartPosition.left, "y":coordofSentStartPosition.top+coordofSentStartPosition.height},
      {"x":sentSpanCoord[i].left, "y":coordofSentStartPosition.top+coordofSentStartPosition.height},
      {"x":sentSpanCoord[i].left, "y":sentSpanCoord[i].top+ sentSpanCoord[i].height},
      {"x":coordofSentEndPosition.left+coordofSentEndPosition.width, "y":coordofSentEndPosition.top+coordofSentEndPosition.height},
      {"x":coordofSentEndPosition.left+coordofSentEndPosition.width, "y":coordofSentEndPosition.top},
      {"x":sentSpanCoord[i].left + sentSpanCoord[i].width, "y":coordofSentEndPosition.top},
      {"x":sentSpanCoord[i].left + sentSpanCoord[i].width, "y":sentSpanCoord[i].top}
    ]);
  }

  return sentencePolygonCoordinates;

};
//coordinates of each sentence with index, each word within sentence with index, num of word in each sentence
function aggregateintoJSON(char, sentece, word){


}

//function to sav coordinates
function sendJSONtoTornado(jsonObj){
  $.ajax({
    url: '/saveCoordinates',
    //headers: {'X-XSRFToken' : "" },
    data: JSON.stringify(jsonObj),
    dataType: "JSON",
    type: "POST",
    success: function ( data , status_text, jqXHR) {
      console.log('ajax success')
    },
    error: function ( data , status_text, jqXHR ) {
      console.log('ajax fail')
    },
  });

}

//check whether a point is within the polygon vs
function inside(point, vs) {
  // ray-casting algorithm based on
  // http://www.ecse.rpi.edu/Homepages/wrf/Research/Short_Notes/pnpoly.html

  var x = point[0], y = point[1];

  var inside = false;
  for (var i = 0, j = vs.length - 1; i < vs.length; j = i++) {
    var xi = vs[i][0], yi = vs[i][1];
    var xj = vs[j][0], yj = vs[j][1];

    var intersect = ((yi > y) != (yj > y))
        && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
    if (intersect) inside = !inside;
  }

  return inside;
};

//assumption is that word would not be in multiple lines
function findCoordinatesofWords(textElementID) {


}