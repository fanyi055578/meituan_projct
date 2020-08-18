from django.urls import path
#from .views import MerchantView,GoodsView,GoodsCategoryView
from .views import MerchantAPIView,GoodsCategoryMixinView,GoodsGenericView,MerchantViewSet,token_view
from rest_framework import routers
router = routers.DefaultRouter()
router.register('merchants',MerchantViewSet,base_name='merchants')

urlpatterns = [
     # path("merchant",MerchantView,name="merchant"),
     # path("goods",GoodsView,name="goods"),
     # path("goods_category",GoodsCategoryView,name="goods_category"),
     path("merchant",MerchantAPIView.as_view(),name="merchant"),
     path('merchant/<int:pk>',MerchantAPIView.as_view(),name="merchant"),
     path('goods_category',GoodsCategoryMixinView.as_view(),name='goods_category'),
     path('goods_category/<int:pk>',GoodsCategoryMixinView.as_view(),name='goods_category'),
     path('goods',GoodsGenericView.as_view(),name='goods'),
     path('token',token_view,name='token'),


]+router.urls