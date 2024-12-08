function sendRequest() {
    fetch('/request')
        .then(response => response.text())
        .then(data => {
            document.getElementById('response').value = data;
        });
}

function stopContainers() {
    fetch('/stop')
        .then(() => alert('System is stopping.'));
}