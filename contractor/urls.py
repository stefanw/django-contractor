from django.urls import path

from .views import webhook

app_name = 'contractor'

urlpatterns = [
    path('webhook/<uuid:token>/', webhook, name='webhook'),
]
