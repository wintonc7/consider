var countdown = $('#countdown').data().countdown;

$('#clock').countdown(countdown, function (event) {
    $(this).html(event.strftime('%D days %H:%M:%S'));
});
//    TODO: Show 'days' part only when time left is more than 24 hours
//    TODO: When it reaches 0, if this is the first time the student is putting in his answer, autosave whatever is in the inupt box, and disable the box as well as the button.
