$(document).ready(function() {

  $("#feedback").submit(formSubmit);

  function formSubmit(event) {

  }

  function checktag(tag){
        if(tag==="other"){
            document.getElementById('othertag').style.display='block';
        }
        else{
            document.getElementById('othertag').style.display='none';
        }
  }
});
