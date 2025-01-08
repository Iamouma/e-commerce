from django.shortcuts import redirect

class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Example: Restrict access to admin URLs for non-staff users
        if request.path.startswith('/admin/') and not request.user.is_staff:
            return redirect('no_access')  # Redirect to a "No Access" page
        return self.get_response(request)
