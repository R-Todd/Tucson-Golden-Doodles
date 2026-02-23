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
            update();
            inputElement.addEventListener('keyup', update);
            inputElement.addEventListener('change', update);
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
                previewElement.textContent = selectedOption ? selectedOption.text : '';
            };
            update();
            selectElement.addEventListener('change', update);
        }
    };

    // Live preview listeners
    syncInputToPreview('name', 'preview-puppy-name');
    syncInputToPreview('coat', 'preview-puppy-coat');

    handleImagePreview('image_upload', 'preview-puppy-image');

    syncSelectToPreview('status', 'preview-puppy-status');
    syncSelectToPreview('litter_id', 'preview-litter-label');
});
