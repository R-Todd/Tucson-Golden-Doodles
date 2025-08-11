// app/static/js/previews/review_preview.js

document.addEventListener('DOMContentLoaded', function() {
    /**
     * A helper function to synchronize a form input's value with a preview element.
     * @param {string} inputId - The ID of the form input element.
     * @param {string} previewId - The ID of the element to display the preview.
     * @param {string} [attribute='textContent'] - The attribute to update on the preview element.
     */
    const syncInputToPreview = (inputId, previewId, attribute = 'textContent') => {
        const inputElement = document.getElementById(inputId);
        const previewElement = document.getElementById(previewId);

        if (inputElement && previewElement) {
            const update = () => {
                // Use innerHTML for textareas to render line breaks as <br>
                if (attribute === 'innerHTML') {
                    previewElement.innerHTML = inputElement.value.replace(/\n/g, '<br>');
                } else {
                    previewElement.textContent = inputElement.value;
                }
            };
            // Set initial value
            update();
            // Update on every keystroke
            inputElement.addEventListener('keyup', update);
        }
    };

    // Initialize the live previews for the review form
    syncInputToPreview('author_name', 'preview-author-name');
    syncInputToPreview('testimonial_text', 'preview-testimonial-text', 'innerHTML');
});