from django.db import models
from djmoney.models.fields import MoneyField
from django.db.models import Sum
from django.contrib.auth.models import AbstractUser, BaseUserManager

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)


class Address(models.Model):
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)

    def __str__(self):
        return f"{self.city} - {self.street} - postal code: {self.postal_code}"
        

class UserManager(BaseUserManager):
    
    def create_user(self, email, username, phone_number, password=None):
        if not email:
            raise ValueError("Users must have an email address.")
        if not username:
            raise ValueError("Users must have a username.")
        if not phone_number:
            raise ValueError("Users must have a phone_number.")

        user = self.model(
            email = self.normalize_email(email),
            username = username,
            phone_number = phone_number,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, phone_number, password):
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,
            phone_number = phone_number,
            password = password
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
        

class User(AbstractUser):
    
    email             = models.EmailField(verbose_name="email", max_length=60, unique=True)
    username          = models.CharField(max_length=100, unique=True)
    phone_number      = models.CharField(max_length=100, unique=True)
    shipping_address  = models.ForeignKey('Address', related_name = 'shipping_address', on_delete = models.SET_NULL, blank = True, null = True)
    billing_address   = models.ForeignKey('Address', related_name = 'billing_address', on_delete = models.SET_NULL, blank = True, null = True)
    date_joined       = models.DateTimeField(verbose_name="date joined", auto_now_add=True)
    last_login        = models.DateTimeField(verbose_name="last login", auto_now=True)
    is_admin          = models.BooleanField(default=False)
    is_active         = models.BooleanField(default=True)
    is_staff          = models.BooleanField(default=False)
    is_superuser      = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD  = 'username'
    REQUIRED_FIELDS = ['email', 'phone_number']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def had_module_perms(self, app_label):
        return True


class Product(models.Model):
    name = models.CharField(max_length=100)
    SKU = models.CharField(max_length=100)
    price = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')
    description = models.TextField()

    def __str__(self):
        return self.name
    
    def stock(self):
        purchase_items = self.purchase_items.all().aggregate(Sum('quantity'))
        sales_items = self.sales_items.all().aggregate(Sum('quantity'))
        purchase_count = 0
        if purchase_items['quantity__sum'] != None :
            purchase_count = purchase_items['quantity__sum']

        sales_count = 0        
        if sales_items['quantity__sum'] != None :
            sales_count = sales_items['quantity__sum']

        return purchase_count - sales_count

    def get_image(self):
        list = UploadProductImage.objects.all()
        for img in list:
            if img.product.id == self.id:
                return img.image
        return 'products/images/defult.png'


class UploadProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to = 'products/images/')

    def __str__(self):
        return self.product.name


class PurchaseOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user.username} - {self.user.email}"


class PurchaseOrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='purchase_items')
    quantity = models.IntegerField(default=0)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.Case)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"


class SalesOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"sale order by {self.user.username}"


class SalesOrderItem(models.Model):
    product    = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales_items')
    quantity   = models.IntegerField(default=0)
    sale_order = models.ForeignKey(SalesOrder, on_delete=models.Case)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
    
    def amount(self):
        return self.product.price * self.quantity