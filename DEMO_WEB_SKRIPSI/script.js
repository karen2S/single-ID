document.addEventListener("DOMContentLoaded", function () {
  const marriedRadio = document.getElementById("married");
  const singleRadio = document.getElementById("single");
  const submitButton = document.getElementById("submitButton");
  const customerForm = document.getElementById("customerForm");

  // Event listener for "Menikah" radio button
  marriedRadio.addEventListener("change", function () {
    if (marriedRadio.checked) {
      submitButton.textContent = "Next: Add Partner Data"; // Change button text
      customerForm.setAttribute("action", "register.php");
      customerForm.setAttribute("method", "post");
    }
  });

  // Event listener for "Lajang" radio button
  singleRadio.addEventListener("change", function () {
    if (singleRadio.checked) {
      submitButton.textContent = "Submit";

      // Remove any previous event listeners
      customerForm.onsubmit = null;

      // Allow form to submit normally to register.php
      customerForm.setAttribute("action", "register.php");
      customerForm.setAttribute("method", "post");
    }
  });
});