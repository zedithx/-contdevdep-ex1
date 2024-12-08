function sendRequest() {
    fetch('/request')
        .then(response => response.text())
        .then(data => {
            document.getElementById('response').value = data;
        });
}

function stopContainers() {
    fetch('/state', {
        method: 'PUT',
        headers: {
            'Content-Type': 'text/plain'
        },
        body: 'SHUTDOWN'
    })
    .then(() => alert('System is stopping.'));
}