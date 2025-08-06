// app/static/js/previews/parent_preview.js

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

    // --- Parent Section Preview ---
    syncInputToPreview('name', 'preview-parent-name');
    syncInputToPreview('breed', 'preview-parent-breed');
    // The description for a parent can contain multiple paragraphs, so we use 'innerHTML'.
    syncInputToPreview('description', 'preview-parent-description', 'innerHTML');
});