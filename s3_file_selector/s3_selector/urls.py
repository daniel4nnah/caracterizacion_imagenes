from django.urls import path, include
from . import views
urlpatterns = [
    # path("agregar", views.image_upload, name="image_upload"),
    path("", views.display_image, name="display_image"),
    path("update/ultrasond_images/<str:url>", views.update_metadata, name="update"),
    
]