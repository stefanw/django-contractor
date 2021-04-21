from django.urls import path

from .views import webhook, redirect_current

app_name = 'contractor'

urlpatterns = [
    path('webhook/<uuid:token>/', webhook, name='webhook'),
    path('file/<slug:slug>/current/<path:path>', redirect_current,
         name='redirect_current'),
]
