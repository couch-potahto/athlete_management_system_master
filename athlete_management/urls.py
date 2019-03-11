"""athlete_management URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import include, path, re_path
from django.conf.urls import url
from training_area.views import team, athlete, coach, app
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('training_area.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', team.SignUpView.as_view(), name = 'signup'),
    path('accounts/signup/athlete/', athlete.AthleteSignUpView.as_view(), name = 'athlete_signup'),
    path('accounts/signup/coach/', coach.CoachSignUpView.as_view(), name = 'coach_signup'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
