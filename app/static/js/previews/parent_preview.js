// app/static/js/previews/parent_preview.js

document.addEventListener('DOMContentLoaded', function() {
    // --- 1. DEFINE HELPER FUNCTIONS ---

    // Syncs text inputs (name, breed, description)
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
            update();
            inputElement.addEventListener('keyup', update);
        }
    };

    // Syncs the weight input with correct formatting
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

    // Reads an image file and updates the src of a preview image tag
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

    // --- 2. INITIALIZE ALL PREVIEWS ---

    // Initialize text and weight previews
    syncInputToPreview('name', 'preview-parent-name');
    syncInputToPreview('breed', 'preview-parent-breed');
    syncInputToPreview('description', 'preview-parent-description', 'innerHTML');
    syncWeightPreview();

    // Initialize all image previews
    handleImagePreview('image_upload', 'preview-parent-image');
    handleImagePreview('alternate_image_upload_1', 'preview-alt-image-1');
    handleImagePreview('alternate_image_upload_2', 'preview-alt-image-2');
    handleImagePreview('alternate_image_upload_3', 'preview-alt-image-3');
    handleImagePreview('alternate_image_upload_4', 'preview-alt-image-4');


    // --- 3. INITIALIZE THE CAROUSEL (REVISED) ---

    const liveCarouselElement = document.getElementById('live-preview-carousel');
    if (liveCarouselElement) {
        // Initialize the carousel instance, making sure it pauses on hover
        const previewCarousel = new bootstrap.Carousel(liveCarouselElement, {
            interval: 8000,
            pause: 'hover' // Pauses the cycling when the mouse is over the carousel
        });

        // This function will permanently stop the auto-cycling
        // once the admin interacts with the controls.
        function stopAutoCycle() {
            previewCarousel.pause(); // Pause the current cycle
            
            // Access the carousel's internal configuration to permanently disable the interval
            const carouselInstance = bootstrap.Carousel.getInstance(liveCarouselElement);
            if (carouselInstance) {
                carouselInstance._config.interval = false;
            }
        }

        // Find the control buttons within this specific carousel
        const prevButton = liveCarouselElement.querySelector('.carousel-control-prev');
        const nextButton = liveCarouselElement.querySelector('.carousel-control-next');

        // Add click listeners to stop the carousel on manual interaction
        if (prevButton) {
            prevButton.addEventListener('click', stopAutoCycle);
        }
        if (nextButton) {
            nextButton.addEventListener('click', stopAutoCycle);
        }

        // Explicitly start the carousel's automatic cycling
        previewCarousel.cycle();
    }
});