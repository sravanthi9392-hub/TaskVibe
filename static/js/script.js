document.addEventListener("DOMContentLoaded", function () {
    // Dynamic Form Interception for Loading UI
    const forms = document.querySelectorAll("form");
    const loader = document.getElementById("loading-indicator");

    forms.forEach(form => {
        form.addEventListener("submit", function () {
            if (loader) loader.style.display = "block";
        });
    });

    // Automatically dismiss system structural notifications after 5 seconds
    setTimeout(() => {
        const alerts = document.querySelectorAll(".alert");
        alerts.forEach(alert => {
            let bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});

/**
 * Universal deletion confirmation routing trigger logic
 * @param {string} title 
 * @param {string} formId 
 */
function confirmDeletion(title, formId) {
    const confirmModalElement = document.getElementById('deleteConfirmationModal');
    if (confirmModalElement) {
        document.getElementById('modal-task-title').innerText = title;
        document.getElementById('modal-delete-form').action = "/task/delete/" + formId;
        
        let targetModal = new bootstrap.Modal(confirmModalElement);
        targetModal.show();
    } else {
        if (confirm(`Are you sure you want to permanently drop "${title}"?`)) {
            let fallBackForm = document.createElement('form');
            fallBackForm.method = 'POST';
            fallBackForm.action = "/task/delete/" + formId;
            document.body.appendChild(fallBackForm);
            fallBackForm.submit();
        }
    }
}
