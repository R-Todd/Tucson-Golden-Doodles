// app/static/js/previews/parent_preview.js

document.addEventListener('DOMContentLoaded', function() {
    // --- 1. DEFINE HELPER FUNCTIONS (No changes here) ---
    const syncInputToPreview = (inputId, previewId, attribute = 'textContent') => {
        const inputElement = document.getElementById(inputId);
        const previewElement = document.getElementById(previewId);
        if (inputElement && previewElement) {
            const update = () => {
                if (attribute === 'innerHTML') {
                    previewElement.innerHTML = inputElement.value.replace(/\n/g, '<br>');
                } else {
                    previewElement.textContent = inputElement.value;
                }
            };
            inputElement.addEventListener('keyup', update);
        }
    };

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
            weightInput.addEventListener('keyup', updateWeight);
        }
    };

    const handleImagePreview = (inputId, previewImgId) => {
        const inputElement = document.getElementById(inputId);
        const previewImgElement = document.getElementById(previewImgId);
        if (inputElement && previewImgElement) {
            inputElement.addEventListener('change', function() {
                if (this.files && this.files[0]) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        previewImgElement.src = e.target.result;
                    };
                    reader.readAsDataURL(this.files[0]);
                }
            });
        }
    };

    // --- 2. INITIALIZE ALL PREVIEWS (No changes here) ---
    syncInputToPreview('name', 'preview-parent-name');
    syncInputToPreview('breed', 'preview-parent-breed');
    syncInputToPreview('description', 'preview-parent-description', 'innerHTML');
    syncWeightPreview();
    handleImagePreview('image_upload', 'preview-parent-image');
    handleImagePreview('alternate_image_upload_1', 'preview-alt-image-1');
    handleImagePreview('alternate_image_upload_2', 'preview-alt-image-2');
    handleImagePreview('alternate_image_upload_3', 'preview-alt-image-3');
    handleImagePreview('alternate_image_upload_4', 'preview-alt-image-4');


    // --- 3. INITIALIZE THE CAROUSEL (REVISED LOGIC) ---
    const liveCarouselElement = document.getElementById('live-preview-carousel');
    if (liveCarouselElement) {
        const previewCarousel = new bootstrap.Carousel(liveCarouselElement, {
            interval: 5000,
            pause: 'hover'
        });

        // This function will be called once, the first time a user
        // manually interacts with the carousel.
        const handleManualInteraction = () => {
            // Stop the carousel from auto-playing further.
            previewCarousel.pause();

            const carouselInstance = bootstrap.Carousel.getInstance(liveCarouselElement);
            if (carouselInstance) {
                carouselInstance._config.interval = false;
            }

            // IMPORTANT: Remove the event listener so this only runs once.
            liveCarouselElement.removeEventListener('slide.bs.carousel', handleManualInteraction);
        };

        // Listen for the 'slide' event, which fires before the transition starts.
        // This is the key change to fix the button functionality.
        liveCarouselElement.addEventListener('slide.bs.carousel', handleManualInteraction);

        // Start the automatic cycling initially.
        previewCarousel.cycle();
    }
});