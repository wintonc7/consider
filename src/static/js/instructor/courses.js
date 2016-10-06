$("#modalForm").submit(function (event) {
    //Prevent the default behaviour
    event.preventDefault();

    //collect form elements
    var $form = $(this),
            courseName = $('#courseName').val();

    bootbox.confirm("Are you sure, you want to add " + courseName + " ?", function (result) {
        if (result) {
            // do the POST and get the callback
            $.post("/courses", {name: courseName, action:'add'}, function (data) {
                if (data.charAt(0) == 'E') {
                    $("#courseNameContainer").addClass("has-error");
                    $("#courseNameHelpBlock").text(data.substring(1));
                    $("#courseName").focus();
                }
                else {
                    location.reload();
                }
            });
        }
    });
});

$("#sectionModalForm").submit(function (event) {
    //Prevent the default behaviour
    event.preventDefault();

    //collect form elements
    var $form = $(this),
            sectionName = $('#sectionName').val(),
            sectionCourse = $('#sectionCourse').val(),
            url = $form.attr("action");

    bootbox.confirm("Are you sure, you want to add Section: " + sectionName + " to Course: " + sectionCourse + "  ?", function (result) {
        if (result) {
            // do the POST and get the callback
            $.post('/sections', {section: sectionName, course: sectionCourse, action: 'add'}, function (data) {
                if (data.charAt(0) == 'E') {
                    $("#sectionNameContainer").addClass("has-error");
                    $("#sectionNameHelpBlock").text(data.substring(1));
                    $("#sectionName").focus();
                }
                else {
                    location.href = "/home?course=" + sectionCourse;
                }
            });
        }
    });
});

$(document).ready(function () {
    $('#courseName').tooltip({'trigger': 'focus', 'title': 'Course name should be unique'});
    $('#sectionName').tooltip({'trigger': 'focus', 'title': 'Section name should be unique inside a Course'});
});

function submitCourse() {
    $("#modalForm").find('[type="submit"]').trigger('click');
}

function submitSection() {
    $("#sectionModalForm").find('[type="submit"]').trigger('click');
}

function addCourse() {
    $("#myModal").modal('show');
}

$('#myModal').on('shown.bs.modal', function () {
    $('#courseName').focus();
});

$('#sectionModal').on('shown.bs.modal', function () {
    $('#sectionName').focus();
});

function addSection(course) {
    $("#sectionModal").modal('show');
    $("#sectionCourse").val(course);
}

function toggleCourseStatus(course) {
    bootbox.confirm("Toggle status of course: " + course + "?", function (result) {
        if (result) {
            // do the POST and get the callback
            $.post("/courses",
            {
              name: course,
              action:'toggle'
            },
            function () {
              location.href = "/home?course=" + course;
            });
        }
    });
}

function toggleSectionStatus(course, section) {
    bootbox.confirm("Toggle status of: " + section + " in course: " + course + "?", function (result) {
        if (result) {
            // do the POST and get the callback
            $.post("/sections",
            {
              course: course,
              section: section,
              action:'toggle'
            },
            function (data) {
              if (data.charAt(0) == 'E') {
                  bootbox.alert(data.substring(1));
              }
              else {
                  location.href = "/home?course=" + course;
              }
            });
        }
    });
}
