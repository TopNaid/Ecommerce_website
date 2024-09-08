from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("listing/<int:listing_id>/", views.listing_detail, name="listing_detail"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create/", views.create_listing, name="create_listing"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("category/", views.category_list, name="category_list"),
     path('categories/<str:category_name>/', views.category_detail, name='category_detail')
]
