// app/static/js/admin_content_preview.js

document.addEventListener('DOMContentLoaded', function() {
    // --- Helper function to link a form input to a preview element ---
    // This function finds an input field and a preview element by their IDs.
    // It sets the initial text and then listens for keyboard input to update the preview in real-time.
    const syncInputToPreview = (inputId, previewId, attribute = 'textContent') => {
        const inputElement = document.getElementById(inputId);
        const previewElement = document.getElementById(previewId);

        if (inputElement && previewElement) {
            // Set the initial preview text when the page loads.
            // Use 'innerHTML' for fields that contain HTML, and 'textContent' for plain text.
            if (attribute === 'innerHTML') {
                previewElement.innerHTML = inputElement.value;
            } else {
                previewElement.textContent = inputElement.value;
            }

            // Add an event listener to update the preview whenever the user types.
            inputElement.addEventListener('keyup', () => {
                if (attribute === 'innerHTML') {
                    previewElement.innerHTML = inputElement.value;
                } else {
                    previewElement.textContent = inputElement.value;
                }
            });
        }
    };

    
    // The previous version of this file was missing the calls for the 'About' and 'Parent' sections.
    // By adding them here, we are activating the live preview for all three admin pages.

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
    // The description for a parent can contain multiple paragraphs, so we use 'innerHTML'.
    syncInputToPreview('description', 'preview-parent-description', 'innerHTML');

});