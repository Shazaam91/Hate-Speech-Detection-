console.log('popup.js is loaded');
// popup.js
document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('checkButton').addEventListener('click', function () {
        const text = document.getElementById('inputText').value;
        fetch('http://127.0.0.1:5000/', {
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
            if (response.ok) {
                return response.json();
            } else {
                return response.text().then(text => { throw new Error(text); });
            }
        })
        .then(data => {
            const resultDiv = document.getElementById('result');
            if (data && typeof data === 'object') {
                const { text, label, confidence } = data;
                resultDiv.innerHTML = `<p>Text: ${text}</p><p>Label: ${label}</p><p>Confidence: ${confidence}</p>`;
            } else {
                resultDiv.innerHTML = '<p>No results found.</p>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = '<p>Failed to analyze text. Please try again later.</p>';
        });
    });
});
