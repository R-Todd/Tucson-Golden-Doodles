// app/static/js/previews/parent_preview.js

document.addEventListener('DOMContentLoaded', function() {
    // Helper to sync text-based inputs to a preview element
    const syncInputToPreview = (inputId, previewId, attribute = 'textContent') => {
        const inputElement = document.getElementById(inputId);
        const previewElement = document.getElementById(previewId);

        if (inputElement && previewElement) {
            const update = () => {
                if (attribute === 'innerHTML') {
                    previewElement.innerHTML = inputElement.value;
                } else {
                    previewElement.textContent = inputElement.value;
                }
            };
            update();
            inputElement.addEventListener('keyup', update);
        }
    };

    // Helper to format and sync the weight preview
    const syncWeightPreview = () => {
        const weightInput = document.getElementById('weight_kg');
        const weightPreview = document.getElementById('preview-parent-weight');

        if (weightInput && weightPreview) {
            const updateWeight = () => {
                const kg = parseFloat(weightInput.value);
                if (!isNaN(kg) && kg > 0) {
                    const lbs = (kg * 2.20462).toFixed(1);
                    weightPreview.textContent = `${kg} kg / ${lbs} lbs`;
                } else {
                    weightPreview.textContent = 'Weight: N/A';
                }
            };
            updateWeight();
            weightInput.addEventListener('keyup', updateWeight);
        }
    };

    // Generalized function to handle live image previews for file inputs
    const handleImagePreview = (inputId, previewImgId) => {
        const inputElement = document.getElementById(inputId);
        const previewImgElement = document.getElementById(previewImgId);

        if (inputElement && previewImgElement) {
            inputElement.addEventListener('change', function() {
                if (this.files && this.files[0]) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        previewImgElement.src = e.target.result;
                    }
                    reader.readAsDataURL(this.files[0]);
                }
            });
        }
    };

    // --- Sync all text fields ---
    syncInputToPreview('name', 'preview-parent-name');
    syncInputToPreview('breed', 'preview-parent-breed');
    syncInputToPreview('description', 'preview-parent-description', 'innerHTML');
    syncWeightPreview();

    // --- Initialize image previews for the carousel ---
    handleImagePreview('image_upload', 'preview-parent-image');
    handleImagePreview('alternate_image_upload_1', 'preview-alt-image-1');
    handleImagePreview('alternate_image_upload_2', 'preview-alt-image-2');
    handleImagePreview('alternate_image_upload_3', 'preview-alt-image-3');
    handleImagePreview('alternate_image_upload_4', 'preview-alt-image-4');

    // --- THIS BLOCK HAS BEEN REMOVED ---
    // The explicit new bootstrap.Carousel() call was conflicting with the
    // data-bs-ride="carousel" attribute in the HTML and has been removed.
});