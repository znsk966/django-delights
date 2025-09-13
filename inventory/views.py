from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, View
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from .models import(
    Ingredient,
    MenuItem,
    RecipeRequirement,
    Purchase,
    GoodsReceiptNote,
    GoodsReceiptNoteItem
)
from .forms import(
    IngredientForm,
    MenuItemForm,
    RecipeRequirementForm,
    PurchaseForm,
    GoodsReceiptNoteForm,   
    GRNItemFormSet
)

# Create your views here.

class HomeView(LoginRequiredMixin, ListView):
    """
    Displays a home dashboard page.
    For now, it will be simple, but we can add more stats later.
    """
    model = Purchase # We can use any model, Purchase is fine for now
    template_name = 'inventory/home.html'
    context_object_name = 'purchases' # We'll need this for the template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Dashboard"
        return context

class IngredientListView(LoginRequiredMixin, ListView):
    """
    Displays a list of all ingredients in the inventory.
    """
    model = Ingredient
    template_name = 'inventory/ingredient_list.html'
    context_object_name = 'ingredients' # Makes it easier to loop in the template

class MenuItemListView(LoginRequiredMixin, ListView):
    """
    Displays a list of all menu items.
    """
    model = MenuItem
    template_name = 'inventory/menuitem_list.html'
    context_object_name = 'menu_items' # Easier to reference in the template

class IngredientCreateView(LoginRequiredMixin, CreateView):
    model = Ingredient
    template_name = "inventory/ingredient_form.html"
    form_class = IngredientForm
    success_url = "/ingredients/" # Redirect to the ingredient list after a successful creation

class MenuItemCreateView(LoginRequiredMixin, CreateView):
    model = MenuItem
    template_name = "inventory/menuitem_form.html"
    # Django will automatically look for a variable named 'form' in the template
    # but we can be explicit with context_object_name if we want.
    # We also need to specify the form_class.
    form_class = MenuItemForm
    success_url = reverse_lazy('menuitem_list')

class RecipeRequirementCreateView(LoginRequiredMixin, CreateView):
    model = RecipeRequirement
    template_name = "inventory/reciperequirement_form.html"
    form_class = RecipeRequirementForm

    def get_success_url(self):
        # Redirect back to the menu list after adding an ingredient
        return reverse_lazy('menuitem_list')

    def form_valid(self, form):
        # The URL will contain the pk of the menu item, e.g., /menu/1/add_ingredient/
        # We retrieve it from the URL kwargs.
        menu_item = MenuItem.objects.get(pk=self.kwargs['menu_item_pk'])
        # Associate the new recipe requirement with the correct menu item.
        form.instance.menu_item = menu_item
        return super().form_valid(form)
    
class PurchaseCreateView(LoginRequiredMixin, View):
    template_name = "inventory/purchase_form.html"

    def get(self, request):
        form = PurchaseForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = PurchaseForm(request.POST)
        if form.is_valid():
            # Get the selected menu item from the form
            menu_item = form.cleaned_data["menu_item"]
            
            # Get all the recipe requirements for this menu item
            requirements = menu_item.reciperequirement_set.all()

            # Check if there are enough ingredients in the inventory
            for req in requirements:
                # THIS IS THE CORRECTED LINE:
                if req.ingredient.quantity_available < req.quantity_required:
                    # If any ingredient is insufficient, add an error to the form
                    form.add_error(None, f"Not enough {req.ingredient.name} in stock.")
                    # Re-render the page with the form and the error message
                    return render(request, self.template_name, {"form": form})

            # If all ingredients are available, proceed with the purchase
            purchase = form.save()

            # Update the inventory
            for req in requirements:
                ingredient = req.ingredient
                # AND THIS IS THE OTHER CORRECTED LINE:
                ingredient.quantity_available -= req.quantity_required
                ingredient.save()

            return redirect("home") # Redirect to the dashboard

        # If the form is not valid, re-render the page with the form and its errors
        return render(request, self.template_name, {"form": form})
    
class GRNCreateView(LoginRequiredMixin, View):
    template_name = 'inventory/grn_form.html'

    def get(self, request, *args, **kwargs):
        form = GoodsReceiptNoteForm()
        formset = GRNItemFormSet(instance=GoodsReceiptNote())
        return render(request, self.template_name, {'form': form, 'formset': formset})

    def post(self, request, *args, **kwargs):
        form = GoodsReceiptNoteForm(request.POST)
        # Create a blank GRN instance to attach the formset to
        grn_instance = GoodsReceiptNote()
        formset = GRNItemFormSet(request.POST, instance=grn_instance)

        if form.is_valid() and formset.is_valid():
            try:
                # Use a database transaction to ensure all updates succeed or none do
                with transaction.atomic():
                    # First, save the main GRN form
                    grn = form.save()

                    # Now, save the formset, linking each item to the saved GRN
                    instances = formset.save(commit=False)
                    for item in instances:
                        item.grn = grn
                        item.save()

                        # Update the inventory for each ingredient
                        ingredient = item.ingredient
                        ingredient.quantity_available += item.quantity_received
                        ingredient.save()
            except Exception as e:
                # If anything goes wrong, the transaction will be rolled back
                print(f"Error processing GRN: {e}")
                # You could add a more user-friendly error message here
                return render(request, self.template_name, {'form': form, 'formset': formset, 'error': 'An error occurred.'})

            return redirect('ingredient_list')

        # If forms are not valid, re-render the page with errors
        return render(request, self.template_name, {'form': form, 'formset': formset})

