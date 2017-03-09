/**
 * Bind jquery handlers
 */
var lastQuestion = false;
$(document).ready(function () {
    $('#inputInitialQuestion').on('keyup', function () {
        showPreviewInitial();
    });

    $('#inputSummaryQuestion').on('keyup', function () {
        showPreviewSummary();
    });

    $(".dateTimePicker").on('mousedown', function () {
        $(this).datetimepicker();
    });

    $('#addInitial').click(function () {
        $('#initialModal').modal('show');
    });

    $('#addSummary').click(function () {
        $('#summaryModal').modal('show');
    });

    $('#addSequentialDiscussion').click(function () {
        $('#seqDiscussionModal').modal('show');
    });

    $('#editSequentialDiscussion').click(function () {
        var modal = $('#seqDiscussionModal'),
            start_time = $('#startTimeSeq').text(),
            end_time = $('#endTimeSeq').text(),
            description = $('#descriptionSeq').text();
        modal.find('#startTimeSeqDisc').val(moment(start_time).format("MM/DD/YYYY hh:mm A"));
        modal.find('#endTimeSeqDisc').val(moment(end_time).format("MM/DD/YYYY hh:mm A"));
        modal.find('#descriptionSeqDisc').val(description);
        modal.modal('show');
    });

    $('#submitSummaryQuestion').click(function () {
        $("#summaryModalForm").find('[type="submit"]').trigger('click');
    });

    $('#submitEditDiscussion').click(function () {
        $("#editDiscussionForm").find('[type="submit"]').trigger('click');
    });

    $('#submitEmail').click(function () {
        $("#editEmailForm").find('[type="submit"]').trigger('click');
    });

    $('.close').click(function () {
        $(this).parent().hide();
    });

    $('#summaryModalForm').submit(function (event) {
        event.preventDefault();
        // First we need to check that a date has been selected
        var $form = $(this),
            question = $form.find("textarea").val(),
            options = $form.find("select").val(),
            url = $form.attr("action");

        console.log('Question = ' + question);
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
        }, function (data) {
            if (data.charAt(0) == 'E') {
                bootbox.alert(data.substring(1));
            } else {
                bootbox.alert(data.substring(1), function () {
                    location.reload();
                });
            }
        });
    });

    $('#submitInitialQuestion').click(function () {
        $("#initialModalForm").find('[type="submit"]').trigger('click');
    });

    $('#initialModalForm').submit(function (event) {
        event.preventDefault();
        // First we need to check that a date has been selected
        var $form = $(this),
            startBuffer = $form.find('#startBuffer').val(),
            question = $form.find("textarea").val(),
            options = $form.find("select").val(),
            url = $form.attr("action");

        var optionVals = [];
        for (var i = 1; i <= options; i++) {
            var val = $form.find("#inputInitialOptions" + i).val();
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
            roundType: 'initial',
            action: 'add',
            startBuffer: startBuffer
        }, function (data) {
            if (data.charAt(0) == 'E') {
                bootbox.alert(data.substring(1));
            } else {
                bootbox.alert(data.substring(1), function () {
                    location.reload();
                });
            }
        });
    });

    $("#inputSummaryOptions").change(function () {
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

    $("#inputInitialOptions").change(function () {
        var $form = $('#initialModalForm');
        var select = parseInt($('#inputInitialOptions').val(), 10);
        var current_num = $form.find('.theOptions').find('input').length;
        var $container = $form.find('.theOptions');

        //Add to end
        if (current_num < select) {
            for (var i = current_num; i < select; i++) {
                var input = $('<input type="text" onkeyup="showPreviewInitial()" class="form-control" id="inputInitialOptions' + (i + 1) + '" name="Options' + (i + 1) + '" placeholder="Option ' + (i + 1) + '" style="margin-bottom: 10px" required="true">');
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

        showPreviewInitial();
    });

    $('#addRoundsForm').submit(function (e) {
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

        var errors = {'duration': [], 'total_discussions': []};

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
            success: function (res) {
                //do stuff with res
                console.log(res);
                //addRoundRows(res);
                location.reload();
            },
            error: function (xhr, status, error) {
                console.log(status);
            }
        });
    });

    $('.edit-round').click(function () {
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

    $('#edit-initial').click(function () {
        var modal = $('#initialModal');
        var table = $('#initial-question-table');
        var tr = $(this).find('tbody > tr');
        var deadline = table.find('td:nth-child(2)').data('deadline');
        var question = table.find('.question').html();
        var options_ul = table.find('.options ul');
        var inputOptions = modal.find('#inputInitialOptions');
        inputOptions.val(options_ul.find('li').length);

        modal.find('#endTime').val(moment(deadline).format("MM/DD/YYYY hh:mm A"));
        modal.find('textarea').val(question);

        showPreviewInitial();

        modal.modal('show');
    });

    $('#edit-summary').click(function () {
        var modal = $('#summaryModal');
        var table = $('#summary-question-table');
        var tr = $(this).find('tbody > tr');
        var deadline = table.find('td:nth-child(2)').data('deadline');
        var question = table.find('.question').html();
        var options_ul = table.find('.options ul');
        var inputOptions = modal.find('#inputSummaryOptions');

        inputOptions.val(options_ul.find('li').length);

        modal.find('#endTime').val(moment(deadline).format("MM/DD/YYYY hh:mm A"));
        modal.find('textarea').val(question);

        showPreviewSummary();

        modal.modal('show');
    });

    $('.remove-round').click(function (e) {
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
            success: function (res) {
                console.log(res);
                location.reload();
            },
            error: function (xhr, status, error) {
                console.log(error);
            }
        });
    });

    $('#end-current-round').click(function (e) {

        var section = $(this).data('section');
        var course = $(this).data('course');
        console.log('ajax: Trying to end the current round: sending POST');
        //Remove the round on the server side
        $.ajax({
            url: '/rounds',
            method: 'POST',
            data: {
                section: section,
                course: course,
                action: 'end-current-round'
            },
            success: function (res) {
                console.log(res);
                location.reload();
            },
            error: function (xhr, status, error) {
                console.log(error);
            }
        });
    });


    $('#editEmailForm').submit(function (e) {
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
        }, function (data) {
            if (data.charAt(0) == 'E') {
                bootbox.alert(data.substring(1));
            } else {
                bootbox.alert(data.substring(0), function () {
                    location.reload();
                });
            }
        });
    });

    //Submit discussion edit to server
    $("#editDiscussionForm").submit(function (event) {
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
        }, function (data) {
            if (data.charAt(0) == 'E') {
                bootbox.alert(data.substring(1));
            } else {
                bootbox.alert(data.substring(1), function () {
                    location.reload();
                });
            }
        });
    });

    $('#seqDiscussionModalForm').submit(function (event) {
        event.preventDefault();
        var $form = $(this),
            startTime = moment($form.find("#startTimeSeqDisc").val()).format("YYYY-MM-DD[T]HH:mm"),
            endTime = moment($form.find("#endTimeSeqDisc").val()).format("YYYY-MM-DD[T]HH:mm"),
            description = $form.find("#descriptionSeqDisc").val();
        console.log('seqDiscussionModalForm' + '; startTime = ' + startTime);

        $.post($form.attr("action"),
            {
                course: $form.find('[name="course"]').val(),
                section: $form.find('[name="section"]').val(),
                action: 'save_seq_disc',
                start_time: startTime,
                end_time: endTime,
                description: description
            },
            function (data) {
                if (data.charAt(0) == 'E') {
                    bootbox.alert(data);
                } else {
                    location.reload();
                }
            }
        );
    });
});

//Utility methods
function validateNumberInput(val) {
    return parseInt(val);
}

function showPreviewSummary() {
    var text = $('#inputSummaryQuestion').val();
    var $form = $('#summaryModalForm');
    var questionOptions = $form.find('.theOptions').find('input');
    text = text + '\r\n<ol>\r\n';
    questionOptions.each(function (i, el) {
        text = text + '<li>' + $(el).val(); + '</li>\r\n';
    });
    text = text + '</ol>\r\n';

    console.log('text = ' + text);
    $('#summaryModal').find('#previewPlaceholder').html(text);
}

function showPreviewInitial() {
    var text = $('#inputInitialQuestion').val();
    var $form = $('#initialModalForm');
    var questionOptions = $form.find('.theOptions').find('input');
    text = text + '\r\n<ol>\r\n';
    questionOptions.each(function (i, el) {
        text = text + '<li>' + $(el).val(); + '</li>\r\n';
    });
    text = text + '</ol>\r\n';

    console.log('text = ' + text);
    $('#initialModal').find('#previewPlaceholder').html(text);
}

