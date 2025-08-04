// app/static/js/admin_content_preview.js

document.addEventListener('DOMContentLoaded', function() {
    // --- Helper function to link a form input to a preview element ---
    const syncInputToPreview = (inputId, previewId, attribute = 'textContent') => {
        const inputElement = document.getElementById(inputId);
        const previewElement = document.getElementById(previewId);

        if (inputElement && previewElement) {
            // Set initial preview text on page load
            if (attribute === 'innerHTML') {
                previewElement.innerHTML = inputElement.value;
            } else {
                previewElement.textContent = inputElement.value;
            }

            // Add event listener to update preview on input
            inputElement.addEventListener('keyup', () => {
                if (attribute === 'innerHTML') {
                    previewElement.innerHTML = inputElement.value;
                } else {
                    previewElement.textContent = inputElement.value;
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

    // --- About Section Preview ---
    syncInputToPreview('about_title', 'preview-about-title');
    syncInputToPreview('about_content', 'preview-about-content', 'innerHTML'); // Use innerHTML for HTML content

    // --- Parent Section Preview ---
    syncInputToPreview('name', 'preview-parent-name');
    syncInputToPreview('breed', 'preview-parent-breed');
    syncInputToPreview('description', 'preview-parent-description', 'innerHTML');

});