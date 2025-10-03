# from django.urls import path
# from . import views

# urlpatterns = [
#     path("", views.products, name="home"),
#     path("login/", views.login_view, name="login"),
#     path("verify-otp/", views.verify_otp, name="verify_otp"),
#     path("complete-profile/", views.complete_profile, name="complete_profile"),
#     path("logout/", views.logout_view, name="logout"),
#     path("forgot-password/", views.forgot_password, name="forgot_password"),
#     path("reset-password/", views.reset_password, name="reset_password"),
#     path("products/", views.products, name="products"),
#     path("products/<slug:slug>/", views.product_detail, name="product_detail"),
#     path("category/<slug:slug>/", views.category_products, name="category_products"),
#     path("contact/", views.contact, name="contact"),
#     path("business-plan/", views.business_plan, name="business_plan"),
#     path("about/", views.about, name="about"),
#     path("add-to-cart/", views.add_to_cart, name="add_to_cart"),
#     path("remove-from-cart/", views.remove_from_cart, name="remove_from_cart"),
#     path("cart/", views.cart, name="cart"),
#     # path("payment/", views.payment, name="payment"),
#     path("checkout/", views.checkout, name="checkout"),
#     path("checkout/success/", views.payment_success, name="payment_success"),
#     path("checkout/failure/", views.payment_failure, name="payment_failure"),
#     path("recent-purchases/", views.recent_purchases, name="recent_purchases"),
#     path('add_address/', views.add_address, name='add_address'),
#     path('select_address/<int:address_id>/', views.select_address, name='select_address'),
#     path('upload_payment_screenshot/<int:order_id>/', views.upload_payment_screenshot, name='upload_payment_screenshot'),
#     path('mark_delivered/<int:item_id>/', views.mark_delivered, name='mark_delivered'),
#     path('resend_otp/', views.resend_otp, name='resend_otp'),
#     path('proceed_to_payment/', views.proceed_to_payment, name='proceed_to_payment'),
#     path('delete_address/<int:address_id>/', views.delete_address, name='delete_address'),
#     # path('update_cart_quantity/', views.update_cart_quantity, name='update_cart_quantity'),
# ]


from django.urls import path
from . import views

urlpatterns = [
    path("", views.products, name="home"),
    path("login/", views.login_view, name="login"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("complete-profile/", views.complete_profile, name="complete_profile"),
    path("logout/", views.logout_view, name="logout"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("reset-password/", views.reset_password, name="reset_password"),
    path("products/", views.products, name="products"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),
    path("category/<slug:slug>/", views.category_products, name="category_products"),
    path("contact/", views.contact, name="contact"),
    path("business-plan/", views.business_plan, name="business_plan"),
    path("about/", views.about, name="about"),
    path("add-to-cart/", views.add_to_cart, name="add_to_cart"),
    path("remove-from-cart/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/", views.cart, name="cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("checkout/success/", views.payment_success, name="payment_success"),
    path("checkout/failure/", views.payment_failure, name="payment_failure"),
    path("recent-purchases/", views.recent_purchases, name="recent_purchases"),
    path("add_address/", views.add_address, name="add_address"),
    path(
        "select_address/<int:address_id>/", views.select_address, name="select_address"
    ),
    path(
        "upload_payment_screenshot/<int:order_id>/",
        views.upload_payment_screenshot,
        name="upload_payment_screenshot",
    ),
    path("mark_delivered/<int:item_id>/", views.mark_delivered, name="mark_delivered"),
    path("resend_otp/", views.resend_otp, name="resend_otp"),
    path("proceed_to_payment/", views.proceed_to_payment, name="proceed_to_payment"),
    path(
        "delete_address/<int:address_id>/", views.delete_address, name="delete_address"
    ),
    path(
        "update_cart_quantity/", views.update_cart_quantity, name="update_cart_quantity"
    ),
]
