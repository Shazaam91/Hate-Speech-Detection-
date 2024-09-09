console.log('popup.js is loaded');

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('checkButton').addEventListener('click', function () {
        const text = document.getElementById('inputText').value.trim();

        if (!text) {
            document.getElementById('result').innerHTML = '<p>Please enter some text to analyze.</p>';
            return;
        }

        fetch('http://127.0.0.1:5000/analyze_text', { // Make sure the URL matches your backend endpoint
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: new URLSearchParams({
                'text': text
            })
        })
        .then(response => {
            if (response.status === 401) {
                // If the user is not logged in, show a login prompt
                document.getElementById('result').innerHTML = '<p>You need to log in to analyze the text. Please log in and try again.</p>';
                throw new Error('Unauthorized access.');
            } else if (!response.ok) {
                // Handle other non-OK responses
                return response.text().then(text => { throw new Error(text); });
            }
            return response.json();
        })
        .then(data => {
            const resultDiv = document.getElementById('result');
            if (data && typeof data === 'object') {
                const { text, label, confidence } = data;
                resultDiv.innerHTML = `
                    <p><strong>Text:</strong> ${text}</p>
                    <p><strong>Label:</strong> ${label}</p>
                    <p><strong>Confidence:</strong> ${(confidence * 100).toFixed(2)}%</p>
                `;
            } else {
                resultDiv.innerHTML = '<p>No results found.</p>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            if (error.message !== 'Unauthorized access.') {
                document.getElementById('result').innerHTML = '<p>Failed to analyze text. Please try again later.</p>';
            }
        });
    });
});
