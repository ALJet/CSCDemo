"""CSCDemo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from django.urls import path

from myApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.login_view,name='login'),
    path('index/',views.Index.as_view(),name='index'),
    path('page/<int:page>',views.Index.as_view(),name='index'),
    path('search/<str:keyword>/',views.SearchView.as_view(),name='search'),
    path('search/<str:keyword>/page/<int:page>',views.SearchView.as_view(),name='search'),
    path('upload/',views.upload_file,name='upload_file'),
    path('upload/upload_data',views.upload_data,name='upload_data'),
    path('edit/<int:pk>/',views.edit_lpg,name='edit'),
    path('accounts/login/',views.login_view,name='login'),
    path('login/',views.login_view,name='login'),
    path('logout/',views.login_view,name='logout'),
    path('export/',views.export_excel,name='export_excel'),
    path('overload/',views.overload.as_view(),name='overload'),

]

