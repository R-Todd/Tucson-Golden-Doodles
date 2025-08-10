// app/static/js/previews/about_preview.js

document.addEventListener('DOMContentLoaded', function() {
    /**
     * A helper function to synchronize a standard form input's value with a preview element.
     * @param {string} inputId - The ID of the form input element.
     * @param {string} previewId - The ID of the element to display the preview.
     */
    const syncInputToPreview = (inputId, previewId) => {
        const inputElement = document.getElementById(inputId);
        const previewElement = document.getElementById(previewId);

        if (inputElement && previewElement) {
            // Update preview on page load with the initial value.
            previewElement.textContent = inputElement.value;
            // Add event listener for real-time updates.
            inputElement.addEventListener('keyup', () => {
                previewElement.textContent = inputElement.value;
            });
        }
    };

    /**
     * A helper function to update an image preview when a new file is selected.
     * @param {string} inputId - The ID of the file input element.
     * @param {string} previewImgId - The ID of the img element to update.
     */
    const handleImagePreview = (inputId, previewImgId) => {
        const inputElement = document.getElementById(inputId);
        const previewImgElement = document.getElementById(previewImgId);

        if (inputElement && previewImgElement) {
            inputElement.addEventListener('change', function() {
                if (this.files && this.files[0]) {
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        previewImgElement.src = e.target.result;
                    };
                    reader.readAsDataURL(this.files[0]);
                }
            });
        }
    };

    // --- Initialize standard previews ---
    syncInputToPreview('about_title', 'preview-about-title');
    handleImagePreview('image_upload', 'preview-about-image');

    // --- THIS IS THE UPDATED LOGIC FOR CKEDITOR ---
    // We check if the CKEDITOR library has loaded and our instance exists.
    if (typeof CKEDITOR !== 'undefined' && CKEDITOR.instances.content_html) {
        const previewElement = document.getElementById('preview-about-content');
        const editor = CKEDITOR.instances.content_html;

        // Set the initial content for the preview on page load.
        if (previewElement) {
            previewElement.innerHTML = editor.getData();
        }

        // Use the editor's 'change' event to update the preview.
        // This is more reliable than 'keyup'.
        editor.on('change', function() {
            if (previewElement) {
                previewElement.innerHTML = this.getData();
            }
        });
    }
});