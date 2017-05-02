function idFor(label, part) {
	return 'id_' + label + '-' + part
}

function getValueElement(label) {
	return document.getElementById(idFor(label, 'value'))
}

function getNegativeAnswersElement(label) {
	return document.getElementById(idFor(label, 'negatives'))
}

function isSelectedAnswerNegative(label) {
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
		//console.log('Displaying ' + element.id)
		element.style.display = 'block'
	})
}

function hideSubtree(label) {
	iterateSubtreeElements(label, function(element) {
		//console.log('Hiding ' + element.id)
		element.style.display = 'none'
	})
}

function hideSubtreeIfChoiceIsNegative(label) {
	if (isSelectedAnswerNegative(label)) {
		hideSubtree(label)
	} else {
		showSubtree(label)
	}
}

function hideSubtreesForNegativeChoices() {
	iterateAnswers(function(answer) {
		var label = answer.id
		hideSubtreeIfChoiceIsNegative(label)
	})
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
		valueElem.setAttribute('onchange', "hideSubtreeIfChoiceIsNegative('" + label + "')")
	})
}

hideSubtreesForNegativeChoices()
installOnchangeListeners()
