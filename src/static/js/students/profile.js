$(document).ready(function() {

  $("#profile").submit(formSubmit);

  function formSubmit(event) {

      var fname = $('#fname').val();
      var lname = $('#lname').val();
      var preferred_email = $('#preferred_email').val();

      //Prevent the default behaviour
      event.preventDefault();

      //collect form elements
      var $form = $(this);

      var url = $form.attr("action");

      $.post(url, {fname: fname, lname: lname, preferred_email: preferred_email});
  }
});
