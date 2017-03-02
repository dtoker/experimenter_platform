
/**
 * Demo in action!
 */
    // (function() {



    // SHOP ELEMENT
var shop = document.querySelector('#star_rating');
var questionList = document.querySelector('#questionList');

console.log(questionObj);
// DUMMY DATA
var starData = [
    {
        mmdid: '',
        id: "1",
        qid: "1",
        questionBody: "The article/snippet was easy to understand.",
        type: 'likert',
        
        //rating: null
    },
    {
        id: "2",
        questionBody: "I am interested in reading the full article.",
        type: 'likert',
        rating: null
    }

];

for(var i=0;i<questionObj.length;i++){
  var questionData = {
    mmdId: questionObj[i][0],
    qid: questionObj[i][1],
    questionBody: questionObj[i][2],
    questionType: questionObj[i][3],
    answers: questionObj[i][4],
    rating: null
  };
  console.log(questionData);
  if(questionData.questionType==='Likert'){

      addRatingWidget(buildShopItem(questionData), questionData);
  }
  else if(questionData.questionType==='MC' || questionData.questionType==='TF'){
    $( "#questionList" ).append( buildMultipleChoiceQuestion(questionData));
  }
}

// // INITIALIZE
// (function init() {
//     for (var i = 0; i < starData.length; i++) {
//         addRatingWidget(buildShopItem(starData[i]), starData[i]);
//     }
// })();

 function buildMultipleChoiceQuestion(questionData){
   var  questionID = questionData.qid;
   var answers = questionData.answers.split(',');


    var html = '<li id="li_'+questionID+'" >'+
      '<label class="description" for="element_2">'+questionData.questionBody+'</label>'+
      '<span>';

   for(var i=0;i<answers.length;i++){
     answers[i] = answers[i].substring(4, answers[i].length-2);


     html+= '<input id="element_'+questionID+'_1" name="element_2" class="element radio" type="radio" value="1" />'+
     '<label class="choice" for="element_2_1">'+answers[i]+'</label>';
   }



      //'<input id="element_'+questionID+'_2" name="element_1" class="element radio" type="radio" value="2" />'+
      //'<label class="choice" for="element_2_2">False</label>'+
   html+='</span>'+
      '</li>';
    return html;
}
// BUILD SHOP ITEM
function buildShopItem(data) {
    var shopItem = document.createElement('div');

    var html = '<div class="c-shop-item__img"></div>' +
        '<div class="c-shop-item__details">' +
        // '<h3 class="c-shop-item__title">' + data.title + '</h3>' +
        '<table><tr><td><p class="c-shop-item__questionBody">' + data.questionBody + '</p></td>' +
        '<td><ul class="c-rating"></ul></td></tr></table>' +
        '</div>';

    shopItem.classList.add('c-shop-item');
    shopItem.innerHTML = html;
    shop.appendChild(shopItem);

    return shopItem;
}

// ADD RATING WIDGET
function addRatingWidget(shopItem, data) {
    var ratingElement = shopItem.querySelector('.c-rating');
    var currentRating = data.rating;
    var maxRating = 5;
    var callback = function(rating) { //alert(rating);
        //console.log(data.id+","+rating+", "+data.rating)
        for (i=0;i,starData.length;i++){
            if(starData[i].id==data.id) {
                starData[i].rating=rating;
                break;
            }
        }
        //console.log(starData);
    };
    var r = rating(ratingElement, currentRating, maxRating, callback);
}

//})();


function getSelectedValue(element){
    var txt="";
    for (i = 0; i < element.length; i++) {
        if (element[i].checked) {
            txt = txt + element[i].value + " ";
        }
    }
    return txt;

}
function submitPostStudy() {
    var userstring="";
    var userid=localStorage.getItem("USERID");

    var f = document.forms[0];
    var txt="";
    var i;
    //console.log(starData);
    console.log(f.element_1);
    if(getSelectedValue(f.element_1)!=''){
        for (i=0;i<starData.length;i++){
            //console.log(starData[i].rating);
            userstring+=starData[i].rating+",";
        }

        userstring+=
            getSelectedValue(f.element_1)+","+$('#element_6').val()+","+$('#element_7').val();
        console.log(userstring);
        //alert($('#element_6').val()+" "+$('#element_7').val());
        //$.getJSON('LogInteraction'+'?jsonp=?', {'text' : userid+","+userstring, 'filename' : '/SaveData/UserData/'+userid+'_post.csv', 'append' : "true"});

        if (typeof(Storage) !== "undefined") {
            localStorage.setItem("USERID", userid);
        } else {
            console.log("Sorry, your browser does not support Web Storage...");
        }
        //console.log("yes");

        window.location.replace("user.html");
    }
    else {
        $('#li_1 .questionBody').css("color","red");
    }
}