// app/static/js/previews/about_preview.js

document.addEventListener('DOMContentLoaded', function() {
    /**
     * Synchronizes an input's value with a preview element.
     * @param {string} inputId - The ID of the form input.
     * @param {string} previewId - The ID of the preview element.
     * @param {string} [attribute='textContent'] - The attribute to update.
     */
    const syncInputToPreview = (inputId, previewId, attribute = 'textContent') => {
        const inputElement = document.getElementById(inputId);
        const previewElement = document.getElementById(previewId);

        if (inputElement && previewElement) {
            const update = () => {
                if (attribute === 'innerHTML') {
                    // Replace newlines with <br> tags for proper rendering.
                    previewElement.innerHTML = inputElement.value.replace(/\n/g, '<br>');
                } else {
                    previewElement.textContent = inputElement.value;
                }
            };
            update(); // Initial update on page load.
            inputElement.addEventListener('keyup', update);
        }
    };

    /**
     * Handles updating an image preview from a file input.
     */
    const handleImagePreview = (inputId, previewImgId) => {
        const inputElement = document.getElementById(inputId);
        const previewImgElement = document.getElementById(previewImgId);

        if (inputElement && previewImgElement) {
            inputElement.addEventListener('change', function() {
                if (this.files && this.files[0]) {
                    const reader = new FileReader();
                    reader.onload = (e) => previewImgElement.src = e.target.result;
                    reader.readAsDataURL(this.files[0]);
                }
            });
        }
    };

    // Initialize all listeners.
    syncInputToPreview('about_title', 'preview-about-title');
    handleImagePreview('image_upload', 'preview-about-image');
    
    // Use the standard sync function for the content, rendering HTML.
    syncInputToPreview('content_html', 'preview-about-content', 'innerHTML');
});