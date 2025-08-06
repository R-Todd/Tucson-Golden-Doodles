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


    // --- 3. INITIALIZE THE CAROUSEL (FINAL CORRECTED LOGIC) ---
    const liveCarouselElement = document.getElementById('live-preview-carousel');
    if (liveCarouselElement) {
        const previewCarousel = new bootstrap.Carousel(liveCarouselElement, {
            interval: 5000, // The auto-cycle interval 
            //pause: 'hover'  // The hover behavior you like
        });

        const prevButton = liveCarouselElement.querySelector('.carousel-control-prev');
        const nextButton = liveCarouselElement.querySelector('.carousel-control-next');

        // This function will run only ONCE when a control button is clicked.
        const stopAutoCycleOnClick = () => {
            previewCarousel.pause(); // Pause the auto-cycle
            const carouselInstance = bootstrap.Carousel.getInstance(liveCarouselElement);
            if (carouselInstance) {
                carouselInstance._config.interval = false; // Permanently disable auto-cycling
            }
            // Clean up the event listeners so this doesn't run again.
            if (prevButton) prevButton.removeEventListener('click', stopAutoCycleOnClick);
            if (nextButton) nextButton.removeEventListener('click', stopAutoCycleOnClick);
        };

        // Attach the listener directly to the buttons' CLICK events.
        if (prevButton) {
            prevButton.addEventListener('click', stopAutoCycleOnClick);
        }
        if (nextButton) {
            nextButton.addEventListener('click', stopAutoCycleOnClick);
        }

        // Initially start the carousel's automatic cycling.
        previewCarousel.cycle();
    }
});