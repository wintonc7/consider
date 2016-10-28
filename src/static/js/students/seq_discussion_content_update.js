var sectionKey = $('#content-update').data().sectionkey;

$('#seqDiscussionForm').submit(function (event) {
    event.preventDefault();

    // Update content of textarea(s) handled by CKEditor
    for ( instance in CKEDITOR.instances ) {
        CKEDITOR.instances[instance].updateElement();
    }

    var $form = $(this),
        url = $form.attr('action');
    $.post(url,
      {
          section: sectionKey,
          text: $form.find('#seqDiscussionPost').val()
      },
      function (data) {
          if (data.charAt(0) == 'E') {
              bootbox.alert(data);
          } else {
              location.reload();
          }
      }
    );
});
