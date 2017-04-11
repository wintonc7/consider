/**
 * Created by Daniel Stelson on 4/7/2017.
 */
$(document).ready(function() {
    $('#tag-select').change(filterFeedback);
});

function filterFeedback(){
    //console.log("filter feedback")
    var filterTo = $('#tag-select')[0].value;
    //console.log(filterTo + " Selected");
    //construct ids
    var id = 1;
    var cardId = "card" + id;
    var cardBodyId = "cardBody" + id;
    //get html elements
    var card = document.getElementById(cardId);
    var cardBody = document.getElementById(cardBodyId);
    while(card){
        //console.log(cardId);
        if(filterTo=="DEFAULT"){
            //make everything visible
            card.style.display = 'block';
        }else if(filterTo == "Other"){
            //check card value and only displays cards w/ true
            if(card.getAttribute("value") == "True"){
                card.style.display = 'block';
            }else{
                card.style.display = 'none';
            }
        }else{
            var tags = cardBody.getAttribute("value");
            if(~tags.indexOf(filterTo)){
                card.style.display = 'block';
            }else{
                card.style.display = 'none';
            }
        }
        //update element objects
        id = id+1;
        cardId = "card" + id;
        cardBodyId = "cardBody" + id;
        card = document.getElementById(cardId);
        cardBody = document.getElementById(cardBodyId);
    }
}