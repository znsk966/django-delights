from django.contrib import admin
from .models import (
    Ingredient, 
    MenuItem, 
    RecipeRequirement, 
    Purchase,
    GoodsReceiptNote,
    GoodsReceiptNoteItem 
)

# Register your models here.
admin.site.register(Ingredient)
admin.site.register(MenuItem)
admin.site.register(RecipeRequirement)
admin.site.register(Purchase)
admin.site.register(GoodsReceiptNote)    
admin.site.register(GoodsReceiptNoteItem)  

