// app/static/js/previews/about_preview.js

document.addEventListener('DOMContentLoaded', function() {
    /**
     * A helper function to synchronize a form input's value with a preview element.
     * @param {string} inputId - The ID of the form input element.
     * @param {string} previewId - The ID of the element to display the preview.
     * @param {string} attribute - The attribute to update on the preview element ('textContent' or 'innerHTML').
     */
    const syncInputToPreview = (inputId, previewId, attribute = 'textContent') => {
        const inputElement = document.getElementById(inputId);
        const previewElement = document.getElementById(previewId);

        if (inputElement && previewElement) {
            // Update preview on page load with the initial value from the form field.
            if (attribute === 'innerHTML') {
                previewElement.innerHTML = inputElement.value;
            } else {
                previewElement.textContent = inputElement.value;
            }

            // Add an event listener to update the preview in real-time as the user types.
            inputElement.addEventListener('keyup', () => {
                if (attribute === 'innerHTML') {
                    previewElement.innerHTML = inputElement.value;
                } else {
                    previewElement.textContent = inputElement.value;
                }
            });
        }
    };

    /**
     * A helper function to handle updating an image preview when a new file is selected.
     * @param {string} inputId - The ID of the file input element.
     * @param {string} previewImgId - The ID of the img element to update.
     */
    const handleImagePreview = (inputId, previewImgId) => {
        const inputElement = document.getElementById(inputId);
        const previewImgElement = document.getElementById(previewImgId);

        if (inputElement && previewImgElement) {
            inputElement.addEventListener('change', function() {
                // Check if a file was selected.
                if (this.files && this.files[0]) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        // Set the src attribute of the preview image to the new file data.
                        previewImgElement.src = e.target.result;
                    };
                    // Read the file as a data URL to display it.
                    reader.readAsDataURL(this.files[0]);
                }
            });
        }
    };

    // --- Initialize all live previews for the "About" section ---
    syncInputToPreview('about_title', 'preview-about-title');
    // Use 'innerHTML' for the content to correctly render any HTML tags.
    syncInputToPreview('about_content_html', 'preview-about-content', 'innerHTML'); 
    handleImagePreview('image_upload', 'preview-about-image');
});