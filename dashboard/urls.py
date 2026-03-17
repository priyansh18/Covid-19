from django.contrib import admin
from django.urls import path
from covid import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.indexPage, name='home'),
    path('chatbot-page/', views.chatbotPage, name='chatbot_page'),
    path('chatBot/', views.chatBot, name='chatbot'),
    path('prediction/', views.prediction, name='prediction'),
    path('vaccination/', views.vaccination, name='vaccination'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'covid.views.handler404'
