var selectedCourse = $('#rounds').data().course;

$('#courseSelector').on('change', function () {
        location.href = "/rounds?course=" + this.value;
});
$('#sectionSelector').on('change', function () {
    location.href = "/rounds?course=" + selectedCourse + "&section=" + this.value;
});

// Toggle anonymity status on server
    function toggleAnon(course, section, anon) {
        bootbox.confirm("Toggle Anonymity?", function (result) {
            if (result) {
                console.log("result = " + result);
                $.post("/rounds", {course: course, section: section, action: 'toggle_anon'}, function (data) {
                    if (data.charAt(0) == 'E') {
                        bootbox.alert(data.substring(1));
                    } else {
                        location.href = "/rounds?course=" + course + "&section=" + section;
                    }
                });
            }
        });
    }
    function toggleRounds(course, section) {
        bootbox.confirm("Toggle Rounds-based structure?", function (result) {
            if (result) {
                console.log("result = " + result);
                $.post("/rounds", {
                    course: course,
                    section: section,
                    action: 'toggle_round_structure'
                }, function (data) {
                    if (data.charAt(0) == 'E') {
                        bootbox.alert(data.substring(1));
                    } else {
                        location.href = "/rounds?course=" + course + "&section=" + section;
                    }
                });
            }
        });
    }
