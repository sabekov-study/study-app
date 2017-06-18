function getEvalForm() {
	return document.getElementById('eval-form')
}

function idFor(label, part) {
	return 'id_' + label + '-' + part
}

function getValueElement(label) {
	var form = getEvalForm()
	return form.elements.namedItem(label + '-value')
}

function getNegativeAnswersElement(label) {
	return document.getElementById(idFor(label, 'negatives'))
}

function isSubtreeInactive(label) {
	var element = getValueElement(label)
	if (!element) {
		console.error("No value element for '" + label + "'")
		return false
	}
	var value = element.value
	if (!value) {
		return false
	}

	var negativeAnswersElem = getNegativeAnswersElement(label)
	if (!negativeAnswersElem) {
		console.warn("No negatives found for " + label)
		return false
	}
	var negativeAnswers = JSON.parse(negativeAnswersElem.value)
	return negativeAnswers.indexOf(value) > -1 || value == "n.n."
}

function iterateAnswers(callback) {
	var answers = document.getElementsByClassName('answer')
	for (var i = 0; i < answers.length; i++) {
		var answer = answers[i]
		callback(answer)
	}
}

function getSubtreeElements(label) {
	return document.getElementsByClassName('child-of-' + label)
}

function iterateSubtreeElements(label, callback) {
	var elements = getSubtreeElements(label)
	for (var i = 0; i < elements.length; i++) {
		var element = elements[i]
		callback(element)
	}
}

function showSubtree(label) {
	iterateSubtreeElements(label, function(element) {
		element.classList.remove('inactive')
	})
}

function hideSubtree(label) {
	iterateSubtreeElements(label, function(element) {
		element.classList.add('inactive')
	})
}

function updateSubtreeVisibility(label) {
	if (isSubtreeInactive(label)) {
		hideSubtree(label)
	} else {
		showSubtree(label)
	}
}

function hideInactiveSubtrees() {
	iterateAnswers(function(answer) {
		var label = answer.id
		updateSubtreeVisibility(label)
	})
}

function handleAnswerChanged(label) {
	updateSubtreeVisibility(label)
}

function installOnchangeListeners() {
	iterateAnswers(function(answer) {
		var label = answer.id
		var elements = document.getElementsByName(label + '-value')
		for (var i = 0; i < elements.length; i++) {
			var element = elements[i]
			element.setAttribute('onchange', "handleAnswerChanged('" + label + "')")
		}
	})
}

function isUnanswered(label) {
	var element = getValueElement(label)
	if (!element) {
		console.error("No value element for '" + label + "'")
		return false
	}
	var value = element.value

	// Collections of checkboxes have to be handled separately
	if (RadioNodeList.prototype.isPrototypeOf(element) && !value) {
		var groupedElements = document.getElementsByName(label + '-value')
		for (var i = 0; i < groupedElements.length; i++) {
			var currentElement = groupedElements[i]
			if (currentElement.tagName == 'INPUT' && currentElement.type == 'checkbox' && currentElement.checked) {
				return false
			}
		}

		// If no answer within a group is given, exclude it from filtering
		return true
	}

	return !value || !value.trim() || value == 'n.n.'
}

function isDiscussionNeeded(label) {
	var element = document.getElementById(idFor(label, 'discussion_needed'))
	return element ? element.checked : false
}

function isRevisionNeeded(label) {
	var element = document.getElementById(idFor(label, 'revision_needed'))
	return element ? element.checked : false
}

function isDirty(label) {
	var element = document.getElementById(idFor(label, 'dirty'))
	return element ? element.checked : false
}

function hasNotes(label) {
	return $('#' + idFor(label, 'note')).val() != ""
}

function filterIsActive(filter) {
	var element = document.getElementById('id_filter_' + filter)
	return element ? element.checked : false
}

function isFiltered(label) {
	return (filterIsActive('1') && !isUnanswered(label))
		|| (filterIsActive('2') && !isDiscussionNeeded(label))
		|| (filterIsActive('3') && !isRevisionNeeded(label))
		|| (filterIsActive('4') && !isDirty(label))
		|| (filterIsActive('5') && !hasNotes(label))
}

function applyFilter() {
	hideInactiveSubtrees() // make sure re-activated sub-q are hidden again (see below)
	iterateAnswers(function(element) {
		var label = element.id
		if (isFiltered(label)) {
			element.classList.add('filtered')
		} else {
			// re-activate hidden sub-questions to show flagged questions
			if ( (filterIsActive('2') && isDiscussionNeeded(label))
					|| (filterIsActive('3') && isRevisionNeeded(label))
					|| (filterIsActive('4') && isDirty(label))
					|| (filterIsActive('5') && hasNotes(label))) {
				element.classList.remove('inactive')
			}
			element.classList.remove('filtered')
		}
	})
}

function ajaxifySubmit() {
	var frm = $('#eval-form');
	frm.submit(function () {
		$.ajax({
			type: frm.attr('method'),
			url: frm.attr('action'),
			data: frm.serialize(),
			success: function (data) {
				bootstrap_alert.success('Successfully saved.');
			},
			error: function(data) {
				console.log(data)
				bootstrap_alert.danger('Saving failed.');
			}
		});
		return false;
	});
}



// https://stackoverflow.com/a/16604526
bootstrap_alert = function() {}
bootstrap_alert.danger = function(message) {
    $('#ajax-messages').append('<div class="alert alert-block alert-danger fade in"><button type="button" class="close" data-dismiss="alert">&times;</button>'+ message +'</div>');
    alertTimeout(10000);
}
bootstrap_alert.success = function(message) {
    $('#ajax-messages').append('<div class="alert alert-block alert-success fade in"><button type="button" class="close" data-dismiss="alert">&times;</button>'+ message +'</div>');
    alertTimeout(10000);
}
function alertTimeout(wait){
    setTimeout(function(){
        $('#ajax-messages').children('.alert:first-child').remove();
    }, wait);
}


hideInactiveSubtrees()
installOnchangeListeners()
ajaxifySubmit()
