from django.urls import path

from .views import keycloak_login, callback, refresh_token, keycloak_logout

urlpatterns = [
    path('login/', keycloak_login, name="login"),
    path('callback/', callback, name="callback"),
    path('refresh_token/', refresh_token, name="refresh_token"),
    path('logout/', keycloak_logout, name="logout"),
]