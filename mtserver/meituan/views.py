from django.shortcuts import render
from .serializers import MerchantSerializer,GoodsSerializer,GoodsCategorySerializer,AddressSerializer,CreateOrderSerializer
from mtauth.serializer import UserSerializer
from .models import Goods,GoodsCategory,Merchant,Address,Order
from rest_framework import viewsets,mixins
from rest_framework.pagination import PageNumberPagination
from rest_framework import views
from utils.CCPSDK import CCPRestSDK
from rest_framework.response import Response
import random
from rest_framework import status
from .throttles import SMSCodeRateThrottle
from django.contrib.auth import get_user_model
from django.core.cache import cache
from .serializers import LoginSerializer
from django.utils.timezone import now
from mt_cms.jwtauth import generate_jwt
from rest_framework import viewsets,mixins
from mt_cms.jwtauth import JWTAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
from rest_framework import filters
from .serializers import GoodsCategorySerializer
from rest_framework import permissions
from rest_framework.decorators import action
from django.conf import settings
from django.shortcuts import redirect
from alipay import AliPay
import os
from redis import Redis
# xtredis = Redis(host='111.231.107.198', port=6379)
# # 添加一个值进去，并且设置过期时间为60秒，如果不设置，则永远不会过期
# xtredis.set('username', 'xiaotuo', ex=60)
# # 获取一个值
# xtredis.get('username')


User = get_user_model()


class SMSCodeView(views.APIView):
    throttle_classes = [SMSCodeRateThrottle]
    def __init__(self,*args,**kwargs):
        super(SMSCodeView, self).__init__(*args,**kwargs)
        self.numbers = ['0','1','2','3','4','5','6','7','8','9']

    def generate_sms_code(self):
        return "".join(random.choices(self.numbers, k=4))

    def get(self,request):
        # /smscode?tel=xxxxx
        telephone = request.GET.get("tel")
        if telephone:
            accountSid = "8a216da86c65c73b016c7564c9bf0b55"
            accountToken = "116e80e3d8504e37b7b75544983bd84d"
            appId = "8a216da86c65c73b016c7564ca150b5c"
            code = self.generate_sms_code()
            cache.set(telephone,code,60*5)
            print(code)
            return Response()
            # rest = CCPRestSDK.REST(accountSid,accountToken,appId)
            # result = rest.sendTemplateSMS(telephone,[code,5],"1")
            # if result['statusCode'] == '000000':
            #     return Response()
            # else:
            #     return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class LoginView(views.APIView):
    def generate_number(self):
        numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        return "".join(random.choices(numbers,k=6))

    def post(self,request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            telephone = serializer.validated_data.get('telephone')
            try:
                user = User.objects.get(telephone=telephone)
                user.last_login = now()
                user.save()
            except:
                username = "美团用户"+self.generate_number()
                password = ""
                user = User.objects.create(username=username,password=password,telephone=telephone,last_login=now())
            serializer = UserSerializer(user)
            token = generate_jwt(user)
            return Response({"user":serializer.data,"token":token})
        else:
            print(serializer.errors)
            return Response(data={"message":dict(serializer.errors)},status=status.HTTP_400_BAD_REQUEST)

class MerchantPagination(PageNumberPagination):
    page_size = 8
    page_query_param = "page"


class MerchantViewSets(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin
):
    queryset = Merchant.objects.all()
    serializer_class = MerchantSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MerchantPagination


class MerchantSearchView(generics.ListAPIView):
    class MerchantSearchFilter(filters.SearchFilter):
        search_param = "q"
    queryset = Merchant.objects.all()
    serializer_class = MerchantSerializer
    filter_backends = [MerchantSearchFilter]
    search_fields = ['name','categories__name','categories__goods_list__name']


class CategoryView(views.APIView):
    def get(self,request,merchant_id=None):
        categories = GoodsCategory.objects.filter(merchant=merchant_id)
        serializer = GoodsCategorySerializer(categories,many=True)
        return Response(serializer.data)


class AddressViewsets(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        print("address=",user.address.all())
        return user.address.all()

    def perform_create(self,serializer):
        is_default = serializer.validated_data.get('is_default')
        if is_default:
            self.request.user.address.update(is_default=False)
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        is_default = serializer.validated_data.get('is_default')
        if is_default:
            self.request.user.address.update(is_default=False)
        serializer.save()

    # /address/default
    @action(['GET'], detail=False, url_path='default')
    def default_address(self, request):
        try:
            address = self.request.user.address.get(is_default=True)
        except:
            address = self.request.user.address.first()
        serializer = self.serializer_class(address)
        return Response(serializer.data)



class CreateOrderView(views.APIView):
    def post(self,request):
        serializer = CreateOrderSerializer(data=request.data)
        if serializer.is_valid():
            address_id = serializer.validated_data.get('address_id')
            goods_id_list = serializer.validated_data.get('goods_id_list')
            address = Address.objects.get(pk=address_id)
            goods_list = Goods.objects.filter(pk__in=goods_id_list)
            goods_count = 0
            total_price = 0
            for goods in goods_list:
                goods_count += 1
                total_price += goods.price
            order = Order.objects.create(
                address=address,
                goods_count=goods_count,
                total_price = total_price,
            )
            order.goods_list.set(goods_list)
            order.save()
            app_private_key_string = open(os.path.join(settings.BASE_DIR,'keys','app_private_key.txt'),'r').read()
            alipay_public_key_string = open(os.path.join(settings.BASE_DIR,'keys','alipay_public_key.txt'),'r').read()
            alipay = AliPay(
                appid="2021000117684771",
                app_notify_url=None,  # 默认回调url
                app_private_key_string=app_private_key_string,
                # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
                alipay_public_key_string=alipay_public_key_string,
                sign_type="RSA2",  # RSA 或者 RSA2
                debug = True  # 默认False
            )
            # 手机网站支付，需要跳转到：
            # 真实环境：https://openapi.alipay.com/gateway.do? + order_string
            # 沙箱环境：https://openapi.alipaydev.com/gateway.do? + order_string
            order_string = alipay.api_alipay_trade_wap_pay(
                out_trade_no=order.pk,
                total_amount=str(order.total_price),
                subject="测试支付商品",
                return_url="http://111.231.107.198/callback",
                notify_url="http://111.231.107.198/callback"  # 可选, 不填则使用默认notify url
            )
            pay_url = "https://openapi.alipaydev.com/gateway.do?" + order_string
            return Response({"pay_url":pay_url})
        else:
            return Response({"message":dict(serializer.errors)},status=status.HTTP_400_BAD_REQUEST)
#
class AlipayCallbackView(views.APIView):
    def get(self,request):
        return redirect("/")

    def post(self,request):
        data = request.data
        # print(data)
        alipay_data = {}
        for key,value in data.items():
            alipay_data[key] = value
        sign = alipay_data.pop("sign")
        app_private_key_string = open(os.path.join(settings.BASE_DIR, 'keys', 'app_private_key.txt'), 'r').read()
        alipay_public_key_string = open(os.path.join(settings.BASE_DIR, 'keys', 'alipay_public_key.txt'), 'r').read()
        alipay = AliPay(
            appid="2016100100640619",
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=True  # 默认False
        )
        success = alipay.verify(alipay_data,sign)
        if success and alipay_data["trade_status"] in ("TRADE_SUCCESS", "TRADE_FINISHED"):
            order_id = alipay_data.get('out_trade_no')
            order = Order.objects.get(pk=order_id)
            order.order_status = 4
            order.pay_method = 2
            order.save()
            return Response()
        else:
            return Response({"message":"订单支付失败！"},status=status.HTTP_400_BAD_REQUEST)