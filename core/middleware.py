# Create middleware.py in your app
class SessionCleanupMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Clear any stale session data
        if not request.user.is_authenticated and "cart" in request.session:
            del request.session["cart"]

        return response
