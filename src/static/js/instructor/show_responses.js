$('#courseSelector').on('change', function () {
    location.href = "/show_responses?course=" + this.value;
});

$('#sectionSelector').on('change', function () {
    location.href = "/show_responses?course={{selectedCourse}}&section=" + this.value;
});

function exportData(course, section) {
    var selector = "";
    var i=0;
    {% if rounds and students %}
    {% for student in students %}
        for (var j=1; j<= {{ rounds }}; j++) {
            var id="{{ student.email}}";
            if(document.getElementById(id.concat(j)).checked){
                //var num=i*{{ rounds }}+j;
                //console.log(num);
                selector=selector.concat((i.toString()+' ').concat(j.toString()+' '))+' ';
            }
        }
        i=i+1;
    {% endfor %}
    {% endif %}
    $.post("/data_file_export", {course: course, section: section, action:selector}, function (data) {
        console.log(123);
        if (data.charAt(0) == 'E') {
            console.log(1234);
            bootbox.alert(data.substring(1));
        }
        else {
            console.log(12345);
            location.href = "/data_file_export"
        }
    });
}

function exportHtml(course, section) {
    var selector = "";
    var i=0;
    {% if rounds and students %}
    {% for student in students %}
        for (var j=1; j<= {{ rounds }}; j++) {
            var id="{{ student.email}}";
            if(document.getElementById(id.concat(j)).checked){
                //var num=i*{{ rounds }}+j;
                //console.log(num);
                selector=selector.concat((i.toString()+' ').concat(j.toString()+' '))+' ';
            }
        }
        i=i+1;
    {% endfor %}
    {% endif %}
    $.post("/data_file_export", {course: course, section: section, action:selector}, function (data) {
        console.log(123);
        if (data.charAt(0) == 'E') {
            console.log(1234);
            bootbox.alert(data.substring(1));
        }
        else {
            console.log(12345);
            location.href = "/data_html_export"
        }
    });
}
function RowChecked(student, rounds) {
        var count=0;
        for (var i=1; i<=rounds; i++){
            if(document.getElementById(student.concat(i)).checked){
                count++;
            }
        }
        if(count!=rounds){
            for (var i=1; i<=rounds; i++){
            document.getElementById(student.concat(i)).checked=true;
        }
        }
        else{
            for (var i=1; i<=rounds; i++){
            document.getElementById(student.concat(i)).checked=false;
        }
        }
}

function ColChecked(index) {
{% if num_std and students %}
        var count=0;
    {% for student in students %}
            var id="{{ student.email}}";
            if(document.getElementById(id.concat(index)).checked){
                count++;
            }
    {% endfor %}
        if(count!={{ num_std }}){
     {% for student in students %}
            var id="{{ student.email}}";
            document.getElementById(id.concat(index)).checked=true;
    {% endfor %}
        }

        else{
     {% for student in students %}
            var id="{{ student.email}}";
            document.getElementById(id.concat(index)).checked=false;
    {% endfor %}
        }
    {% endif %}
}
function SelectAll() {
    {% if rounds and students and num_std%}
        var count=0;
    {% for student in students %}
            var id="{{ student.email}}";
        for (var i=1; i<={{ rounds }}; i++) {
            if (document.getElementById(id.concat(i)).checked) {
                count++;
            }
        }
    {% endfor %}
        var a={{ num_std }};
        var b={{ rounds }};
        if(count!= a*b ){
     {% for student in students %}
            var id="{{ student.email}}";
         for (var i=1; i<={{ rounds }}; i++) {
             document.getElementById(id.concat(i)).checked = true;
         }
    {% endfor %}
        }

        else{
     {% for student in students %}
            var id="{{ student.email}}";
         for (var i=1; i<={{ rounds }}; i++) {
             document.getElementById(id.concat(i)).checked = false;
         }
    {% endfor %}
        }
    {% endif %}
}
