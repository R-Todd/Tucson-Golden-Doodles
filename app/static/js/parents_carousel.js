document.addEventListener('DOMContentLoaded', function () {
    // Select all carousel elements that have an ID starting with 'parentCarousel-'
    var carousels = document.querySelectorAll('[id^="parentCarousel-"]');

    carousels.forEach(function(carouselElement) {
        // Initialize Bootstrap Carousel for each element
        var carouselInstance = new bootstrap.Carousel(carouselElement, {
            interval: 5000, // Auto-cycle every 5 seconds
            pause: 'hover' // Pause on hover, resume on mouseout
        });

        // Function to stop auto-cycling permanently after user interaction
        function stopCarouselAutoCycle() {
            carouselInstance.pause(); // Pause current cycling
            // Set interval to false to permanently stop auto-cycling
            // We access _config directly as there isn't a public method to change interval after init
            carouselInstance._config.interval = false; 
        }

        // Get the previous and next buttons for the current carousel
        var prevButton = carouselElement.querySelector('.carousel-control-prev');
        var nextButton = carouselElement.querySelector('.carousel-control-next');
        var indicators = carouselElement.querySelector('.carousel-indicators'); // Get indicators too

        // Add event listeners to the control buttons
        if (prevButton) {
            prevButton.addEventListener('click', stopCarouselAutoCycle);
        }
        if (nextButton) {
            nextButton.addEventListener('click', stopCarouselAutoCycle);
        }
        // Also stop if an indicator is clicked
        if (indicators) {
            indicators.addEventListener('click', stopCarouselAutoCycle);
        }

        // Optionally, start cycling immediately if you want it to auto-start initially
        carouselInstance.cycle();
    });
});