/**
 * Created by Enamul on 2016-11-23.
 */
var MMDSet = [];
var currentMMD; //by default


/*$( "#button_next" ).click(function() {
     console.log(new Date().getTime()); //get the timestamp

     var getCurrentMMDIndex = MMDSet.indexOf(parseInt(currentMMD));
     if(getCurrentMMDIndex<MMDSet.length){
          currentMMD = (MMDSet[getCurrentMMDIndex+1]).toString();
          console.log(currentMMD);
          loadMMD(currentMMD);

     }

});
*/

     console.log("dfasdasdasd");
d3.json("static/data/conditions.json", function(data){
     console.log(data);
	 var selectHtml = "";
     MMDSet = data;
     for(var i=0;i<data.length;i++){
          //console.log(data[i]);
          selectHtml+= '<option value="'+data[i]+'">'+data[i]+'</option>';
     }
     $("#mmdOptions").html(selectHtml);

     $("#mmdOptions").change(function() {
          //alert($(this).find("option:selected").text()+' clicked!');
          currentMMD = $(this).find("option:selected").text();
          loadMMD(currentMMD);
     });




});

function loadMMD(mmdName){	
     d3.json("static/data/"+mmdName+".json", function(data){
          $("#thetextparagraph").html(data.text);
          //console.log('<img src='+data.chart+'');
          $("#visualization").html('<img src="static/'+data.chart+'">' );

     });
}
