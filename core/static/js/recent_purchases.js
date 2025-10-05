document.addEventListener("DOMContentLoaded", function () {
  // Add file upload feedback for both upload and replace
  const fileInputs = document.querySelectorAll(".file-input");

  fileInputs.forEach((input) => {
    input.addEventListener("change", function () {
      const form = this.closest("form");
      const label =
        this.nextElementSibling?.querySelector("label") ||
        this.nextElementSibling;

      if (this.files.length > 0) {
        // Show loading state
        if (label) {
          const originalText = label.innerHTML;
          label.innerHTML =
            '<i class="fas fa-spinner fa-spin"></i> Uploading...';
          label.style.opacity = "0.7";
          label.disabled = true;

          // Submit form after a brief delay to show feedback
          setTimeout(() => {
            form.submit();
          }, 500);
        } else {
          form.submit();
        }
      }
    });
  });

  // Add smooth interactions for all action buttons
  const actionButtons = document.querySelectorAll(
    ".btn-upload, .btn-view-screenshot, .btn-mark-delivered, .btn-replace-screenshot"
  );

  actionButtons.forEach((button) => {
    button.addEventListener("mouseenter", function () {
      this.style.transform = "translateY(-2px)";
    });

    button.addEventListener("mouseleave", function () {
      this.style.transform = "translateY(0)";
    });
  });

  // Add confirmation for mark delivered
  const deliverButtons = document.querySelectorAll(".btn-mark-delivered");

  deliverButtons.forEach((button) => {
    button.addEventListener("click", function (e) {
      if (
        !confirm(
          "Have you received this item? Click OK to mark it as delivered."
        )
      ) {
        e.preventDefault();
      }
    });
  });

  // Add confirmation for replacing screenshot
  const replaceButtons = document.querySelectorAll(".btn-replace-screenshot");

  replaceButtons.forEach((button) => {
    button.addEventListener("click", function (e) {
      if (
        !confirm(
          "Are you sure you want to replace the current payment screenshot? The old one will be overwritten."
        )
      ) {
        e.preventDefault();
      }
    });
  });
});

