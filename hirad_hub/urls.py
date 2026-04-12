from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('user/', include('user.urls')),
    path('post/', include('post.urls')),
    path('note/', include('note.urls')),
    path('library/', include('library.urls')),
    path('roadmap/', include('roadmap.urls')),
    path('community/', include('community.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)