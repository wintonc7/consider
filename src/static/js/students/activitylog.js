/**
 * Created by Alan on 3/5/2017.
 */
$(document).ready(function() {
    $('#course-select').change(filterCourses);
    $('#assignment-select').change(filterAssignments);
    sortActivity();
});

function filterCourses() {
    selectedCourse = $('#course-select')[0].value;
    logRows = $('.log-row');
    for (i = 0; i < logRows.length; i++) {
        // Check selected course
        if (selectedCourse == "DEFAULT") {
            $('#assignment-select')[0].disabled = true;
            $('#assignment-select')[0].value = "DEFAULT";
            $(logRows[i]).css("display", "table-row");
        } else if (logRows[i].hasChildNodes() && logRows[i].children[1].innerHTML == selectedCourse) {
            $('#assignment-select')[0].disabled = false;
            $(logRows[i]).css("display", "table-row");
        } else {
            $(logRows[i]).css("display", "none");
        }
    }
    sortActivity();
}

function filterAssignments() {
    selectedAssignment = $('#assignment-select')[0].value;
    logRows = $('.log-row');
    for (i = 0; i < logRows.length; i++) {
        console.log(selectedAssignment + " = " + logRows[i].children[2].innerText);
        if (selectedAssignment == "DEFAULT" || (logRows[i].hasChildNodes() && logRows[i].children[2].innerText.trim() == selectedAssignment)) {
            $(logRows[i]).css("display", "table-row");
        } else {
            $(logRows[i]).css("display", "none");
        }
    }
    sortActivity();
}

function sortActivity() {
    // f is a placeholder for the ascending/descending selection
    f = -1;
    logRows = $('.log-row');
    logRows.sort(function(a, b) {
        A = a.children[0].innerText;
        B = b.children[0].innerText;
        if (A < B) {
            return -1 * f;
        } else if (A > B) {
            return 1 * f;
        } else {
            return 0;
        }
    });

    $.each(logRows, function(index, row) {
        $('#activity-table').children('tbody').append(row);
    })
}