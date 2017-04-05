$(document).ready(function() {

  $("#feedback").submit(formSubmit);

  function formSubmit(event) {
      //Prevent the default behaviour
      event.preventDefault();

      var email, tag, othertag, comments;

      email = $('#email').is(":checked");
      tag = $('#tag').val();
      othertag= $('#othertag').val();

      console.log(email);

      // Update content of textarea(s) handled by CKEditor
      for ( instance in CKEDITOR.instances ) {
          CKEDITOR.instances[instance].updateElement();
          comments = CKEDITOR.instances[instance].getData().replace(/<p>/g,'').replace(/<\/p>/g,'').replace(/&nbsp;/g,'');
      }

      var $form = $(this);
      var url = $form.attr("action");

          $.post(url, {email: email.toString(), tag: tag, othertag: othertag, comments: comments});
  }


  function CheckTag(val){
        var element = getElementById('othertag');
        if(val=="other")
            element.style.display='block';
        else
            element.style.display='none';
  }
});
