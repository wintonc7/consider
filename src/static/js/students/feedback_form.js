$(document).ready(function() {

  $("#feedback").submit(formSubmit);

  function formSubmit(event) {

  }

  function CheckTag(val){
        var element = getElementById('othertag');
        if(val=="other")
            element.style.display='block';
        else
            element.style.display='none';
  }
});
