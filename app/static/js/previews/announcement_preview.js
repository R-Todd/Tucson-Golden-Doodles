// app/static/js/previews/announcement_preview.js

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
            // Update on page load
            previewElement.textContent = inputElement.value;
            // Update in real-time
            inputElement.addEventListener('keyup', () => {
                previewElement.textContent = inputElement.value;
            });
        }
    };

    /**
     * Handles the special logic for the sub-text, which uses placeholders.
     */
    const syncSubtextPreview = () => {
        const subtextInput = document.getElementById('sub_text');
        const litterSelect = document.getElementById('featured_puppy');
        const previewElement = document.getElementById('preview-sub-text');

        if (!subtextInput || !litterSelect || !previewElement) return;

        const updateSubtext = () => {
            let subtext = subtextInput.value;
            const selectedOption = litterSelect.options[litterSelect.selectedIndex];

            if (selectedOption && selectedOption.value) {
                // Get data attributes from the selected option
                const momName = selectedOption.getAttribute('data-mom-name');
                const dadName = selectedOption.getAttribute('data-dad-name');
                const birthDate = selectedOption.getAttribute('data-birth-date');
                
                // Replace placeholders
                subtext = subtext.replace('{mom_name}', momName)
                                 .replace('{dad_name}', dadName)
                                 .replace('{birth_date}', birthDate);
            }
            previewElement.textContent = subtext;
        };
        
        // Update on load and when inputs change
        updateSubtext();
        subtextInput.addEventListener('keyup', updateSubtext);
        litterSelect.addEventListener('change', updateSubtext);
    };

    // --- Initialize all live previews ---
    syncInputToPreview('main_text', 'preview-main-text');
    syncInputToPreview('button_text', 'preview-button-text');
    syncSubtextPreview();
});