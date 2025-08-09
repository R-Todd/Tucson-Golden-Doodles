// app/static/js/previews/about_preview.js

document.addEventListener('DOMContentLoaded', function() {
    const syncInputToPreview = (inputId, previewId, attribute = 'textContent') => {
        const inputElement = document.getElementById(inputId);
        const previewElement = document.getElementById(previewId);

        if (inputElement && previewElement) {
            if (attribute === 'innerHTML') {
                previewElement.innerHTML = inputElement.value;
            } else {
                previewElement.textContent = inputElement.value;
            }

            inputElement.addEventListener('keyup', () => {
                if (attribute === 'innerHTML') {
                    previewElement.innerHTML = inputElement.value;
                } else {
                    previewElement.textContent = inputElement.value;
                }
            });
        }
    };

    // --- About Section Preview ---
    syncInputToPreview('about_title', 'preview-about-title');
    syncInputToPreview('about_content', 'preview-about-content', 'innerHTML'); // Use innerHTML for HTML content
});