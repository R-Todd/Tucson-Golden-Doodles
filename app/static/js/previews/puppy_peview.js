// app/static/js/previews/puppy_preview.js

document.addEventListener('DOMContentLoaded', function() {
    /**
     * Synchronizes a form input's value with a preview element's text content.
     * @param {string} inputId - The ID of the form input element.
     * @param {string} previewId - The ID of the element to display the preview.
     */
    const syncInputToPreview = (inputId, previewId) => {
        const inputElement = document.getElementById(inputId);
        const previewElement = document.getElementById(previewId);

        if (inputElement && previewElement) {
            const update = () => previewElement.textContent = inputElement.value;
            update(); // Set initial value on page load
            inputElement.addEventListener('keyup', update);
        }
    };

    /**
     * Updates an image preview when a new file is selected.
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
                    reader.onload = (e) => previewImgElement.src = e.target.result;
                    reader.readAsDataURL(this.files[0]);
                }
            });
        }
    };
    
    /**
     * Synchronizes a dropdown select's text with a preview element.
     * @param {string} selectId - The ID of the select dropdown element.
     * @param {string} previewId - The ID of the element to display the selected text.
     */
    const syncSelectToPreview = (selectId, previewId) => {
        const selectElement = document.getElementById(selectId);
        const previewElement = document.getElementById(previewId);

        if (selectElement && previewElement) {
            const update = () => {
                const selectedOption = selectElement.options[selectElement.selectedIndex];
                // Use the option's display text for the preview.
                previewElement.textContent = selectedOption ? selectedOption.text : '';
            };
            update(); // Set initial value
            selectElement.addEventListener('change', update);
        }
    };

    // Initialize all live preview listeners.
    syncInputToPreview('name', 'preview-puppy-name');
    handleImagePreview('image_upload', 'preview-puppy-image');
    syncSelectToPreview('status', 'preview-puppy-status');
    syncSelectToPreview('mom_id', 'preview-mom-name');
    syncSelectToPreview('dad_id', 'preview-dad-name');
});