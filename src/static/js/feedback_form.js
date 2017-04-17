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

      if(comments.length > 0 && tags.length > 0){
            $.post(url, {email: email.toString(), tags: tags, othertag: othertag.toString(), comments: comments});
            bootbox.alert("Thank You for submitting feedback!", function(){
                is_student = $('#email').val();
                if(is_student){
                    window.location = "/student_home";
                }else{
                    window.location = "/courses";
                }
            });
      }else{
            bootbox.alert("To submit you must have entered feedback and selected at least one tag");
      }
  }
});

