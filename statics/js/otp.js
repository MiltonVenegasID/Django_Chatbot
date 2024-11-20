function moveFocus(currentField, nextFieldId) {
    if (currentField.value.length === currentField.maxLength) {
        document.getElementById(nextFieldId).focus();
    }
}