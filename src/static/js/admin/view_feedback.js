/**
 * Created by Daniel Stelson on 4/7/2017.
 */

 var fbNum = 0;

$(document).ready(function() {
    $('#tag-select').change(filterArchives);
    $('#status-select').change(filterArchives);
    $('#show-select').change(filterArchives);
    filterArchives();
});

function filterFeedback(){
    //console.log("filter feedback")
    var filterToTag = $('#tag-select')[0].value;
    var filterToStatus = $('#status-select')[0].value;
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
        if(filterToTag=="DEFAULT" && filterToStatus=="DEFAULT"){
            //make everything visible
            card.style.display = 'block';
        }else if(filterToTag=="DEFAULT" && filterToStatus!="DEFAULT"){
            //filter based only on status
            var status = document.getElementById("status"+id).getAttribute("value");
            if(status==filterToStatus){
                card.style.display = 'block';
            }else{
                card.style.display = 'none';
            }
        }else if(filterToTag!="DEFAULT" && filterToStatus=="DEFAULT"){
            //filter based only on tag
            if(filterToTag=="Other"){
                if(card.getAttribute("value") == "True"){
                    card.style.display = 'block';
                }else{
                    card.style.display = 'none';
                }
            }else{
                var tags = cardBody.getAttribute("value");
                if(~tags.indexOf(filterToTag)){
                    card.style.display = 'block';
                }else{
                    card.style.display = 'none';
                }
            }
        }else{
        //filter by both
            var tags = cardBody.getAttribute("value");
            var status = document.getElementById("status"+id).getAttribute("value");
            //if filtering for other tag
            if(filterToTag=="Other"){
                if((card.getAttribute("value") == "True") && (status==filterToStatus)){
                    card.style.display = 'block';
                }else{
                    card.style.display = "none";
                }
            }else{//filtering by tag that is not other
               if((~tags.indexOf(filterToTag)) &&  (status==filterToStatus)){
                    card.style.display = 'block';
               }else{
                    card.style.display = "none";
               }
            }
        }

        //update element objects
        id = id+1;
        cardId = "card" + id;
        cardBodyId = "cardBody" + id;
        card = document.getElementById(cardId);
        cardBody = document.getElementById(cardBodyId);
    }
    fbNum = id-1;
}

function sendGet(){
    var show = $('#show-select')[0].value;
    $.get("/view_feedback", {show: show});

}

function filterArchives(){
    filterFeedback();
    console.log(fbNum);
    var showArchived = ($('#show-select')[0].value == "Archived");
    console.log("showArchived: " + showArchived);
    for(count = 1; count<=fbNum; count++){
        console.log("iteration: " + count);
        var card = document.getElementById("card" + count);
        if(card){
            var deleteButton = document.getElementById("delete" + count);
            if(deleteButton){
                if(!showArchived){
                    console.log("hiding card");
                    card.style.display = 'none';
                }
            }else{
                if(showArchived){
                    console.log("showing card");
                    card.style.display = 'none';
                }
            }
        }
    }
}

function advanceTicket(idnum){
    //console.log("advance ticket " +idnum);
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
    //console.log("delete ticket " + idnum);
    var fb_id = document.getElementById("cardTitle"+idnum).getAttribute("value");
    bootbox.confirm("Are you sure you want to delete this ticket?", function(){
        $.post("/view_feedback", {id: fb_id, action: "DELETE"}, function(resp){
            //console.log(resp);
            location.reload(true);
        });
    });
}

function archiveTicket(idnum){
    var fb_id = document.getElementById("cardTitle"+idnum).getAttribute("value");
    var status = document.getElementById("status"+idnum).getAttribute("value");
    if(status == "CLOSED"){
        $.when($.post("/view_feedback", {id: fb_id, action: "ARCHIVE"}, function(resp){
            //console.log(resp);
        })).done(function(){
            location.reload(true);
        });
     }else{
        bootbox.alert("Error: You can only archive closed tickets");
     }
}

function reactivateTicket(idnum){
    var fb_id = document.getElementById("cardTitle"+idnum).getAttribute("value");
    $.when($.post("/view_feedback", {id: fb_id, action: "REACTIVATE"}, function(resp){
        //console.log(resp);
     })).done(function(){
        location.reload(true);
     });
}