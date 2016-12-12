var selectedCourse = $('#responses').data().course;

$('#courseSelector').on('change', function () {
    location.href = "/responses?course=" + this.value;
});

$('#sectionSelector').on('change', function () {
    location.href = "/responses?course=" + selectedCourse + "&section=" + this.value;
});
