function toggleCompanyFields() {
    const registrationType = document.getElementById("registrationTypeInput").value;
    const companyFields = document.getElementById("companyFields");

    if (registrationType === "proprietor" || registrationType === "company") {
        companyFields.style.display = "flex";  // Show fields for Proprietor and Company
    } else {
        companyFields.style.display = "none";  // Hide fields for Individual
    }
}