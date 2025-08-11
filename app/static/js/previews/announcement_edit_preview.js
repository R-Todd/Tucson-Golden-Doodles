// app/static/js/previews/announcement_edit_preview.js

/**
 * This script is responsible for populating the data attributes
 * on the 'Featured Litter' dropdown in the announcement banner
 * edit page. It ensures the live preview can access the necessary
 * parent names and birth dates.
 */
document.addEventListener('DOMContentLoaded', function() {
    const select = document.getElementById('featured_puppy');
    const litterDataElement = document.getElementById('litter-data-for-js');

    if (select && litterDataElement) {
        // Parse the JSON data embedded in the template
        const litters = JSON.parse(litterDataElement.textContent);

        // Iterate over the data and assign attributes to the options
        litters.forEach(litter => {
            const option = select.querySelector(`option[value="${litter.id}"]`);
            if (option) {
                option.setAttribute('data-mom-name', litter.mom_name);
                option.setAttribute('data-dad-name', litter.dad_name);
                option.setAttribute('data-birth-date', litter.birth_date);
            }
        });

        // Trigger the 'change' event on the main preview script
        // to ensure the preview is populated on initial page load.
        select.dispatchEvent(new Event('change'));
    }
});