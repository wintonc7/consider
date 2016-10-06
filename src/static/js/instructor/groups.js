var selectedCourse = $('#groups').data().course;
var selectedSection = $('#groups').data().section;

$('#courseSelector').on('change', function () {
    location.href = "/groups?course=" + this.value;
});
$('#sectionSelector').on('change', function () {
    location.href = "/groups?course=" + selectedCourse + "&section=" + this.value;
});
$("#form").submit(function (event) {
    //Prevent the default behaviour
    event.preventDefault();
    //collect form elements
    var $form = $(this),
            groups = $form.find("input[name='groups']").val(),
            url = $form.attr("action");
    // do the POST and get the callback
    $.post("/groups", {
        groups: groups,
        course: selectedCourse,
        section: selectedSection,
        action: 'add'
    }, function (data) {
        if (data.charAt(0) == 'E') {
            bootbox.alert(data.substring(1));
        }
        else {
            location.reload();
        }
    });
});
$("#form_table").submit(function (event) {
    //Prevent the default behaviour
    event.preventDefault();
    //collect form elements
    var $form = $(this),
            url = $form.attr("action");
    var data = {};
    $("#group_table > tbody tr").each(function () {
        var stud = $(this).find("td").eq(1).html();
        var group = $("#select_" + $(this).find("td").eq(0).html()).val();
        data[stud] = group;
    });
    data = JSON.stringify(data);
    console.log(data);
    console.log("url = " + url);
    // do the POST and get the callback
    $.post(url, {
        groups: data,
        course: selectedCourse,
        section: selectedSection,
        action: 'update'
    }, function (data) {
        if (data.charAt(0) == 'E') {
            bootbox.alert(data.substring(1));
        }
        else {
            location.reload();
        }
    });
});

$("#form_table2").submit(function (event) {
    //Prevent the default behaviour
    event.preventDefault();
    //collect form elements
    var $form = $(this),
            url = $form.attr("action");
    var data = {};
    $("#group_table2 > tbody tr").each(function () {
        var stud = $(this).find("td").eq(1).html();
        var group = $("#select2_" + $(this).find("td").eq(0).html()).val();
        data[stud] = group;
    });
    data = JSON.stringify(data);
    console.log(data);
    console.log("url = " + url);
    // do the POST and get the callback
    $.post(url, {
        groups: data,
        course: selectedCourse,
        section: selectedSection,
        action: 'update'
    }, function (data) {
        if (data.charAt(0) == 'E') {
            bootbox.alert(data.substring(1));
        }
        else {
            location.reload();
        }
    });
});
