{%- if option -%}
    $("#{{option}}").prop("checked",true);
{%- endif -%}

{% if not expired -%}
    var radio, comment, summary;

    function formSubmit(event){
        //Prevent the default behaviour
        event.preventDefault();

        // Update content of textarea(s) handled by CKEditor
        for (instance in CKEDITOR.instances) {
            CKEDITOR.instances[instance].updateElement();
        }

        //collect form elements
        var $form = $(this);

        if (document.getElementsByClassName('optionsRadios').length > 0
                && $form.find("input:radio[name='optionsRadios']:checked").val() === undefined) {
            bootbox.alert("Please select one of the options");
        } else {
            radio = $form.find("input:radio[name='optionsRadios']:checked").val();

            comment = $form.find("#comment").val();
            var url = $form.attr("action");
            console.log("option = " + radio + ", comment = " + comment + ", url = " + url);

            {%- if last_round -%}
                summary = $form.find("#summary").val();
            {%- else -%}
                summary = '';
            {%- endif -%}


            $.post(url,{option:radio, comm:comment, summary:summary, section:'{{sectionKey}}'},function (data) {
                bootbox.alert(data,function(){
                    ocomment = comment;
                });
            });
        }
    }

  $("#form").submit(formSubmit);

    var ocomment = $("#comment").val();

    $(window).bind('beforeunload', function() {
        if ($('#comment').val() !== ocomment) {
            return "It looks like you have input you haven't submitted.";
        }
    });
 {%- endif -%} // not expired
