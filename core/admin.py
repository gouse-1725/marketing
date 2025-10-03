from django.contrib import admin
from django.contrib import messages
from .models import CustomUser, Prod_category, Product, OTP, Order, OrderItem, Address


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = [
        "mobile_no",
        "first_name",
        "last_name",
        "email",
        "is_active",
        "is_staff",
    ]
    search_fields = ["mobile_no", "email"]
    list_filter = ["is_active", "is_staff"]


@admin.register(Prod_category)
class ProdCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "price", "stock", "available"]
    search_fields = ["name"]
    list_filter = ["category", "available"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ["mobile_no", "code", "created_at", "expires_at", "is_used"]
    search_fields = ["mobile_no"]
    list_filter = ["is_used"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "order_id",
        "user",
        "payment_status",
        "order_status",
        "total_amount",
        "tracking_number",
        "created_at",
    ]
    list_filter = ["payment_status", "order_status"]
    search_fields = ["order_id", "user__mobile_no", "tracking_number"]
    list_editable = ["payment_status", "order_status", "tracking_number"]
    readonly_fields = ["order_id", "created_at", "updated_at"]

    def save_model(self, request, obj, form, change):
        # Prevent setting order_status to "delivered" unless all OrderItems are "delivered"
        if obj.order_status == "delivered":
            order_items = OrderItem.objects.filter(order=obj)
            if not order_items.exists():
                messages.error(
                    request,
                    "Cannot set order status to 'Delivered' as no items exist in this order.",
                )
                obj.order_status = "pending"  # Revert to pending
            elif not all(item.status == "delivered" for item in order_items):
                messages.error(
                    request,
                    "Cannot set order status to 'Delivered' unless all items are marked as 'Delivered'.",
                )
                obj.order_status = form.initial.get(
                    "order_status", "pending"
                )  # Revert to previous or pending
        super().save_model(request, obj, form, change)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        "order",
        "product",
        "quantity",
        "item_total",
        "status",
        "payment_screenshot",
        "product_image",
    ]
    list_filter = ["status"]
    search_fields = ["order__order_id", "product__name"]
    list_editable = ["status", "product_image"]
    readonly_fields = ["item_total"]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ["user", "address_line", "city", "state", "pincode", "is_selected"]
    search_fields = ["user__mobile_no", "address_line", "city"]
    list_filter = ["is_selected"]
