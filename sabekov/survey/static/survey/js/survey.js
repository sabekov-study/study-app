function idFor(label, part) {
	return 'id_' + label + '-' + part
}

function getValueElement(label) {
	return document.getElementById(idFor(label, 'value'))
}

function getNegativeAnswersElement(label) {
	return document.getElementById(idFor(label, 'negatives'))
}

function isSubtreeInactive(label) {
	var valueElem = getValueElement(label)
	if (!valueElem) {
		console.warn("No value element for " + label)
		return false
	}
	if (valueElem.tagName != 'SELECT') {
		console.warn("Unhandled tag type of value element for " + label + ": " + valueElem.tagName)
		return false
	}
	var choices = valueElem.selectedOptions
	if (choices.length != 1) {
		console.warn("None or multiple choices made for " + label)
		return false
	}
	var choice = choices[0].value

	var negativeAnswersElem = getNegativeAnswersElement(label)
	if (!negativeAnswersElem) {
		console.warn("No negatives found for " + label)
		return false
	}
	var negativeAnswers = JSON.parse(negativeAnswersElem.value)
	return negativeAnswers.indexOf(choice) > -1 || choice == "n.n."
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
		var valueElem = getValueElement(label)
		if (!valueElem) {
			console.warn("No value element for " + label)
			return false
		}
		if (valueElem.tagName != 'SELECT') {
			console.warn("Unhandled tag type of value element for " + label + ": " + valueElem.tagName)
			return false
		}
		valueElem.setAttribute('onchange', "handleAnswerChanged('" + label + "')")
	})
}

function isUnanswered(label) {
	var element = getValueElement(label)

	if (!element) {
		// No specific element by that ID, see if we have multiple values, i.e.,
		// checkboxes

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

	if (element.tagName == 'SELECT') {
		return element.selectedOptions[0].value == 'n.n.'
	}

	if (element.tagName == 'INPUT') {
		if (element.type == 'text') {
			return element.value.trim().length == 0
		}
	}

	// If the element is unknown, exclude it from filtering
	return true
}

function isDiscussionNeeded(label) {
	var element = document.getElementById(idFor(label, 'discussion_needed'))
	return element ? element.checked : false
}

function isRevisionNeeded(label) {
	var element = document.getElementById(idFor(label, 'revision_needed'))
	return element ? element.checked : false
}

function filterIsActive(filter) {
	var element = document.getElementById('id_filter_' + filter)
	return element ? element.checked : false
}

function isFiltered(label) {
	return (filterIsActive('1') && !isUnanswered(label))
		|| (filterIsActive('2') && !isDiscussionNeeded(label))
		|| (filterIsActive('3') && !isRevisionNeeded(label))
}

function applyFilter() {
	hideInactiveSubtrees() // make sure re-activated sub-q are hidden again (see below)
	iterateAnswers(function(element) {
		var label = element.id
		if (isFiltered(label)) {
			element.classList.add('filtered')
		} else {
			// re-activate hidden sub-questions to show changed questions
			// marked for revision
			if (filterIsActive('3') && isRevisionNeeded(label)) {
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
