from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Customer(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200,  null=True)
    email = models.CharField(max_length=200, null=True)

    def __str__(self):
        return f'{str(self.id)} {self.name}'
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

class CategoryProduct(models.Model):
    name = models.CharField(max_length=100,verbose_name='Nombre')

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

class Product(models.Model):
    name = models.CharField(max_length=200, null=True)
    price = models.FloatField()
    digital = models.BooleanField(default=False, null=True, )
    photo = models.ImageField(upload_to="products/%Y/%m", default=False)
    category=models.ForeignKey(CategoryProduct, on_delete=models.CASCADE,null=False,blank=False)

    def __str__(self):
        return f'{self.id} {self.name}'
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'


class Cart(models.Model):
    user = models.ForeignKey(
        Customer, on_delete=models.CASCADE, null=False, blank=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.name}'
    
    class Meta:
        verbose_name = 'Carrito'
        verbose_name_plural = 'Carritos'

class CartItem(models.Model):
    cart=models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, null=False, blank=False)
    cantidad = models.IntegerField(default=0)

    def total(self): #en vez de guardar el valor, mejor lo genero
        return self.cantidad*self.product.price

    def __str__(self):
        return f'{self.cantidad} / {self.product.name} - {self.cart.user.name}'
    
    class Meta:
        verbose_name = 'Item carrito'
        verbose_name_plural = 'Items carrito'