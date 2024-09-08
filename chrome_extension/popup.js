console.log('popup.js is loaded');

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('checkButton').addEventListener('click', function () {
        const text = document.getElementById('inputText').value.trim();

        if (!text) {
            document.getElementById('result').innerHTML = '<p>Please enter some text to analyze.</p>';
            return;
        }

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
                resultDiv.innerHTML = `
                    <p><strong>Text:</strong> ${text}</p>
                    <p><strong>Label:</strong> ${label}</p>
                    <p><strong>Confidence:</strong> ${confidence.toFixed(2) * 100}%</p>
                `;
            } else {
                resultDiv.innerHTML = '<p>No results found.</p>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('result').innerHTML = '<p>Failed to analyze text. Please try again later.</p>';
        });
    });
});
