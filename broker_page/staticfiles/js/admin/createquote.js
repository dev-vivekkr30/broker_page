document.addEventListener('DOMContentLoaded', function () {
    // Add New Section Button
    document.querySelector('.add-section-btn').addEventListener('click', function (e) {
        e.preventDefault();  // Prevent form submission
        const newSection = document.querySelector('.newsection').cloneNode(true);

        // Clear the inputs in the new section
        newSection.querySelectorAll('input, select').forEach(input => input.value = '');

        // Add event listeners for buttons in the new section
        addSectionEventListeners(newSection);

        // Insert the new section before the "Add New Section" button
        document.querySelector('form').insertBefore(newSection, e.target);
    });

    // Initial call to set up event listeners for the first section
    addSectionEventListeners(document.querySelector('.newsection'));

    // Function to add event listeners to a section
    function addSectionEventListeners(section) {
        // Add Items to Table
        section.querySelector('.addBtn').addEventListener('click', function (e) {
            e.preventDefault();  // Prevent form submission
            const row = section.querySelector('tbody tr').cloneNode(true);

            // Clear input values in the new row
            row.querySelectorAll('input').forEach(input => input.value = '');

            // Attach delete row event to new row
            row.querySelector('.icon-btn').addEventListener('click', function () {
                row.remove();
            });

            // Append new row to the table
            section.querySelector('tbody').appendChild(row);
        });

        // Delete Section
        section.querySelector('#deleteSection').addEventListener('click', function () {
            section.remove();
        });

        // Set up delete row event for each existing row in the new section
        section.querySelectorAll('tbody .icon-btn').forEach(button => {
            button.addEventListener('click', function () {
                button.closest('tr').remove();
            });
        });
    }
});
