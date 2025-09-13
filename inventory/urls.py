from django.urls import path
from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("ingredients/", views.IngredientListView.as_view(), name="ingredient_list"),
    path("ingredients/new/", views.IngredientCreateView.as_view(), name="ingredient_create"),
    path("menu/", views.MenuItemListView.as_view(), name="menuitem_list"),
    path("menu/new/", views.MenuItemCreateView.as_view(), name="menuitem_create"),
    path(
        "menu/<int:menu_item_pk>/add_ingredient/",
        views.RecipeRequirementCreateView.as_view(),
        name="reciperequirement_create",
    ),
    path("purchase/new/", views.PurchaseCreateView.as_view(), name="purchase_create"),
    path("grn/new/", views.GRNCreateView.as_view(), name="grn_create"),
]

