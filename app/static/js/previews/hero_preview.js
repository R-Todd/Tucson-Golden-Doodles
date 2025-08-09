// app/static/js/previews/hero_preview.js

document.addEventListener('DOMContentLoaded', function() {
    // Helper function to link a form input to a preview element
    const syncInputToPreview = (inputId, previewId, attribute = 'textContent') => {
        const inputElement = document.getElementById(inputId);
        const previewElement = document.getElementById(previewId);

        if (inputElement && previewElement) {
            // Set initial preview text on page load
            if (attribute === 'textContent') {
                previewElement.textContent = inputElement.value;
            } else {
                previewElement.innerHTML = inputElement.value;
            }

            // Add event listener to update preview on input
            inputElement.addEventListener('keyup', () => {
                if (attribute === 'textContent') {
                    previewElement.textContent = inputElement.value;
                } else {
                    previewElement.innerHTML = inputElement.value;
                }
            });
        }
    };

    // --- Hero Section Preview ---
    syncInputToPreview('main_title', 'preview-main-title');
    syncInputToPreview('subtitle', 'preview-subtitle');
    syncInputToPreview('description', 'preview-description');
    syncInputToPreview('scroll_text_main', 'preview-scroll-main');
    syncInputToPreview('scroll_text_secondary', 'preview-scroll-secondary');
});