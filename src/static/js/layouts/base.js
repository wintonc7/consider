jQuery.ajaxSetup({
    beforeSend: function () {
        $('#spinner').show();
    },
    complete: function () {
        $('#spinner').hide();
    },
    success: function () {
    }
});

$(window).load(function () {
    $("#spinner").fadeOut("slow");
});
