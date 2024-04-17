from django.urls import path

from .views import *

urlpatterns = [
    # Leave as empty string for base url
    path('', StoreView.as_view(), name="store"),
    path('cart/', CartView.as_view(), name="cart"),
    path('checkout/', checkout, name="checkout"),
    path('register/', RegisterForm.as_view(), name="register"),
    path('login/', IngresarView.as_view(), name="login"),
    #cerrar sesión
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('product/<int:pk>/',ProductDetailView.as_view(),name='detalle_product'),
    #acciones del carrito
    path('cart/acciones/',CarritoAcciones.as_view(), name="acciones_carrito")
]
