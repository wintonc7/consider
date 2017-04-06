$(document).ready(function() {

  $("#feedback").submit(formSubmit);

  function formSubmit(event) {
      //Prevent the default behaviour
      event.preventDefault();

      var email, tags, othertagged, comments;

      email = $('#email').is(":checked");
      othertag= $('#other').is(":checked");

      // Update content of textarea(s) handled by CKEditor
      for ( instance in CKEDITOR.instances ) {
          CKEDITOR.instances[instance].updateElement();
          comments = CKEDITOR.instances[instance].getData().replace(/<p>/g,'').replace(/<\/p>/g,'').replace(/&nbsp;/g,'');
      }

      //construct tag list
      tags = "";

      for(i = 1; i <= 4; i++) {
        if($('#tag' + i).is(':checked')) {
            tags+=$('#tag' + i).val();
            tags+=",";
        }
      }

      if(othertag){
            tags+=$('#othertag').val();
            tags+=","
      }

      var $form = $(this);
      var url = $form.attr("action");

          $.post(url, {email: email.toString(), tags: tags, othertag: othertag.toString(), comments: comments});
  }
});

