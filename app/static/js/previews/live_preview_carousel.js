// app/static/js/previews/live_preview_carousel.js

document.addEventListener('DOMContentLoaded', function() {
    // Find the specific carousel element in the live preview by its ID.
    const liveCarouselElement = document.getElementById('live-preview-carousel');
    
    // If the element exists, initialize it as a Bootstrap Carousel.
    if (liveCarouselElement) {
        new bootstrap.Carousel(liveCarouselElement, {
            // Set interval to false to disable auto-playing.
            interval: false 
        });
    }
});