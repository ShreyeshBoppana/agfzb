from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'djangoapp'
urlpatterns = [
    # route is a string contains a URL pattern
    # view refers to the view function
    # name the URL

    # path for about view
    path(route='about', view=views.about, name='about'),

    # path for contact us view

     path(route='contact', view=views.contact, name='contact'),
    # path for registration
    path('create_superuser/', view=views.create_superuser, name='create_superuser'),

    # path for login
    path('login/', view=views.custom_login, name='login'),

    # path for logout

    path('logout/', view=views.custom_logout, name='logout'),

    # path for dealer reviews view
    path('deal/', view=views.get_dealerships, name='deal'),

    # path for add a review view

    path('review/<int:id>/', views.get_reviews, name='reviews'),

     path('sent/<int:id>', views.get_sentiment, name='sent'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)