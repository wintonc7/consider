// Dynamically reloads the page content and refreshes
// the highlighting/styles in the navigation bar to reflect
// which round is being displayed.
var currentPage = $('#reload').data().currentPage;
var sectionKey = $('#reload').data().sectionkey;

var curr_round = currentPage;
function loadRound(round) {
    var url = location.href.split('?')[0] + '?section=' + sectionKey + '&round=' + round;
    $("#navbar li").removeClass("round-viewing nav-active");
    $("#navbar a").removeClass("round-viewing nav-active");
    getRoundButton(round).addClass("round-viewing nav-active");
    $('#pageContent').load(url + ' #pageContent', function() {
        $(this).children(':first').unwrap();
        if (curr_round == round) {
            reloadOpinions();
        }
    });
    // Update page number of page being viewed.
    view_page = round;
}

// Helper function that dynamically reapplies the selected
// opinion(s) for comment(s) if viewing current round.
function reloadOpinions() {
    if (typeof resp !== 'undefined') {
        resp.forEach(function(opinion, index) {
            if (index > 0) {
                $("#jum_" + index).removeClass().addClass('jumbotron ' + opinion);
            }
        });
    }
}

// Returns the jQuert element corresponding to the specified
// round's button (li element).
function getRoundButton(round) {
    return $('.nav_reload[data-round="' + round + '"]')
}

var view_page = currentPage;

// Dynamically reload the page content when a navigation
// button is pressed.
$(".nav_reload").click(function(event) {
    event.preventDefault();
    loadRound($(event.target).data('round'));
});
