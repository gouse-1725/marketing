document.addEventListener("DOMContentLoaded", function () {
  // Add smooth interactions
  const confirmBtn = document.querySelector(".btn-confirm-payment");
  const confirmForm = document.querySelector(
    "form[action=\"{% url 'payment_success' %}\"]"
  );

  if (confirmBtn && confirmForm) {
    confirmBtn.addEventListener("click", function (e) {
      // Optional: Add confirmation dialog
      const confirmed = confirm(
        "Have you completed the payment? Click OK to proceed to upload payment screenshot."
      );

      if (!confirmed) {
        e.preventDefault();
        return;
      }

      // Add loading state
      const originalText = this.innerHTML;
      this.innerHTML =
        '<i class="fas fa-spinner fa-spin"></i><span>Processing...</span>';
      this.disabled = true;

      // The form will naturally submit and redirect to recent_purchases
      // via the Django view handling the payment_success URL
    });
  }

  // Add copy UPI ID functionality
  const upiIdElement = document.querySelector(".upi-id");
  if (upiIdElement) {
    upiIdElement.style.cursor = "pointer";
    upiIdElement.title = "Click to copy UPI ID";

    upiIdElement.addEventListener("click", function () {
      const upiId = this.textContent;
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(upiId).then(() => {
          // Show temporary feedback
          const originalText = this.textContent;
          this.textContent = "Copied!";
          this.style.color = "#28a745";

          setTimeout(() => {
            this.textContent = originalText;
            this.style.color = "#007bff";
          }, 2000);
        });
      }
    });
  }
});
