from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
from rest_framework import routers
from receipts import views

router = routers.DefaultRouter()
router.register(r'items', views.ItemViewSet)
router.register(r'receipts', views.ReceiptViewSet, "Receipt")
router.register(r'profiles', views.ProfileViewSet, "Profile")
router.register(r'users', views.CreateUserView, "User")
router.register(r'exclude', views.ExcludeViewSet, "Exclude")

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^receipts/', include('receipts.urls')),
    url(r'^api/', include(router.urls)),
    #url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^$', views.OnePageAppView.as_view(), name='home'),
    url(r'^api/auth/$', views.AuthView.as_view(), name='authenticate'),
    url(r'^api/upload/', views.upload, name="upload"),

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)



if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
