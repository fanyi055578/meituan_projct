from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.authtoken.serializers import AuthTokenSerializer
from .jwtauth import generate_jwt,JWTAuthentication
from rest_framework.response import Response

from django.utils.timezone import now
from mtauth.serializer import UserSerializer
from meituan.models import Merchant,GoodsCategory,Goods
from .serializers import MerchantSerializer,GoodsCategorySerializer,GoodsSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.pagination import PageNumberPagination
import shortuuid
import os
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import action


class MerchantPagination(PageNumberPagination):
    page_size = 11
    page_query_param = "page"


class MerchantView(viewsets.ModelViewSet):
    queryset = Merchant.objects.all()
    serializer_class = MerchantSerializer
    # permission_classes = [IsAuthenticated,IsAdminUser]
    # authentication_classes = [JWTAuthentication]

    pagination_class = MerchantPagination


class LoginView(APIView):

    def post(self,request):
        serializer = AuthTokenSerializer(data=request.data)
        #这边serializer就已经去数据库读取完了用户名密码
        #并且进行了判断，确定用户名密码已经存在
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            user.last_login = now()
            user.save()
            jwt = generate_jwt(user)
            user_serializer = UserSerializer(user)

            return Response({"jwt":jwt,"user":user_serializer.data},status=200)

        else:
            return Response({"error":"账户或密码错误"},status=400)


class UploadView(APIView):
    def save_file(self,file):
        filename = shortuuid.uuid() + os.path.splitext(file.name)[-1]
        filepath = os.path.join(settings.MEDIA_ROOT,filename)
        with open(filepath,'wb') as fp:
            for files in file.chunks():
                fp.write(files)
        return self.request.build_absolute_uri(settings.MEDIA_URL + filename)

    def post(self,request):
        file = request.data.get('file')
        file_url = self.save_file(file)
        print(file_url)
        print("ddddd")
        return Response({"picture": file_url})



# Create,Update,Destroy,Retrieve
class CategoryViewSet(

    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin
):
    queryset = GoodsCategory.objects.all()
    serializer_class = GoodsCategorySerializer
    # permission_classes = [permissions.IsAuthenticated, IsEditorUser]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.goods_list.count() > 0:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)

    # /cms/category/merchant/<int:merchant_id>
    @action(['GET'],detail=False,url_path="merchant/(?P<merchant_id>\d+)")
    def merchant_category(self,request,merchant_id=None):
        queryset = self.get_queryset()
        seriazlier_class = self.get_serializer_class()
        categories = queryset.filter(merchant=merchant_id)
        serializer = seriazlier_class(categories,many=True)
        return Response(serializer.data)


class GoodsViewSet(viewsets.ModelViewSet):
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializer
