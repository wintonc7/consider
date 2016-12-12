var students = $('#show-responses').data().students;
var rounds = $('#show-responses').data().rounds;
var num_std = $('#show-responses').data().std;

$('#courseSelector').on('change', function () {
    location.href = "/show_responses?course=" + this.value;
});

$('#sectionSelector').on('change', function () {
    location.href = "/show_responses?course={{selectedCourse}}&section=" + this.value;
});

function getIndicesOf(searchStr, str, caseSensitive) {
    var searchStrLen = searchStr.length;
    if (searchStrLen == 0) {
        return [];
    }
    var startIndex = 0, index, indices = [];
    if (!caseSensitive) {
        str = str.toLowerCase();
        searchStr = searchStr.toLowerCase();
    }
    while ((index = str.indexOf(searchStr, startIndex)) > -1) {
        indices.push(index);
        startIndex = index + searchStrLen;
    }
    return indices;
}

function SelectAll() {
  if (rounds > 0 && students.length > 0 && num_std > 0)
  {
    var count = 0;
    var emails = [];

    var indicesOfEmailStart = getIndicesOf("email=u", students);
    for (var i = 0; i < indicesOfEmailStart.length; i++)
    {
      var indicesOfEmailEnd = students.indexOf("'", indicesOfEmailStart[i] + 8);
      emails.push(students.substring(indicesOfEmailStart[i] + 8, indicesOfEmailEnd))
    }

    for (var i = 0; i < emails.length; i++)
    {
      for (var j = 1; j <= rounds; j++)
      {
        if (document.getElementById(emails[i].concat(j)).checked) {
            count++;
        }
      }
    }

    if (count != num_std * rounds)
    {
      for (var i = 0; i < emails.length; i++)
      {
        for (var j = 1; j <= rounds; j++)
        {
          document.getElementById(emails[i].concat(j)).checked = true;
        }
      }
    }
    else
    {
      for (var i = 0; i < emails.length; i++)
      {
        for (var j = 1; j <= rounds; j++)
        {
          document.getElementById(emails[i].concat(j)).checked = false;
        }
      }
    }
  }
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

function exportData(course, section) {
    var students = $('#show-responses').data().students;
    var indicesOfEmailStart = getIndicesOf("email=u", students);
    emails = [];
    for (var i = 0; i < indicesOfEmailStart.length; i++)
    {
      var indicesOfEmailEnd = students.indexOf("'", indicesOfEmailStart[i] + 8);
      emails.push(students.substring(indicesOfEmailStart[i] + 8, indicesOfEmailEnd))
    }
    // Gather student emails
    var selector = "";
    var i=0;
    if (rounds > 0 && students.length > 0)
    {
      for (var k = 0; k < emails.length; k++)
      {
          for (var j=1; j<= rounds; j++) {
              if(document.getElementById(emails[k].concat(j)).checked){
                  //var num=i*{{ rounds }}+j;
                  //console.log(num);
                  selector = selector.concat((i.toString()+' ').concat(j.toString()+' '))+' ';
              }
          }
          i=i+1;
      }
    }
    $.post("/data_file_export", {course: course, section: section, action:selector}, function (data) {
        if (data.charAt(0) == 'E') {
            bootbox.alert(data.substring(1));
        }
        else {
            location.href = "/data_file_export"
        }
    });
}

function exportHtml(course, section) {
  var students = $('#show-responses').data().students;
  var indicesOfEmailStart = getIndicesOf("email=u", students);
  emails = [];
  for (var i = 0; i < indicesOfEmailStart.length; i++)
  {
    var indicesOfEmailEnd = students.indexOf("'", indicesOfEmailStart[i] + 8);
    emails.push(students.substring(indicesOfEmailStart[i] + 8, indicesOfEmailEnd))
  }
  // Gather student emails

    var selector = "";
    var i=0;
    if (rounds > 0 && students.length > 0)
    {
      for (var k = 0; k < emails.length; k++)
      {
        for (var j=1; j<= rounds; j++) {
            var id="{{ student.email}}";
            if(document.getElementById(emails[k].concat(j)).checked){
                //var num=i*{{ rounds }}+j;
                //console.log(num);
                selector=selector.concat((i.toString()+' ').concat(j.toString()+' '))+' ';
            }
        }
        i=i+1;
      }
    }
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

function ColChecked(index) {
  var students = $('#show-responses').data().students;
  var indicesOfEmailStart = getIndicesOf("email=u", students);
  emails = [];
  for (var i = 0; i < indicesOfEmailStart.length; i++)
  {
    var indicesOfEmailEnd = students.indexOf("'", indicesOfEmailStart[i] + 8);
    emails.push(students.substring(indicesOfEmailStart[i] + 8, indicesOfEmailEnd))
  }
  // Gather student emails

  if (num_std > 0 && emails.length > 0)
  {
    var count=0;
    for (var k = 0; k < emails.length; k++)
    {
        if(document.getElementById(emails[k].concat(index)).checked)
        {
          count++;
        }
    }
    if(count != num_std){
      for (var k = 0; k < emails.length; k++)
      {
        document.getElementById(emails[k].concat(index)).checked=true;
      }
    }

    else{
      for (var k = 0; k < emails.length; k++)
      {
      document.getElementById(emails[k].concat(index)).checked=false;
      }
    }
  }
}
