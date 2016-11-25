$(document).ready(function() {
  var option = $('#student-round').data().option;
  var expired = $('#student-round').data().expired;
  var lastRound = $('#student-round').data().last;
  var sectionKey = $('#student-round').data().sectionkey;

  if (option.length > 0)
  {
    $(option).prop("checked",true);
    // Make sure this is working
  }
  var radio, comment, summary;

  $("#form").submit(formSubmit);

  function formSubmit(event){

    var radio, comment, summary;
    if (expired.length == 0)
    {
      //Prevent the default behaviour
      event.preventDefault();

      // Update content of textarea(s) handled by CKEditor
      for (instance in CKEDITOR.instances) {
          CKEDITOR.instances[instance].updateElement();
      }

      //collect form elements
      var $form = $(this);

      if (document.getElementsByClassName('optionsRadios').length > 0
              && $form.find("input:radio[name='optionsRadios']:checked").val() === undefined) {
          bootbox.alert("Please select one of the options");
      }
      else
      {
        radio = $form.find("input:radio[name='optionsRadios']:checked").val();
        comment = CKEDITOR.instances.comment.getData().replace(/<p>/g,'').replace(/<\/p>/g,'').replace(/&nbsp;/g,'');
        var url = $form.attr("action");

        if (lastRound.localeCompare("True") === 0)
        {
          summary = CKEDITOR.instances.summary.getData().replace(/<p>/g,'').replace(/<\/p>/g,'');
        }
        else {
          summary = '';
        }

        if (comment.length > 0)
        {
          $.post(url,{option:radio, comm:comment, summary:summary, section:sectionKey},function (data) {
              bootbox.alert(data,function(){
                  ocomment = comment;
              });
          });
        }
        else {
          bootbox.alert("It looks like you haven't submitted everything.")
        }
      }
    }
  }
});

if ($('#student-round').data().expired.length == 0)
{
  $(window).bind('beforeunload', function () {
    var ocomment = $('#comment').val();
      if ($('#comment').val() !== ocomment) {
          return "It looks like you have input you haven't submitted.";
      }
  });
} // not expired
