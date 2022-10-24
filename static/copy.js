function Copy() {
    // Get the text from the id generate
    var copyText = document.getElementById("generate");
    // Copy the text
    copyText.select();
    // Put the text to the clipboard
    navigator.clipboard.writeText(copyText.value);
}