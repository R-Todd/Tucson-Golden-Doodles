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
            // No need to call update() on load, as Jinja now pre-fills the values.
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


    // --- 3. INITIALIZE THE CAROUSEL (UNIFIED LOGIC) ---
    const liveCarouselElement = document.getElementById('live-preview-carousel');
    if (liveCarouselElement) {
        // Initialize with the same settings as the main site's carousel
        const previewCarousel = new bootstrap.Carousel(liveCarouselElement, {
            interval: 5000, // Auto-cycle every 5 seconds
            pause: 'hover'  // Pause on hover
        });

        // Function to permanently stop auto-cycling on user interaction
        function stopAutoCycle() {
            previewCarousel.pause();
            const carouselInstance = bootstrap.Carousel.getInstance(liveCarouselElement);
            if (carouselInstance) {
                // We access the internal config to permanently stop the auto-cycle
                carouselInstance._config.interval = false;
            }
        }

        const prevButton = liveCarouselElement.querySelector('.carousel-control-prev');
        const nextButton = liveCarouselElement.querySelector('.carousel-control-next');

        if (prevButton) {
            prevButton.addEventListener('click', stopAutoCycle);
        }
        if (nextButton) {
            nextButton.addEventListener('click', stopAutoCycle);
        }

        // Start the carousel cycling automatically
        previewCarousel.cycle();
    }
});