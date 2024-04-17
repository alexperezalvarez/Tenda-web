from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from .models import Product, Cart, Customer, Cart, CartItem
from django.views.generic import ListView, DetailView, FormView, DeleteView
from django.contrib.auth.views import LoginView, LogoutView
from .form import UserRegisterForm
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, authenticate
import json  # para manejar el body del json
from django.utils import timezone

# vista de los articulos
class StoreView(ListView):
    model = Product
    template_name = 'store/store.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    

    def post(self, request, *args, **kwargs):
        data=json.loads(request.body)
        # miro si existe un action
        action = data['action']
        if action == 'add_cart':
            # obtengo el producto
            producto_id = data['pk']
            try:
              producto = Product.objects.get(id=producto_id)
            except Exception as e:
              return JsonResponse({'error':f'El producto no existe'})
            # obtengo el usuario para obtener su customer
            user = request.user
            # obtengo el customer o creo el customer y si lo creo, le paso el name a colocar
            customer, create = Customer.objects.get_or_create(
                user=user, defaults={'name': request.user.username})
            # busco el carrito del customer, y si no existe, lo creo
            cart, create = Cart.objects.get_or_create(user=customer)
            # en el cart se guarda el objeto y en el create es true si se creo uno, o false si encontro alguno
            cartItem, create = CartItem.objects.get_or_create(
                cart=cart, product=producto, defaults={'cantidad': 1})
            if not create:
                # si lo encuentra, le sumo la cantidad en 1, y le asigno el nuevo total
                cartItem.cantidad += 1
            cartItem.save()
            now = timezone.now()
            cart.updated = now.strftime("%Y-%m-%d %H:%M:%S")
            cart.save()
            mensaje={'mensaje':f'¡{producto.name.title()} agregado al carrito!',
                 'can_carrito':CartItem.objects.filter(cart=cart).count()}
        else:
            mensaje={'error':'Acción no valida'}
        return JsonResponse(mensaje)

    def get_queryset(self):
        busqueda = self.request.GET.get('busqueda')
        if busqueda:
            query = Product.objects.filter(name__icontains=busqueda)
            return query
        else:
            return super().get_queryset()

    def get_context_data(self, **kwargs):
        # recupero el context para enviar datos
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # obtengo la cantidad de productos en el carrito del usuario
            user = self.request.user
            customer, create = Customer.objects.get_or_create(
                user=user, name=user.username)
            cart, create = Cart.objects.get_or_create(user=customer)
            canCarrito = CartItem.objects.filter(cart=cart).count()
            context['can_carrito'] = canCarrito

        context['title'] = 'Tienda'
        context['cart_url'] = reverse_lazy('cart')
        if not context['object_list']:
            busqueda = self.request.GET.get('busqueda')
            if busqueda:
                context['mensaje_busqueda'] = f'Producto no encontrado con "{busqueda}"'
        return context

# registro
class RegisterForm(FormView):
    form_class = UserRegisterForm
    template_name = 'store/register.html'
    success_url = reverse_lazy('store')

    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:  # si esta logueado lo mando a la vista principal
            return redirect('store')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # ejecuto el guardado del formulario, el cual es una instancia del formulario en el form_class (UserRegisterForm(self.request.POST).save()) pero el form como ya es la instancia del formulario valido, entonces solo se le aplica el save() para guardar el registro, o en este caso al usuario
        form.save()
        username = form.cleaned_data['username']
        password = form.cleaned_data['password1']
        usuario = authenticate(username=username, password=password)
        login(self.request, usuario)
        return redirect('store')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registro'
        return context

# login
class IngresarView(LoginView):
    template_name = 'store/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:  # si esta logueado lo mando a la vista principal
            return redirect('store')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # recupero el context para enviar datos
        context = super().get_context_data(**kwargs)
        context['title'] = 'Iniciar sesión'
        # agregar next_page
        return context

# carrito
class CartView(ListView):
    model = Cart
    template_name = 'store/cart.html'

    @method_decorator(login_required) #para que agregue el next en la dirección y con el input invisible lo recibe la vista del login y lo redirecciona al cart cuando inicie sesión correctamente
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        customer, create = Customer.objects.get_or_create(
            user=user, name=user.username)
        cart, create = Cart.objects.get_or_create(user=customer)
        query = CartItem.objects.filter(cart=cart)
        return query

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        canCarrito = self.get_queryset().count()
        cartItems = self.get_queryset()
        sumaCarrito = 0
        for prod in cartItems:
            sumaCarrito += prod.cantidad * prod.product.price
        context['checkoutValor'] = sumaCarrito
        context['title'] = 'Carrito'
        return context

# vista detail de los productos
class ProductDetailView(DetailView):
    model = Product
    template_name = 'store/product_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # obtengo la cantidad de productos en el carrito del usuario
            user = self.request.user
            customer, create = Customer.objects.get_or_create(
                user=user, name=user.username)
            cart, create = Cart.objects.get_or_create(user=customer)
            canCarrito = CartItem.objects.filter(cart=cart).count()
            context['can_carrito'] = canCarrito

        context['title'] = context['object'].name
        return context

#vista para borrar, restar y sumar al carrito
class CarritoAcciones(View):

    def dispatch(self, request, *args, **kwargs):
        
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
      mensaje={}
      data=json.loads(request.body) # para convertir a dict los valores del post, van en el body
      pk=data['pk']
      user=request.user
      # obtengo el customer del usuario
      customer = Customer.objects.get(user=user)
      # obtengo el carrito del customer
      cart = Cart.objects.get(user=customer)
      # obtengo todos los cartitems del cart del customer
      cartItems = CartItem.objects.filter(cart=cart)
      # obtengo el cartitem del customer y el producto
      cartItem = CartItem.objects.filter(id=pk, cart=cart)
      if not cartItem.exists():
          return JsonResponse({'error':'Item no existe'})
      #continuar
      else:
        # obtengo el carrito
        cartItem = cartItem.first()
        # pregunto la acción
        action=data['action']
        if action=='eliminar':
          #elimino el item
          cartItem.delete()
          mensaje['mensaje']=f'{cartItem.product.name} eliminado'
        elif action=='aumentar':
          # aumento la cantidad
          cartItem.cantidad += 1
          cartItem.save()
          mensaje['mensaje']=f'{cartItem.product.name}'
        elif action=='disminuir':
          if not cartItem.cantidad < 2:
            # aumento la cantidad
            cartItem.cantidad -= 1
            cartItem.save()
            mensaje['mensaje']=f'{cartItem.product.name}'
          else:
            return JsonResponse({'error':'La cantidad es 1, no se puede restar'})
        else:
          return JsonResponse({'error':'Opción no valida'})
        # suma de todo el carrito
        suma=0
        for cartI in cartItems:
            suma+=cartI.cantidad * cartI.product.price
        #mensajes
        mensaje['can_cantidad']=cartItem.cantidad #cantidad del producto
        mensaje['can_total']=cartItem.total() #cantidad total del producto
        mensaje['check_total']=suma #cantidad total de carrito
        

        # actualizo el carrito en su fecha de actualización
        now = timezone.now()
        cart.updated = now.strftime("%Y-%m-%d %H:%M:%S")
        cart.save()
        return JsonResponse(mensaje)

# vista para comprar
def checkout(request):
    context = {}
    return render(request, 'store/checkout.html', context)