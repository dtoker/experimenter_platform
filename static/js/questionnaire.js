
/**
 * Demo in action!
 */
    // (function() {



    // SHOP ELEMENT
var shop = document.querySelector('#star_rating');

// DUMMY DATA
var starData = [
    {
        id: "1",
        description: "The article/snippet was easy to understand.",
        rating: null
    },
    {
        id: "2",
        description: "I am interested in reading the full article.",
        rating: null
    }

];

// INITIALIZE
(function init() {
    for (var i = 0; i < starData.length; i++) {
        addRatingWidget(buildShopItem(starData[i]), starData[i]);
    }
})();

// BUILD SHOP ITEM
function buildShopItem(data) {
    var shopItem = document.createElement('div');

    var html = '<div class="c-shop-item__img"></div>' +
        '<div class="c-shop-item__details">' +
        // '<h3 class="c-shop-item__title">' + data.title + '</h3>' +
        '<table><tr><td><p class="c-shop-item__description">' + data.description + '</p></td>' +
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
        $.getJSON('LogInteraction'+'?jsonp=?', {'text' : userid+","+userstring, 'filename' : '/SaveData/UserData/'+userid+'_post.csv', 'append' : "true"});

        if (typeof(Storage) !== "undefined") {
            localStorage.setItem("USERID", userid);
        } else {
            console.log("Sorry, your browser does not support Web Storage...");
        }
        //console.log("yes");

        window.location.replace("user.html");
    }
    else {
        $('#li_1 .description').css("color","red");
    }
}