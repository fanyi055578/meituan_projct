from django.urls import path
from .views import LoginView,MerchantView,UploadView,CategoryViewSet,GoodsViewSet
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register('merchant',viewset=MerchantView,base_name='merchant')
router.register('category',viewset=CategoryViewSet,base_name="category")
router.register('goods',viewset=GoodsViewSet,base_name='goods')

urlpatterns = [
    path('login',LoginView.as_view(),name="login"),
    path('upload',UploadView.as_view(),name='upload')

]+router.urls
