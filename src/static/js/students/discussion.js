$(document).ready(function() {
  var numComments = $('#student-discussion').data().numcomments;
  var response = $('#student-discussion').data().response;
  var expired = $('#student-discussion').data().expired;
  var sectionKey = $('#student-discussion').data().sectionkey;
  var page = $('#student-discussion').data().page;

  var resp = [];
  var thumbs = {};
  resp[0] = null;

  if (response.length > 0)
  {
    resp = resp.concat(response.split(','));
  }

  if (expired.length == 0)
  {
    $('.alert .close').on('click', function (e) {
        $(this).parent().hide();
    });
  }

  $("#form").submit(formSubmit);

  function formSubmit(event) {

    var expired = $('#student-discussion').data().expired;
    if (expired.length == 0)
    {
      //Prevent the default behaviour
      event.preventDefault();

      var sectionKey = $('#student-discussion').data().sectionkey;

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
          var comment = CKEDITOR.instances.comment.getData().replace(/<p>/g,'').replace(/<\/p>/g,'').replace(/&nbsp;/g,'');
          var url = $form.attr("action");

          $.post(url, {comm: comment, response: JSON.stringify(resp), section: sectionKey, thumbs:JSON.stringify(thumbs)}, function (data) {
              bootbox.alert(data, function () {
                  ocomment = comment;
              });
          });
      }
    }
  }

  // Checks if the user has selected their opinion for all the comments;
  // returns true if they have, false if there are any comments they have
  // not picked an opinion on.
  function selAll() {
    for (var i = 1; i <= $('#student-discussion').data().numcomments; i++) {
        if (!resp[i]) return false;
    }
    return true;
  }

  window.updateAlert = function(obj, email, type) {
    var expired = $('#student-discussion').data().expired;
    var page = $('#student-discussion').data().page;
    if (expired.length == 0)
    {
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
      message += email + '\'s Round ' + page;
      console.log(message);
      thumbs[email] = type;
    }
  }
});

if ($('#student-discussion').data().expired.length == 0)
{
  $(window).bind('beforeunload', function () {
    var ocomment = $('#comment').val();
      if ($('#comment').val() !== ocomment) {
          return "It looks like you have input you haven't submitted.";
      }
  });
}
