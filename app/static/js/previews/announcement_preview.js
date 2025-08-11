// app/static/js/previews/announcement_preview.js

document.addEventListener('DOMContentLoaded', function() {
    // --- PART 1: Populate Dropdown Data Attributes ---
    // This logic was formerly in announcement_edit_preview.js

    const select = document.getElementById('featured_puppy');
    const litterDataElement = document.getElementById('litter-data-for-js');

    if (select && litterDataElement) {
        try {
            const litters = JSON.parse(litterDataElement.textContent);
            litters.forEach(litter => {
                const option = select.querySelector(`option[value="${litter.id}"]`);
                if (option) {
                    option.setAttribute('data-mom-name', litter.mom_name);
                    option.setAttribute('data-dad-name', litter.dad_name);
                    option.setAttribute('data-birth-date', litter.birth_date);
                }
            });
        } catch (e) {
            console.error("Failed to parse litter data JSON:", e);
        }
    }

    // --- PART 2: Handle Live Preview Updates ---
    // This is the core logic from the original announcement_preview.js

    const syncInputToPreview = (inputId, previewId) => {
        const inputElement = document.getElementById(inputId);
        const previewElement = document.getElementById(previewId);

        if (inputElement && previewElement) {
            previewElement.textContent = inputElement.value;
            inputElement.addEventListener('keyup', () => {
                previewElement.textContent = inputElement.value;
            });
        }
    };

    const syncSubtextPreview = () => {
        const subtextInput = document.getElementById('sub_text');
        const litterSelect = document.getElementById('featured_puppy'); // Already defined as 'select'
        const previewElement = document.getElementById('preview-sub-text');

        if (!subtextInput || !litterSelect || !previewElement) return;

        const updateSubtext = () => {
            let subtext = subtextInput.value;
            const selectedOption = litterSelect.options[litterSelect.selectedIndex];

            if (selectedOption && selectedOption.value) {
                const momName = selectedOption.getAttribute('data-mom-name');
                const dadName = selectedOption.getAttribute('data-dad-name');
                const birthDate = selectedOption.getAttribute('data-birth-date');
                
                if (momName && dadName && birthDate) {
                    subtext = subtext.replace('{mom_name}', momName)
                                     .replace('{dad_name}', dadName)
                                     .replace('{birth_date}', birthDate);
                }
            }
            previewElement.textContent = subtext;
        };
        
        updateSubtext(); // Initial call
        subtextInput.addEventListener('keyup', updateSubtext);
        litterSelect.addEventListener('change', updateSubtext);
    };

    // Initialize all preview functionalities
    syncInputToPreview('main_text', 'preview-main-text');
    syncInputToPreview('button_text', 'preview-button-text');
    syncSubtextPreview();

    // Finally, trigger the change event to ensure the preview is populated on page load
    if (select) {
        select.dispatchEvent(new Event('change'));
    }
});