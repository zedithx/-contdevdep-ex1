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
    .then(response => {
        if (response.ok) {
            alert('System is stopping.');
        } else {
            alert('Failed to stop the system. Please try again.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while trying to stop the system.');
    });
}