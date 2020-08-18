from rest_framework import throttling


class SMSCodeRateThrottle(throttling.SimpleRateThrottle):
    scope = 'smscode'

    def get_cache_key(self, request, view):
        telephone = request.GET.get('tel')
        if telephone:
            ident = telephone
        else:
            ident = self.get_ident(request)

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }