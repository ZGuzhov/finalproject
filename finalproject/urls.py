"""finalproject URL Configuration

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
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.views import LoginView, LogoutView
from polls.views import main, signup, polls_list, poll_detail, user_answers, statistics


urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'', main, name='main'),
    path(r'signup/', signup, name='signup'),
    path(r'login/', LoginView.as_view(template_name='login.html'), name='login'),
    path(r'logout/', LogoutView.as_view(), name='logout'),
    path(r'polls-list/<polls_choice>/', polls_list, name='polls-list'),
    path(r'poll/<int:poll_id>/<scroll_id>/', poll_detail, name='poll-detail'),
    path(r'answers/<int:poll_id>/<int:q_in_p_id>/<int:a_id>/', user_answers, name='user-answers'),
    path(r'statistics/', statistics, name='statistics'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)