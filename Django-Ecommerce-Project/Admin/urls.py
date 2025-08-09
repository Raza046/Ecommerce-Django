"""Furniture_Ecom URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from Admin import views as admin_views


urlpatterns = [

    path('', admin_views.AdminDashboardView.as_view(), name="AdminDashboard"),
    path('filter_graph', admin_views.FilterGraphView.as_view(), name="filter_graph"),

    # ADMIN STORE CAT, SUBCATEGORY
    path('store', admin_views.CategoryView.as_view(), name="store"),
    path('delete_category/<int:pk>', admin_views.DeleteCategory.as_view(), name="delete_category"),

    # path('subcategory/<str:id>', admin_views.SubCat, name="subcategory"),
    path('show_subcats/<int:pk>', admin_views.SubCategoryView.as_view(), name="show_subcats"),
    path('delete_subcat/<int:pk>', admin_views.DeleteSubCategoryView.as_view(), name="delete_subcat"),
    # path('add_cat', admin_views.AddCategory, name="add_cat"),
    # path('add_subcat', admin_views.SubCategoryView.as_view(), name="add_subcat"),


    path('products/<str:id>/variation', admin_views.ProductVariationView.as_view(), name="view_product_variation"),
    path('products/<str:id>/add-variation', admin_views.AddProductVariationView.as_view(), name="add_product_variation"),
    path('editproduct_var', admin_views.EditProductVariation, name="editproduct_var"),
    path('product/<str:id>/variants/create', admin_views.CreateProductVariantView.as_view(), name="create_new_product_variant"),
    path('add_image_product_var', admin_views.AddProductImages, name="add_image_product_var"),
    #path('delete-product-variant', admin_views.DeleteProductVar, name="delete_product_variant"),
    path('product-variant/<str:id>/delete', admin_views.DeleteProductVariantView.as_view(), name="delete_product_variant"),

    # Variations CRUD
    path('admin-panel/variations', admin_views.CreateVariationView.as_view(), name="admin_panel_variations_list"),
    path('admin-panel/variation/create', admin_views.CreateVariation, name="admin_panel_create_variation"),
    path('delete_variation/<str:id>', admin_views.RemoveVariation, name="delete_variation"),
    path('edit_variation/<str:id>', admin_views.EditVariation, name="edit_variation"),
    path('delete_variation_val/<str:id>', admin_views.RemoveVariationValue, name="delete_variation_val"),


    # Admin Add Product

    path('products/<int:pk>', admin_views.ProductView.as_view(), name="products"),
    path('add_variation', admin_views.Addvariation, name="add_variation"),

    # Coupon Page URL's
    path('admin-panel/coupons', admin_views.CouponView.as_view(), name="coupons"),
    path('admin-panel/coupons/create', admin_views.CouponCreateView.as_view(), name="create_coupons"),
    path('admin-panel/coupons/edit', admin_views.CouponView.as_view(), name="edit_coupons"),
    path('admin-panel/coupons/assign', admin_views.CouponView.as_view(), name="assign_coupons"),
    path('admin-panel/coupons/remove', admin_views.CouponView.as_view(), name="remove_coupon"),

    # Settings Page
    path('settings', admin_views.AdminSettingView.as_view(), name="settings"),
    path('edit_profile', admin_views.EditProfile, name="edit_profile"),

    # Customer Page
    path('customers', admin_views.CustomerView.as_view(), name="customers"),
    path('customers/order/<str:id>', admin_views.CustomerOrdersListView.as_view(), name="customers_orders"),

    # Complain Page
    path('complains', admin_views.ComplainListView.as_view(), name="complains"),

    # Team Page
    path('team', admin_views.TeamListView.as_view(), name="team"),
]
