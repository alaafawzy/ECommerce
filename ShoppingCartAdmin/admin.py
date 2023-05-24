from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from ShoppingCartAdmin.models import *
from django import forms

class UserAdmn(UserAdmin):
    list_display = ('username', 'email', 'phone_number', 'date_joined', 'last_login', 'is_admin', 'is_staff')
    search_fields = ('email', 'phone_number')
    readonly_fields = ('id', 'date_joined', 'last_login')
    
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','price', 'stock')

class UploadProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image')


class SalesOrderAdmin(admin.ModelAdmin):
    def total_amount(self, order):
        total = 0 
        item_list = SalesOrderItem.objects.all()

        for item in item_list:
            if item.sale_order.id == order.id:
                total += item.product.price * item.quantity
        
        return total

    
    list_display = ('user', 'created', 'total_amount')


class SaleOrderItemForm(forms.ModelForm):
    def clean(self):
        product = self.cleaned_data['product']
        item_quantity = self.cleaned_data['quantity']
        purchase_quantity = product.purchase_items.all().aggregate(Sum('quantity'))
        sales_quantity = product.sales_items.all().aggregate(Sum('quantity'))

        purchases = 0 
        if purchase_quantity['quantity__sum'] != None:
            purchases = purchase_quantity['quantity__sum']
        
        sales = 0 
        if sales_quantity['quantity__sum'] != None:
            sales = sales_quantity['quantity__sum']
        
        have = purchases - sales
        if item_quantity > have:
            raise forms.ValidationError({'quantity': "There is not enough quantity"})


class SaleOrderItemAdmin(admin.ModelAdmin):
    form = SaleOrderItemForm
    list_display = ('id', 'product', 'quantity', 'amount')



admin.site.register(User, UserAdmn)

admin.site.register(Product, ProductAdmin)
admin.site.register(UploadProductImage, UploadProductImageAdmin)

admin.site.register(PurchaseOrder)
admin.site.register(PurchaseOrderItem)

admin.site.register(SalesOrder, SalesOrderAdmin)
admin.site.register(SalesOrderItem, SaleOrderItemAdmin)

admin.site.register(Address)