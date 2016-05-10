/**
 * Bind jquery handlers
 */
var lastQuestion = false;
$(document).ready(function() {
    $('#inputLeadInQuestion').on('keyup', function() {
        showPreviewLeadIn();
    });

    $('#inputSummaryQuestion').on('keyup', function() {
        showPreviewSummary();
    });

    $(".dateTimePicker").on('mousedown', function() {
        $(this).datetimepicker();
    });

    $('#addLeadIn').click(function() {
        $('#leadInModal').modal('show');
    });

    $('#addSummary').click(function() {
        $('#summaryModal').modal('show');
    });

    $('#submitSummaryQuestion').click(function() {
        $("#summaryModalForm").find('[type="submit"]').trigger('click');
    });

    $('#submitEditDiscussion').click(function() {
        $("#editDiscussionForm").find('[type="submit"]').trigger('click');
    });

    $('#submitEmail').click(function() {
        $("#editEmailForm").find('[type="submit"]').trigger('click');
    });

    $('.close').click(function() {
        $(this).parent().hide();
    });

    $('#summaryModalForm').submit(function(event) {
        event.preventDefault();
        // First we need to check that a date has been selected
        var $form = $(this),
            question = $form.find("textarea").val(),
            options = $form.find("select").val(),
            url = $form.attr("action");

        var optionVals = [];
        for (var i = 1; i <= options; i++) {
            var val = $form.find("#inputSummaryOptions" + i).val();
            console.log(val);
            optionVals.push(val);
        }

        optionVals = JSON.stringify(optionVals);

        var time_val = moment($form.find("#endTime").val()).format("YYYY-MM-DD[T]HH:mm");

        $.post(url, {
            time: time_val,
            question: question,
            number: options,
            options: optionVals,
            course: $form.find('[name="course"]').val(),
            section: $form.find('[name="section"]').val(),
            round: $form.find('[name="nextRound"]').val(),
            roundType: 'summary',
            action: 'add'
        }, function(data) {
            if (data.charAt(0) == 'E') {
                bootbox.alert(data.substring(1));
            } else {
                bootbox.alert(data.substring(1), function() {
                    location.reload();
                });
            }
        });
    });

    $('#submitLeadInQuestion').click(function() {
        $("#leadInModalForm").find('[type="submit"]').trigger('click');
    });


    $('#leadInModalForm').submit(function(event) {
        event.preventDefault();
        // First we need to check that a date has been selected
        var $form = $(this),
            startBuffer = $form.find('#startBuffer').val(),
            question = $form.find("textarea").val(),
            options = $form.find("select").val(),
            url = $form.attr("action");

        var optionVals = [];
        for (var i = 1; i <= options; i++) {
            var val = $form.find("#inputLeadInOptions" + i).val();
            console.log(val);
            optionVals.push(val);
        }
        optionVals = JSON.stringify(optionVals);

        var time_val = moment($form.find("#endTime").val()).format("YYYY-MM-DD[T]HH:mm");

        $.post(url, {
            time: time_val,
            question: question,
            number: options,
            options: optionVals,
            course: $form.find('[name="course"]').val(),
            section: $form.find('[name="section"]').val(),
            round: 1,
            roundType: 'leadin',
            action: 'add',
            startBuffer: startBuffer
        }, function(data) {
            if (data.charAt(0) == 'E') {
                bootbox.alert(data.substring(1));
            } else {
                bootbox.alert(data.substring(1), function() {
                    location.reload();
                });
            }
        });
    });

    $("#inputSummaryOptions").change(function() {
        var $form = $('#summaryModalForm');
        var select = parseInt($('#inputSummaryOptions').val(), 10);
        var current_num = $form.find('.theOptions').find('input').length;
        var $container = $form.find('.theOptions');

        //Add to end
        if (current_num < select) {
            for (var i = current_num; i < select; i++) {
                var input = $('<input type="text" onkeyup="showPreviewSummary()" class="form-control" id="inputSummaryOptions' + (i + 1) + '" name="Options' + (i + 1) + '" placeholder="Option ' + (i + 1) + '" style="margin-bottom: 10px" required="true">');
                $container.append(input).find('input:last-child').hide().fadeIn('slow');
            }
        }

        //Remove from end
        if (current_num > select) {
            while (current_num > select) {
                $container.find('input:last-child').remove();
                current_num--;
            }
        }

        showPreviewSummary();
    });

    $("#inputLeadInOptions").change(function() {
        var $form = $('#leadInModalForm');
        var select = parseInt($('#inputLeadInOptions').val(), 10);
        var current_num = $form.find('.theOptions').find('input').length;
        var $container = $form.find('.theOptions');

        //Add to end
        if (current_num < select) {
            for (var i = current_num; i < select; i++) {
                var input = $('<input type="text" onkeyup="showPreviewLeadIn()" class="form-control" id="inputLeadInOptions' + (i + 1) + '" name="Options' + (i + 1) + '" placeholder="Option ' + (i + 1) + '" style="margin-bottom: 10px" required="true">');
                $container.append(input).find('input:last-child').hide().fadeIn('slow');
            }
        }

        //Remove from end
        if (current_num > select) {
            while (current_num > select) {
                $container.find('input:last-child').remove();
                current_num--;
            }
        }

        showPreviewLeadIn();
    });

    $('#addRoundsForm').submit(function(e) {
        e.preventDefault();

        var $form = $(this),
            total_discussions = $('#total_discussions').val(),
            duration = $('#duration').val(),
            course = $form.find('[name="course"]').val(),
            section = $form.find('[name="section"]').val(),
            num = $('#total_discussions').val(),
            action = "add_disc";

        //Logic to add new discussion round to UI
        var $duration_error = $('#duration_error');
        var $total_discussions_error = $('#total_dis_error');

        var errors = { 'duration': [], 'total_discussions': [] };

        //Validate number
        if (!validateNumberInput(total_discussions)) {
            errors.total_discussions.push('Total Discussions must be a valid number');
        }

        //Populate validation errors
        if (errors.total_discussions.length > 0) {
            var _error_text = "";
            for (var i = 0; i < errors.total_discussions.length; i++) {
                _error_text += errors.total_discussions[i];
                if (i - 1 != errors.total_discussions.length)
                    _error_text += '<br><br>';
            }
            $total_discussions_error.find('strong').html(_error_text);
            $total_discussions_error.show();
        }

        //Validate number
        if (!validateNumberInput(duration)) {
            errors.duration.push('Duration must be a valid number');
        }

        if (errors.duration.length > 0) {
            var _error_text = "";
            for (var i = 0; i < errors.duration.length; i++) {
                _error_text += errors.duration[i];
                if (i - 1 != errors.duration.length)
                    _error_text += '<br><br>';
            }
            $duration_error.find('strong').html(_error_text);
            $duration_error.show();
        }

        if (errors.duration.length + errors.total_discussions.length > 0)
            return false;


        //Add new rounds on the server side
        $.ajax({
            url: '/rounds',
            method: 'POST',
            data: {
                total_discussions: total_discussions,
                duration: duration,
                course: course,
                section: section,
                action: action,
                total_discussions: num
            },
            success: function(res) {
                //do stuff with res
                console.log(res);
                //addRoundRows(res);
                location.reload();
            },
            error: function(xhr, status, error) {
                console.log(status);
            }
        });
    });

    $('.edit-round').click(function() {
        var modal = $('#editDiscussionModal');
        var self = $(this);

        //get values
        var description = self.closest('td').siblings('.round_description').find('input').val();
        var deadline = self.closest('td').siblings('.round_deadline').find('input').val();
        var start = self.closest('td').siblings('.round_starttime').find('input').val();
        var id = self.closest('tr').attr('id').split('_')[1];

        //populate fields with this rounds data
        modal.find('#discussionStartTime').val(moment(start).format("MM/DD/YYYY hh:mm A"));
        modal.find('#discussionEndTime').val(moment(deadline).format("MM/DD/YYYY hh:mm A"));

        modal.find('#inputEditDiscussionDescription').val(description);
        modal.find('[name="round_id"]').val(id);

        //show modal
        modal.modal('show');
    });

    $('#edit-leadin').click(function() {
        var modal = $('#leadInModal');
        var table = $('#leadin-question-table');
        var tr = $(this).find('tbody > tr');
        var deadline = table.find('td:nth-child(2)').data('deadline');
        var question = table.find('.question').text();
        var options_ul = table.find('.options ul');
        var inputOptions = modal.find('#inputLeadInOptions');
        inputOptions.val(options_ul.find('li').length);

        modal.find('#endTime').val(moment(deadline).format("MM/DD/YYYY hh:mm A"));
        modal.find('textarea').val(question);

        showPreviewLeadIn();

        modal.modal('show');
    });

    $('#edit-summary').click(function() {
        var modal = $('#summaryModal');
        var table = $('#summary-question-table');
        var tr = $(this).find('tbody > tr');
        var deadline = table.find('td:nth-child(2)').data('deadline');
        var question = table.find('.question').text();
        var options_ul = table.find('.options ul');
        var inputOptions = modal.find('#inputSummaryOptions');

        inputOptions.val(options_ul.find('li').length);

        modal.find('#endTime').val(moment(deadline).format("MM/DD/YYYY hh:mm A"));
        modal.find('textarea').val(question);

        showPreviewSummary();

        modal.modal('show');
    });

    $('.remove-round').click(function(e) {
        var round_key = $(this).data('round-key'),
            course = $(this).data('course'),
            section = $(this).data('section');

        console.log('Trying to remove round: ' + round_key);

        //Remove the round on the server side
        $.ajax({
            url: '/rounds',
            method: 'POST',
            data: {
                course: course,
                section: section,
                round_id: round_key,
                action: 'delete'
            },
            success: function(res) {
                console.log(res);
                location.reload();
            },
            error: function(xhr, status, error) {
                console.log(error);
            }
        });
    });

    $('#editEmailForm').submit(function(e) {
        e.preventDefault();

        var course = $(this).find('[name="course"]').val(),
            section = $(this).find('[name="section"]').val(),
            subject = $(this).find('[name="subject"]').val(),
            message = $(this).find('[name="message"]').val();


        $.post('/rounds', {
            course: course,
            section: section,
            message: message,
            subject: subject,
            action: 'start'
        }, function(data) {
            if (data.charAt(0) == 'E') {
                bootbox.alert(data.substring(1));
            } else {
                bootbox.alert(data.substring(1), function() {
                    location.reload();
                });
            }
        });
    });

    //Submit discussion edit to server
    $("#editDiscussionForm").submit(function(event) {
        //Prevent the default behaviour
        event.preventDefault();

        //collect form elements
        var $form = $(this),
            description = $form.find("textarea").val(),
            url = $form.attr("action"),
            start_time = moment($form.find('#discussionStartTime').val()).format("YYYY-MM-DD[T]HH:mm"),
            deadline = moment($form.find('#discussionEndTime').val()).format("YYYY-MM-DD[T]HH:mm"),
            round = $form.find('[name="round_id"]').val();

        // do the POST and get the callback
        $.post(url, {
            round_id: round,
            description: description,
            course: $form.find('[name="course"]').val(),
            section: $form.find('[name="section"]').val(),
            roundType: 'discussion',
            action: 'change',
            deadline: deadline,
            start_time: start_time
        }, function(data) {
            if (data.charAt(0) == 'E') {
                bootbox.alert(data.substring(1));
            } else {
                bootbox.alert(data.substring(1), function() {
                    location.reload();
                });
            }
        });
    });
});

(function() {
    mds = document.getElementsByClassName('md');
    console.log('mds = ' + mds.length);
    for (var i = 0; i < mds.length; i++) {
        text = mds[i].innerHTML;
        mds[i].innerHTML = mdToHtml(text);
    }
})();

//Utility methods
function validateNumberInput(val) {
    return parseInt(val);
}

function mdToHtml(text) {
    var converter = new showdown.Converter();
    return converter.makeHtml(text);
}

function showPreviewSummary() {
    var text = $('#inputSummaryQuestion').val();
    var $form = $('#summaryModalForm');
    var questionOptions = $form.find('.theOptions').find('input');

    console.log('questionOptions.length = ' + questionOptions.length);

    questionOptions.each(function(i, el) {
        text = text + '<br>\r\n' + (i + 1) + '. ' + $(el).val();
    });

    console.log('text = ' + text);
    preview = mdToHtml(text);
    $('#summaryModal').find('#previewPlaceholder').html(preview);
}

function showPreviewLeadIn() {
    var text = $('#inputLeadInQuestion').val();
    var $form = $('#leadInModalForm');
    var questionOptions = $form.find('.theOptions').find('input');

    console.log('questionOptions.length = ' + questionOptions.length);

    questionOptions.each(function(i, el) {
        text = text + '<br>\r\n' + (i + 1) + '. ' + $(el).val();
    });

    console.log('text = ' + text);
    preview = mdToHtml(text);
    $('#leadInModal').find('#previewPlaceholder').html(preview);
}
