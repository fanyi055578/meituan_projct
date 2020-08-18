import jwt
import time
from django.conf import settings
from rest_framework.authentication import BaseAuthentication,get_authorization_header
from rest_framework import exceptions
from django.contrib.auth import get_user_model
from jwt.exceptions import ExpiredSignatureError
MTUser = get_user_model()

def generate_jwt(user):
    expire_time = time.time() + 60*60*24*7
    return jwt.encode({"userid":user.pk,"exp":expire_time},key=settings.SECRET_KEY).decode('utf-8')


class JWTAuthentication(BaseAuthentication):
    keyword = 'JWT'

    def authenticate(self, request):
        jwts = request.META.get("HTTP_AUTHORIZATION")
        path = request.META.get("HTTP_PATH_INFO")
        print(request.META)
        print("dddddd",type(jwts))
        if path == '/login':
            return None
        if jwts==None :
           return None
        auth = jwts.split(" ")
        if not auth or auth[0].lower() != self.keyword.lower():
            msg = 'JWT 错误'

            raise exceptions.AuthenticationFailed(msg)

        if len(auth) == 1:
            msg = "不可用的JWT请求头！"
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = '不可用的JWT请求头！JWT Token中间不应该有空格！'
            raise exceptions.AuthenticationFailed(msg)

        try:
            jwt_token = auth[1]
            jwt_info = jwt.decode(jwt_token,settings.SECRET_KEY)
            print(jwt_info)
            userid = jwt_info.get('userid')
            try:
                # 绑定当前user到request对象上
                user = MTUser.objects.get(pk=userid)
                return user, jwt_token
            except:
                msg = '用户不存在！'
                raise exceptions.AuthenticationFailed(msg)
        except ExpiredSignatureError:
            msg = "JWT Token已过期！"
            raise exceptions.AuthenticationFailed(msg)



