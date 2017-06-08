function highlightDifferingAnswers() {
    $("table").each(function() {
        var prev = null;
        var differing = false;
        $(this).find('.value').each(function() {
            if (prev != null && prev != $(this).html()) {
                differing = true;
            }
            prev = $(this).html();
        });
        if (differing) {
            $(this).find('.answer').each(function() {
                $(this).addClass('danger');
            });
        }
    });
}

$(document).ready(highlightDifferingAnswers);
