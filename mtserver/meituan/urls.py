from django.urls import path
from .views import MerchantViewSets,MerchantSearchView,CategoryView,LoginView,SMSCodeView,AddressViewsets,CreateOrderView,AlipayCallbackView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('merchant',viewset=MerchantViewSets,base_name='merchant')
router.register('address',viewset=AddressViewsets,base_name='address')



urlpatterns = [
    path("gen_code",SMSCodeView.as_view(),name="sms"),
    path("login",LoginView.as_view(),name="login"),
    path("search", MerchantSearchView.as_view(), name="search"),
    path("category/<int:merchant_id>", CategoryView.as_view(), name="search"),
    path("order",CreateOrderView.as_view(),name="order"),
    path("callback",AlipayCallbackView.as_view(),name="callback")
]+router.urls
