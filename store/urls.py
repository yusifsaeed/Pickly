
from . import views
from django.urls import path

urlpatterns=[
    path('',views.store,name="store"),
    path('cart',views.cart,name="cart"),
    path('checkout',views.checkout,name="checkout"),
    path('favorites',views.favorites_view,name="favorites"),
    path('login',views.login,name="login"),
    path('signup',views.signup,name="signup"),
    path('logout',views.logout_view,name="logout"),
    path('update_item/', views.updateItem, name="update_item"),
    path('toggle_favorite/', views.toggle_favorite, name="toggle_favorite"),
]