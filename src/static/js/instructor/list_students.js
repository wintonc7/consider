var selectedCourse = $('#list-students').data().course;
var selectedSection = $('#list-students').data().section;

$('#courseSelector').on('change', function () {
    location.href = "/students?course=" + this.value;
});

$('#sectionSelector').on('change', function () {
    location.href = "/students?course=" + selectedCourse + "&section=" + this.value;
});

function addStudents() {
    $("#myModal").modal('show');
}

function submitStudents() {
    $("#modalForm").find('[type="submit"]').trigger('click');
}

$("#modalForm").submit(function (event) {
    //Prevent the default behaviour
    event.preventDefault();

    //collect form elements
    var $form = $(this),
            email = $form.find("input[name='email']").val(),
            course = selectedCourse,
            section = selectedSection,
            url = $form.attr("action");

    var emails = email.replace(/ /g, ',').split(/[\n,]+/);
    // Allows emails to be space, comma, and newline separated
    
    bootbox.confirm("Are you sure, you want to add " + emails.length + " student(s)?", function (result) {
        if (result) {
            // do the POST and get the callback
            $.post(url, {
                emails: JSON.stringify(emails),
                course: course,
                section: section,
                action: 'add'
            }, function (data) {
                if (data.charAt(0) == 'E') {
                    bootbox.alert(data.substring(1));
                }
                else {
                    location.reload();
                }
            });
        }
    });
});

function deleteStudent(student) {
    bootbox.confirm("Are you sure, you want to remove student: " + student + "?", function (result) {
        if (result) {
            // do the POST and get the callback
            $.post("/students", {
                email: student,
                course: selectedCourse,
                section: selectedSection,
                action: 'remove'
            }, function (data) {
                if (data.charAt(0) == 'E') {
                    bootbox.alert(data.substring(1));
                }
                else {
                    location.reload();
                }
            });
        }
    });
}
