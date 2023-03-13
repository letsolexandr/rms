"""test_proj URL Configuration

The `urlpatterns` list routes URLs to viewsets. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function viewsets
    1. Add an import:  from my_app import viewsets
    2. Add a URL to urlpatterns:  url(r'^$', viewsets.home, name='home')
Class-based viewsets
    1. Add an import:  from other_app.viewsets import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.urls import re_path as url
from .views import protectedMedia

urlpatterns = [
    url(r'media/', protectedMedia),
    
]