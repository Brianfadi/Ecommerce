from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("cart/", views.cart, name="cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("update_item/", views.updateItem, name="update_item"),
    path("product_view/<int:myid>/", views.product_view, name="product_view"),
    path("search/", views.search, name="search"),
    path("tracker/", views.tracker, name="tracker"),
    path("contact/", views.contact, name="contact"),
    path("loggedin_contact/", views.loggedin_contact, name="loggedin_contact"),

    path("register/", views.register, name="register"),
    path("change_password/", views.change_password, name="change_password"),
    path("login/", views.Login, name="login"),
    path("logout/", views.Logout, name="logout"),

    path('mpindex/', views.index, name='mpindex'),  # form page
    path('stk_push/', views.stk_push, name='stk_push'),
    path('waiting/<int:transaction_id>/', views.waiting_page, name='waiting_page'),

    path('mpesa_payment/<int:order_id>/', views.mpesa_payment, name='mpesa_payment'),
    path('customersupport/', views.customer_support, name='customer_support'),
    path('submit_support_ticket/', views.submit_support_ticket, name='submit_support_ticket'),
    path('faq/', views.faq_page, name='faq_page'),
    path('return-policy/', views.return_policy, name='return_policy'),
    path('profile/', views.profile_view, name='profile'),

]