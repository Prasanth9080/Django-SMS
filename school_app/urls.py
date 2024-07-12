"""newapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
# from django.conf import settings
# from django.conf.urls.static import static
# from django.urls import include, path

# urlpatterns = [
#     path("accounts/", include("django.contrib.auth.urls")),
#     path("", include("apps.corecode.urls")),
#     path("student/", include("apps.students.urls")),
#     path("staff/", include("apps.staffs.urls")),
#     path("finance/", include("apps.finance.urls")),
#     path("result/", include("apps.result.urls")),
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



# from django.conf import settings
# from django.conf.urls.static import static
# from django.urls import include, path
# from django.contrib.auth import views as auth_views
# from . import views

# urlpatterns = [
#     path("accounts/", include("django.contrib.auth.urls")),
#     path("", include("apps.corecode.urls")),
#     path("student/", include("apps.students.urls")),
#     path("staff/", include("apps.staffs.urls")),
#     path("finance/", include("apps.finance.urls")),
#     path("result/", include("apps.result.urls")),


#     # path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
#     # path('signup/', views.signup, name='signup'),
#     # path('logout/', auth_views.LogoutView.as_view(), name='logout'),
# ]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.contrib import admin  # Import the admin module
from django.contrib.auth import views as auth_views
from . import views  
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("admin/", admin.site.urls),  # Add this line for the admin panel
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("apps.corecode.urls")),
    path("student/", include("apps.students.urls")),
    path("staff/", include("apps.staffs.urls")),
    path("finance/", include("apps.finance.urls")),
    path("result/", include("apps.result.urls")),
    path('index/', views.index, name='index'),  # This points to the index view
    path('password_change/', views.change_password, name='password_change'),
    path('password_change/done/', views.index, name='password_change_done'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
