function addInstructor() {
    console.log('In addInstructor');
    var email = $("#textEmail").val();
    console.log('Email = ' + email);
    $.post("/admin", {email: email, action: 'add'}, function (data) {
        bootbox.alert(data, function () {
            location.reload();
        });
    });
}

function toggleStatus(instructor) {
    bootbox.confirm("Toggle status of : " + instructor + "?", function (result) {
        if (result) {
            // do the POST and get the callback
            $.post("/admin",
              {
                email: instructor,
                action: 'toggle'
              },
              function (data) {
                bootbox.alert(data, function () {
                    location.reload();
                });
            });
        }
    });
}
