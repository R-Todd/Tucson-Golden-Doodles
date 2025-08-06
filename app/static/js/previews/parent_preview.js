// app/static/js/previews/parent_preview.js

document.addEventListener('DOMContentLoaded', function() {
    /**
     * A generic helper function to sync a form input's value to an HTML element's
     * textContent or innerHTML.
     */
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
            update(); // Set initial value on page load
            inputElement.addEventListener('keyup', update);
        }
    };

    /**
     * A specific function to handle the weight preview, which requires
     * formatting and unit conversion.
     */
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
            updateWeight(); // Set initial value on page load
            weightInput.addEventListener('keyup', updateWeight);
        }
    };

    // --- Sync all Parent fields to the live preview ---
    syncInputToPreview('name', 'preview-parent-name');
    syncInputToPreview('breed', 'preview-parent-breed');
    syncInputToPreview('description', 'preview-parent-description', 'innerHTML');
    
    // Use the custom handler for the weight field
    syncWeightPreview();
});