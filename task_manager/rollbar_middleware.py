from rollbar.contrib.django.middleware import RollbarNotifierMiddleware


class CustomRollbarNotifierMiddleware(RollbarNotifierMiddleware):
    def get_payload_data(self, request, exc):
        """Add person (user) information to the payload."""
        payload_data = {}

        if request.user and not request.user.is_anonymous:
            payload_data['person'] = {
                'id': str(request.user.id),
                'username': request.user.username,
                'email': request.user.email,
            }

        return payload_data

    def get_extra_data(self, request, exc):
        """Add custom metadata to the payload."""
        return {
            'request_id': request.META.get('HTTP_X_REQUEST_ID'),
            'user_agent': request.META.get('HTTP_USER_AGENT'),
            'ip_address': self.get_client_ip(request),
        }

    def get_client_ip(self, request):
        """Extract client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')