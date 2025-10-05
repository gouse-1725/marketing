document.addEventListener("DOMContentLoaded", function () {
  const loadingOverlay = document.getElementById("loadingOverlay");

  // Show loading overlay
  function showLoading() {
    loadingOverlay.style.display = "flex";
  }

  // Hide loading overlay
  function hideLoading() {
    loadingOverlay.style.display = "none";
  }

  // Toggle address form visibility
  const toggleAddressBtn = document.getElementById("toggleAddressForm");
  const addressFormContainer = document.getElementById("addressFormContainer");

  if (toggleAddressBtn && addressFormContainer) {
    toggleAddressBtn.addEventListener("click", function () {
      addressFormContainer.classList.toggle("show");
      this.innerHTML = `<i class="fas fa-plus"></i> ${
        addressFormContainer.classList.contains("show")
          ? "Hide Form"
          : "Add New Address"
      }`;
    });
  }

  // Update cart total
  function updateCartTotal() {
    let total = 0;
    document.querySelectorAll(".item-total").forEach((element) => {
      total += parseFloat(element.textContent) || 0;
    });
    document.getElementById("cart-total-amount").textContent = total.toFixed(2);
  }

  // Update individual item total
  function updateItemTotal(productId, quantity) {
    const price = parseFloat(
      document.querySelector(`.qty-input[data-product-id="${productId}"]`)
        .dataset.price
    );
    const itemTotal = price * quantity;
    document.querySelector(
      `.item-total[data-product-id="${productId}"]`
    ).textContent = itemTotal.toFixed(2);
  }

  // Initialize quantity and cart functionality
  document.querySelectorAll(".add-to-cart-form").forEach(function (form) {
    const minus = form.querySelector(".qty-minus");
    const plus = form.querySelector(".qty-plus");
    const input = form.querySelector(".qty-input");
    const productId = form.dataset.productId;
    const submitBtn = form.querySelector(".btn-update-cart");

    minus.addEventListener("click", function (e) {
      e.preventDefault();
      let val = parseInt(input.value) || 1;
      if (val > 1) {
        input.value = val - 1;
        updateItemTotal(productId, input.value);
        updateCartTotal();
      }
    });

    plus.addEventListener("click", function (e) {
      e.preventDefault();
      let val = parseInt(input.value) || 1;
      if (val < 99) {
        input.value = val + 1;
        updateItemTotal(productId, input.value);
        updateCartTotal();
      }
    });

    // Form submission for updating cart
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      showLoading();
      const formData = new FormData(this);
      fetch('{% url "add_to_cart" %}', {
        method: "POST",
        body: formData,
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      })
        .then((response) => response.json())
        .then((data) => {
          hideLoading();
          if (data.success) {
            console.log("Cart updated successfully");
          } else {
            console.error("Failed to update cart:", data.error);
            location.reload();
          }
        })
        .catch((error) => {
          hideLoading();
          console.error("Error updating cart:", error);
          location.reload();
        });
    });
  });

  // Handle remove from cart with confirmation
  document.querySelectorAll(".remove-form").forEach((form) => {
    form.addEventListener("submit", function (e) {
      e.preventDefault();

      if (
        confirm("Are you sure you want to remove this item from your cart?")
      ) {
        showLoading();
        this.submit();
      }
    });
  });

  // Style form fields
  document
    .querySelectorAll(
      ".address-form input, .address-form select, .address-form textarea"
    )
    .forEach((field) => {
      field.classList.add("form-control");
    });
});

// Form submission for updating cart
form.addEventListener("submit", function (e) {
  e.preventDefault();
  showLoading();
  const formData = new FormData(this);
  fetch('{% url "add_to_cart" %}', {
    method: "POST",
    body: formData,
    headers: {
      "X-Requested-With": "XMLHttpRequest",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      hideLoading();
      if (data.success) {
        console.log("Cart updated successfully");
      } else {
        console.error("Failed to update cart:", data.error);
        location.reload();
      }
    })
    .catch((error) => {
      hideLoading();
      console.error("Error updating cart:", error);
      location.reload();
    });
});
