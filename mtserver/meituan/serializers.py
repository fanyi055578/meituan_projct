from rest_framework import serializers
from meituan.models import Merchant,Goods,GoodsCategory,Address
from rest_framework import serializers
from django.core.cache import cache
from django.contrib.auth import get_user_model
User = get_user_model()


class LoginSerializer(serializers.Serializer):
    telephone = serializers.CharField(max_length=11,min_length=11)
    smscode = serializers.CharField(max_length=4,min_length=4)

    def validate(self, attrs):
        telephone = attrs.get('telephone')
        smscode = attrs.get("smscode")
     #   cached_code = cache.get(telephone)
        cache_code = "1234"
        if cache_code != smscode:
            raise serializers.ValidationError("短信验证码错误！")
        return attrs

class MerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = "__all__"


class GoodsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Goods
        fields = "__all__"

    def create(self, validated_data):

        return Goods.objects.create(**validated_data)


class GoodsCategorySerializer(serializers.ModelSerializer):
    # merchant = MerchantSerializer(read_only=True)
    merchant_id = serializers.IntegerField()
    goods_list = GoodsSerializer(many=True,read_only=True)
    class Meta:
        model = GoodsCategory
        # fields = "__all__"
        exclude = ['merchant']

    def validate_merchant_id(self,value):
        if not Merchant.objects.filter(pk=value).exists():
            raise serializers.ValidationError("商家不存在！")
        return value

    def create(self,validated_data):
        merchant_id = validated_data.get('merchant_id')
        merchant = Merchant.objects.get(pk=merchant_id)
        category = GoodsCategory.objects.create(**validated_data,merchant=merchant)
        return category


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        include = ['telephone']


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        exclude = ['user']


class CreateOrderSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()
    goods_id_list = serializers.ListField(min_length=1)