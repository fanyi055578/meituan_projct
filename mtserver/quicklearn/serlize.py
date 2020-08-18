from rest_framework import serializers
from meituan.models import Merchant,Goods,GoodsCategory

#
# class MerchantSerializer(serializers.Serializer):
#     id = serializers.IntegerField(read_only=True)
#     name = serializers.CharField(max_length=200,required=True)
#     address = serializers.CharField(max_length=200,required=True)
#     logo = serializers.CharField(max_length=200,required=True)
#     notice = serializers.CharField(max_length=200,allow_blank=True)
#     up_send = serializers.DecimalField(default=0,max_digits=6,decimal_places=2)
#     lon = serializers.FloatField(required=True)
#     lat = serializers.FloatField(required=True)
#
#     def update(self, instance, validated_data):
#         instance.name = validated_data.get("name",instance.name)
#         instance.address = validated_data.get("address",instance.address)
#         instance.logo = validated_data.get("logo",instance.logo)
#         instance.notice = validated_data.get("notice",instance.notice)
#         instance.up_send = validated_data.get("up_send",instance.up_send)
#         instance.lon = validated_data.get("lon",instance.lon)
#         instance.lat = validated_data.get("lat",instance.lat)
#         instance.save()
#         return instance
#
#     def create(self, validated_data):
#         data = Merchant.objects.create(**validated_data)
#         #validated_data 本来是字典数据  但是加上**后就会变为关键字形数据
#         #    "name":"张珊"  变为 name:"张珊"
#         return data


# Serializer的构造函数的参数：
# 1. instance：需要传递一个ORM对象，或者是一个queryset对象。用来将ORM模型序列化成JSON的
# 2. data：把需要验证的数据传给data，用来验证这些数据是不是符合要求。
# 3. many：如果instance是一个queryset对象，那么就需要设置为True，否则为False

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
    merchant = MerchantSerializer(read_only=True)
    goods_list = GoodsSerializer(many=True,required=False)
    merchant_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = GoodsCategory
        fields = "__all__"

    def validate_merchant_id(self,value):
        if Merchant.objects.filter(pk=value).exsists():
            raise serializers.ValidationError("merchant not exist")
        else:
            return value

    def create(self, validated_data):
        merchant_id = validated_data.get("merchant_id")
        merchant = Merchant.objects.filter(pk=merchant_id)
        category = GoodsCategory.objects.create(name=validated_data.get("name"),merchant=merchant)
        return category


