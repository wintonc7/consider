var selectedCourse = $('#rounds').data().course;

$('#courseSelector').on('change', function () {
        location.href = "/rounds?course=" + this.value;
});
$('#sectionSelector').on('change', function () {
    location.href = "/rounds?course=" + selectedCourse + "&section=" + this.value;
});
