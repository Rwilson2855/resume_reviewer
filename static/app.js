document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.querySelector('#file');
    const reviewButton = document.querySelector('#submit');
    const results = document.querySelector('#results');
    const downloadLink = document.querySelector('#download-link');

    reviewButton.addEventListener('click', async function(e) {
        e.preventDefault();
        if (fileInput.files.length === 0) {
            results.innerHTML = "<span style='color:red;'>Please select a PDF resume to upload.</span>";
            return;
        }
        reviewButton.disabled = true;
        results.innerHTML = "Reviewing your resume...";
        downloadLink.style.display = 'none';
        downloadLink.href = "#";

        let formData = new FormData();
        formData.append('file', fileInput.files[0]);
        try {
            let resp = await fetch('/review', {
                method: 'POST',
                body: formData
            });
            if (!resp.ok) {
                throw new Error("Server error");
            }
            let json = await resp.json();
            let result = marked.parse(json.review);
            results.innerHTML = result;
            if (json.pdf_url) {
                downloadLink.href = json.pdf_url;
                downloadLink.style.display = 'inline-block';
            }
        } catch (err) {
            results.innerHTML = "<span style='color:red;'>An error occurred. Please try again.</span>";
        }
        reviewButton.disabled = false;
    });
});
