document.addEventListener('DOMContentLoaded', function() {
    // Find all file input fields within a form
    const fileInputs = document.querySelectorAll('form input[type="file"]');

    fileInputs.forEach(function(input) {
        // --- PREVIEW CONTAINER SETUP (No changes here) ---
        const previewContainer = document.createElement('div');
        previewContainer.className = 'image-preview-container mt-2';
        
        const previewImage = document.createElement('img');
        previewImage.className = 'image-preview-thumbnail';
        previewImage.style.maxHeight = '150px';
        previewImage.style.maxWidth = '100%';
        previewImage.style.border = '1px solid #ddd';
        previewImage.style.borderRadius = '4px';
        previewImage.style.padding = '5px';

        previewContainer.appendChild(previewImage);
        input.parentNode.insertBefore(previewContainer, input.nextSibling);

        // --- NEW: SHOW CURRENT IMAGE ON PAGE LOAD ---
        const currentImageUrl = input.getAttribute('data-current-image');
        if (currentImageUrl) {
            previewImage.src = currentImageUrl;
            previewContainer.style.display = 'block';
        } else {
            previewContainer.style.display = 'none'; // Keep it hidden if no current image
        }

        // --- HANDLE NEW FILE SELECTION (No changes here) ---
        input.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewImage.src = e.target.result;
                    previewContainer.style.display = 'block'; 
                }
                reader.readAsDataURL(file);
            } else {
                // If a new file selection is cancelled, show the original image again
                if (currentImageUrl) {
                    previewImage.src = currentImageUrl;
                } else {
                    previewContainer.style.display = 'none';
                }
            }
        });
    });
});