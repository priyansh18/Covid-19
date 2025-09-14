"""dashboard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, re_path
from covid import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.indexPage,name='home'),
    re_path(r'^chatbot-page/', views.chatbotPage,name="chatbot_page"),
    re_path(r'^chatBot/', views.chatBot,name="chatbot"),
    re_path(r'^prediction/', views.prediction,name="prediction"),
    re_path(r'^vaccination/', views.vaccination,name="vaccination"),
    path('selectCountry',views.singleCountry,name="single"),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
