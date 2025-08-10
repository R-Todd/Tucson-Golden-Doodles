// app/static/js/previews/hero_preview.js

document.addEventListener('DOMContentLoaded', function() {
    /**
     * A helper function to synchronize a form input's value with a preview element.
     * @param {string} inputId - The ID of the form input element.
     * @param {string} previewId - The ID of the element to display the preview.
     */
    const syncInputToPreview = (inputId, previewId) => {
        const inputElement = document.getElementById(inputId);
        const previewElement = document.getElementById(previewId);

        if (inputElement && previewElement) {
            // Update preview on page load with the initial value
            previewElement.textContent = inputElement.value;

            // Add event listener to update the preview in real-time on keyup
            inputElement.addEventListener('keyup', () => {
                previewElement.textContent = inputElement.value;
            });
        }
    };

    /**
     * A helper function to update the background image of the hero preview.
     * @param {string} inputId - The ID of the file input element.
     * @param {string} previewSelector - The CSS selector for the preview section.
     */
    const handleImagePreview = (inputId, previewSelector) => {
        const inputElement = document.getElementById(inputId);
        const previewSection = document.querySelector(previewSelector);

        if (inputElement && previewSection) {
            inputElement.addEventListener('change', function() {
                if (this.files && this.files[0]) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        // Set the background image using an inline style
                        previewSection.style.backgroundImage = `url('${e.target.result}')`;
                    };
                    reader.readAsDataURL(this.files[0]);
                }
            });
        }
    };

    // --- Initialize all live previews ---
    syncInputToPreview('main_title', 'preview-main-title');
    syncInputToPreview('subtitle', 'preview-subtitle');
    syncInputToPreview('description', 'preview-description');
    syncInputToPreview('scroll_text_main', 'preview-scroll-main');
    syncInputToPreview('scroll_text_secondary', 'preview-scroll-secondary');

    // Initialize the image preview
    handleImagePreview('image_upload', '.hero-preview-wrapper .hero-section');
});