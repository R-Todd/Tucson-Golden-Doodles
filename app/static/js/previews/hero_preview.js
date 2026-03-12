// app/static/js/previews/hero_preview.js

document.addEventListener('DOMContentLoaded', function() {
    const FALLBACKS = {
        main_title: 'Beautiful Mini Goldendoodles Raised with Care',
        subtitle: 'Family-raised in Arizona',
        description: 'Meet our current litters, learn about our parents, and explore available puppies.'
    };

    const byId = (id) => document.getElementById(id);

    const setText = (inputId, previewId, fallback = '') => {
        const input = byId(inputId);
        const preview = byId(previewId);
        if (!input || !preview) return;

        const update = () => {
            const value = input.value.trim();
            preview.textContent = value || fallback;
        };

        update();
        input.addEventListener('input', update);
    };

    const setBullet = (inputId, itemId, textId) => {
        const input = byId(inputId);
        const item = byId(itemId);
        const text = byId(textId);
        if (!input || !item || !text) return;

        const update = () => {
            const value = input.value.trim();
            text.textContent = value;
            item.style.display = value ? '' : 'none';
        };

        update();
        input.addEventListener('input', update);
    };

    const handleImagePreview = (inputId, previewImgId) => {
        const input = byId(inputId);
        const previewImg = byId(previewImgId);
        if (!input || !previewImg) return;

        input.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewImg.src = e.target.result;
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    };

    const syncImageAltToTitle = () => {
        const titleInput = byId('main_title');
        const previewImg = byId('preview-hero-image');
        if (!titleInput || !previewImg) return;

        const update = () => {
            const value = titleInput.value.trim();
            previewImg.alt = value || 'Hero image preview';
        };

        update();
        titleInput.addEventListener('input', update);
    };

    setText('main_title', 'preview-main-title', FALLBACKS.main_title);
    setText('subtitle', 'preview-subtitle', FALLBACKS.subtitle);
    setText('description', 'preview-description', FALLBACKS.description);

    setBullet('scroll_text_main', 'preview-scroll-main-item', 'preview-scroll-main');
    setBullet('scroll_text_secondary', 'preview-scroll-secondary-item', 'preview-scroll-secondary');

    handleImagePreview('image_upload', 'preview-hero-image');
    syncImageAltToTitle();
});