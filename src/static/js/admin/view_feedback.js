/**
 * Created by Daniel Stelson on 4/7/2017.
 */
$(document).ready(function() {
    $('#tag-select').change(filterFeedback);
    //var id = 1;
    //var cardTitle = document.getElementById("cardTitle"+id);
    //while(cardTitle){
    //    $('#delete'+id).onClick = deleteTicket(id);
    //    $('#advance'+id).onClick = advanceTicket(id);
    //    id = id+1;
    //    cardTitle = document.getElementById("cardTitle"+id);
    //}
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

function advanceTicket(idnum){
    console.log("advance ticket " +idnum);
    var fb_id = document.getElementById("cardTitle"+idnum).getAttribute("value");
    $.post("/view_feedback", {id: fb_id, action: "ADVANCE"}, function(resp){
        //console.log(resp);
        location.reload(true);
    });
}

function markOpen(idnum){
    var fb_id = document.getElementById("cardTitle"+idnum).getAttribute("value");
    $.post("/view_feedback", {id: fb_id, action: "OPEN"}, function(resp){
        //console.log(resp);
        location.reload(true);
    });
}

function markInProgress(idnum){
    var fb_id = document.getElementById("cardTitle"+idnum).getAttribute("value");
    $.post("/view_feedback", {id: fb_id, action: "IN PROGRESS"}, function(resp){
        //console.log(resp);
        location.reload(true);
    });
}

function markClosed(idnum){
    var fb_id = document.getElementById("cardTitle"+idnum).getAttribute("value");
    $.post("/view_feedback", {id: fb_id, action: "CLOSED"}, function(resp){
        //console.log(resp);
        location.reload(true);
    });
}

function deleteTicket(idnum){
    console.log("delete ticket " + idnum);
    var fb_id = document.getElementById("cardTitle"+idnum).getAttribute("value");
    $.post("/view_feedback", {id: fb_id, action: "DELETE"}, function(resp){
        //console.log(resp);
        location.reload(true);
    });
}