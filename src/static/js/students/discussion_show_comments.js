var numComments = {{comments | length}};
var resp = [];
var thumbs = {};
resp[0] = null;
{% if response %}
resp = resp.concat('{{response}}'.split(','));
{% endif %}
{%- if not expired -%}
$('.alert .close').on('click', function (e) {
    $(this).parent().hide();
});
$("#form").submit(function (event) {
    //Prevent the default behaviour
    event.preventDefault();
    // Update content of textarea(s) handled by CKEditor
    for ( instance in CKEDITOR.instances ) {
        CKEDITOR.instances[instance].updateElement();
    }
    //collect form elements
    if (!selAll()) {
        // Missing some opinions; force reload current page dynamically
        // and pop up the alert box.
        loadRound(curr_round);
        bootbox.alert('Please choose your opinion for all the comments.');
    } else {
        var $form = $(this);
        var comment = $form.find("textarea").val();
        var url = $form.attr("action");
        console.log('Thumbs = '+JSON.stringify(thumbs));
        $.post(url, {comm: comment, response: JSON.stringify(resp), section: '{{sectionKey}}', thumbs:JSON.stringify(thumbs)}, function (data) {
            bootbox.alert(data, function () {
                ocomment = comment;
            });
        });
    }
});
// Checks if the user has selected their opinion for all the comments;
// returns true if they have, false if there are any comments they have
// not picked an opinion on.
function selAll() {
    for (var i = 1; i <= numComments; i++) {
        if (!resp[i]) return false;
    }
    return true;
}
function updateAlert(obj, email, type) {
    var index = obj.id.substring(4);
    var message = 'Current student ';
    if (type == 1) {
        $("#jum_" + index).removeClass().addClass('jumbotron').addClass('support');
        resp[index] = 'support';
        message += 'supports ';
    } else if (type == 0) {
        $("#jum_" + index).removeClass().addClass('jumbotron').addClass('neutral');
        resp[index] = 'neutral';
        message += 'seeks clarification from ';
    } else {
        $("#jum_" + index).removeClass().addClass('jumbotron').addClass('disagree');
        resp[index] = 'disagree';
        message += 'disagrees with ';
    }
    message += email + '\'s Round ' +{{ curr_page-2 }};
    console.log(message);
    thumbs[email] = type;
}
var ocomment = $('#comment').val();
$(window).bind('beforeunload', function () {
    if ($('#comment').val() !== ocomment) {
        return "It looks like you have input you haven't submitted.";
    }
});
{% endif %}
