var selectedCourse = $('#group-responses-selectors').data().course;

$('#courseSelector').on('change', function () {
    location.href = "/group_responses?course=" + this.value;
});
$('#sectionSelector').on('change', function () {
    location.href = "/group_responses?course=" + selectedCourse + "&section=" + this.value;
});
