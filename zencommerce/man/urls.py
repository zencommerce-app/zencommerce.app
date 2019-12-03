from django.urls import path

from . import views

urlpatterns = [
    path('oauth_callback/<int:shop_id>/', views.oauth_callback, name='oauth_callback'),
    path('etsy_response/<int:shop_id>/', views.etsy_response, name='etsy_response'),

    path('run_job/<int:shop_id>/', views.run_job, name='run_job'),
]
