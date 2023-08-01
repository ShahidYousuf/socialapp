from rest_framework.throttling import SimpleRateThrottle

class FriendRequestThrottle(SimpleRateThrottle):
    scope = 'friend_request'

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            return f"{self.scope}:{request.user.id}"
        else:
            return self.get_ident(request)

    def allow_request(self, request, view):
        if request.method == 'GET':
            return True
        return super().allow_request(request, view)