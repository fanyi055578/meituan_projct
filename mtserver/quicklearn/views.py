from meituan import models
# Create your views here.
from .serlize import MerchantSerializer,GoodsSerializer,GoodsCategorySerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics,mixins
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.authentication import BasicAuthentication
from mt_cms.jwtauth import JWTAuthentication,generate_jwt
from django.contrib.auth import get_user_model
from .mypermition import MyPermission

User = get_user_model()


class MerchantViewSet(viewsets.ModelViewSet):
    queryset = models.Merchant.objects.all()
    serializer_class = MerchantSerializer
    authentication_classes = [JWTAuthentication,BasicAuthentication]
    permission_classes = [MyPermission]

@api_view(['GET'])
def token_view(request):
    token = generate_jwt(User.objects.first())
    print(User.objects.first())
    return Response({"token":token})


class MerchantAPIView(APIView):

    def get_object(self, pk):
        try:
            return models.Merchant.objects.get(pk=pk)
        except models.Merchant.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND

    def get(self, request,pk=None):
        if pk:
            res = self.get_object(pk)
            data = MerchantSerializer(res)
            return Response(data.data,status.HTTP_200_OK)
        else:
            res = models.Merchant.objects.all()
            data = MerchantSerializer(res,many=True)
            return Response(data.data,status.HTTP_200_OK)

    def post(self, request):
        res = MerchantSerializer(data=request.data)
        if res.is_valid():
            res.save()
            return Response(request.data, status=status.HTTP_200_OK)
        else:
            return Response("post err",status=status.HTTP_400_BAD_REQUEST)

    def put(self, request,pk=None):
        res = self.get_object(pk)
        data = MerchantSerializer(res,data=request.data)
        if data.is_valid():
            data.save()
            return Response(data.data,status=status.HTTP_200_OK)
        else:
            return Response("PUT ERR",status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        res = self.get_object(pk)
        res.delete()
        return Response('delete ok',status=status.HTTP_200_OK)


class GoodsCategoryMixinView(generics.GenericAPIView,mixins.ListModelMixin,mixins.CreateModelMixin,mixins.DestroyModelMixin,mixins.UpdateModelMixin
                             ,mixins.RetrieveModelMixin):
    queryset = models.GoodsCategory.objects.all()
    serializer_class = GoodsCategorySerializer

    def get(self,request,pk=None):
        if pk:
            return self.retrieve(pk)
        else:
            return self.list(request)

    def post(self,request):
        return self.create(request)

    # def perform_create(self, serializer):
    #     #     serializer.save(created=self.request.user)
    #    一定注意在重写create方法的时候写的是这个方法
    def put(self,request,pk):
        return self.update(request)

    def delete(self,request,pk):
        return self.destroy(request)


class GoodsGenericView(generics.ListAPIView,generics.CreateAPIView,generics.DestroyAPIView,generics.RetrieveAPIView,generics.UpdateAPIView):
    queryset = models.Goods.objects.all()
    serializer_class = GoodsSerializer





#
# @require_http_methods(['GET','POST'])
# def MerchantView(request):
#     if request.method=="GET":
#         data = models.Merchant.objects.all()
#         res = MerchantSerializer(instance=data,many=True)
#         return JsonResponse(data=res.data,status=200,safe=False)
#     else:
#         data = MerchantSerializer(data=request.POST)
#         if data.is_valid():
#             data.save()
#             return JsonResponse(data=data.data, status=200)
#         else:
#             return JsonResponse(data.errors,status=400)
#
#
# @require_http_methods(['GET','POST'])
# def GoodsView(request):
#     if request.method=="GET":
#         Goods = models.Goods.objects.all()
#         data = GoodsSerializer(instance=Goods,many=True)
#         return JsonResponse(data.data,status=200,safe=False)
#     else:
#         data = GoodsSerializer(data=request.POST)
#         if data.is_valid():
#             data.save()
#             return JsonResponse(data.data,status=200)
#         else:
#             return JsonResponse(data.errors,status=400)
#
#
# @require_http_methods(['GET','POST'])
# def GoodsCategoryView(request):
#     if request.method=="GET":
#         category = models.GoodsCategory.objects.all()
#         data = GoodsCategorySerializer(instance=category,many=True)
#         return JsonResponse(data.data,status=200,safe=False)
#     else:
#         data = GoodsCategorySerializer(data=request.POST)
#         if data.is_valid():
#             data.save()
#             return JsonResponse(data.data,status=200)
#         else:
#             return JsonResponse(data.errors,status=400)