function Copy() {
    // Get the text from the textarea with id generate
    var copyText = document.getElementById("generate");
    // Copy the text
    copyText.select();
    // Put the text to the clipboard
    navigator.clipboard.writeText(copyText.value);
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function drawWinner() {
    entries = document.getElementById("generate").innerHTML.split(/\r?\n/)
    // remove last element as it is always blank due to using new lines for the for loop
    entries.pop()
    for (let count = 0; count < 10; count++) {
        winner = Math.floor(Math.random() * entries.length)
        document.getElementById("winner").innerHTML = entries[winner]
        await sleep(count * 100)
    }
    document.getElementById("winner").innerHTML = "Winner: " + entries[winner]
}