document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.querySelector('#file');
    const reviewButton = document.querySelector('#submit');
    const results = document.querySelector('#results');

    reviewButton.addEventListener('click', async function(e) {
        e.preventDefault();
        if (fileInput.files.length === 0) return;
        reviewButton.disabled = true;
        let formData = new FormData();
        formData.append('file', fileInput.files[0]);
        let resp = await fetch('/review', {
            method: 'POST',
            body: formData
        });
        let json = await resp.json();
        let result = marked.parse(json.review);
        results.innerHTML = result;
        reviewButton.disabled = false;
    });
});