from django import forms
from .models import(
    Ingredient,
    MenuItem,
    RecipeRequirement,
    Purchase,
    GoodsReceiptNote,
    GoodsReceiptNoteItem
)

class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = "__all__" # This will include all fields from the Ingredient model in our form

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = "__all__" # This will include all fields from the MenuItem model in our form

class RecipeRequirementForm(forms.ModelForm):
    class Meta:
        model = RecipeRequirement
        fields = ['ingredient', 'quantity_required']

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ["menu_item"] # This will include all fields from the Purchase model in our form

class GoodsReceiptNoteForm(forms.ModelForm):
    class Meta:
        model = GoodsReceiptNote
        fields = ['note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 3}),
        }

# This creates a factory that can produce a set of forms for GRN items
GRNItemFormSet = forms.inlineformset_factory(
    GoodsReceiptNote,         # The parent model
    GoodsReceiptNoteItem,     # The child model
    fields=('ingredient', 'quantity_received'), # Fields to include in each form
    extra=1,                  # Start with one extra form
    can_delete=False          # We don't need a delete checkbox for new items
)