// app/static/js/previews/puppy_preview.js

document.addEventListener('DOMContentLoaded', function() {
    const setText = (element, value, fallback = '—') => {
        if (!element) return;
        const cleaned = (value || '').toString().trim();
        element.textContent = cleaned || fallback;
    };

    const syncInputToPreview = (inputId, previewId, fallback = '—') => {
        const inputElement = document.getElementById(inputId);
        const previewElement = document.getElementById(previewId);

        if (inputElement && previewElement) {
            const update = () => setText(previewElement, inputElement.value, fallback);
            update();
            inputElement.addEventListener('keyup', update);
            inputElement.addEventListener('change', update);
        }
    };

    const handleImagePreview = (inputId, previewImgId) => {
        const inputElement = document.getElementById(inputId);
        const previewImgElement = document.getElementById(previewImgId);

        if (inputElement && previewImgElement) {
            inputElement.addEventListener('change', function() {
                if (this.files && this.files[0]) {
                    const reader = new FileReader();
                    reader.onload = (e) => previewImgElement.src = e.target.result;
                    reader.readAsDataURL(this.files[0]);
                }
            });
        }
    };

    const syncSelectToPreview = (selectId, previewId, fallback = '—') => {
        const selectElement = document.getElementById(selectId);
        const previewElement = document.getElementById(previewId);

        if (selectElement && previewElement) {
            const update = () => {
                const selectedOption = selectElement.options[selectElement.selectedIndex];
                if (!selectedOption || !selectedOption.value) {
                    previewElement.textContent = fallback;
                    return;
                }
                previewElement.textContent = selectedOption.text;
            };
            update();
            selectElement.addEventListener('change', update);
        }
    };

    const syncStatusBadge = () => {
        const statusSelect = document.getElementById('status');
        const badge = document.getElementById('preview-puppy-status');
        if (!statusSelect || !badge) return;

        const update = () => {
            const selectedOption = statusSelect.options[statusSelect.selectedIndex];
            const value = selectedOption ? selectedOption.value : '';
            const text = selectedOption ? selectedOption.text : '';

            badge.classList.remove('bg-secondary', 'bg-success', 'bg-warning', 'text-dark', 'bg-dark');

            if (!value) {
                badge.textContent = '—';
                badge.classList.add('bg-secondary');
                return;
            }

            badge.textContent = text;

            if (value === 'AVAILABLE') {
                badge.classList.add('bg-success');
            } else if (value === 'RESERVED') {
                badge.classList.add('bg-warning', 'text-dark');
            } else if (value === 'SOLD') {
                badge.classList.add('bg-dark');
            } else {
                badge.classList.add('bg-secondary');
            }
        };

        update();
        statusSelect.addEventListener('change', update);
    };

    const syncLitterPreview = () => {
        const litterSelect = document.getElementById('litter_id');
        const breedElement = document.getElementById('preview-breed-name');
        const motherElement = document.getElementById('preview-mother-name');
        const fatherElement = document.getElementById('preview-father-name');

        if (!litterSelect) return;

        const update = () => {
            const selectedOption = litterSelect.options[litterSelect.selectedIndex];
            const optionText = selectedOption ? selectedOption.text.trim() : '';

            if (!selectedOption || !selectedOption.value || !optionText) {
                setText(breedElement, '', '—');
                setText(motherElement, '', '—');
                setText(fatherElement, '', '—');
                return;
            }

            setText(breedElement, optionText, '—');

            const parentMatch = optionText.match(/(.+?)\s+[–-]\s+(.+?)\s*x\s*(.+)$/i);
            if (parentMatch) {
                setText(breedElement, parentMatch[1], '—');
                setText(motherElement, parentMatch[2], '—');
                setText(fatherElement, parentMatch[3], '—');
            } else {
                setText(motherElement, '', '—');
                setText(fatherElement, '', '—');
            }
        };

        update();
        litterSelect.addEventListener('change', update);
    };

    syncInputToPreview('name', 'preview-puppy-name', 'New Puppy');
    syncInputToPreview('coat', 'preview-puppy-coat');
    syncInputToPreview('gender', 'preview-puppy-gender');

    handleImagePreview('image_upload', 'preview-puppy-image');

    syncStatusBadge();
    syncLitterPreview();
    syncSelectToPreview('gender', 'preview-puppy-gender');
});