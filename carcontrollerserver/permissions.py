from rest_framework import permissions

class IsAuthenticatedPost(permissions.IsAuthenticated):        

    def has_permission(self, request, view):
        # Allow all methods different from POST
        if request.method != 'POST':
            return True

        return super().has_permission(request, view)

class IsNotAuthenticatedPost(permissions.IsAuthenticated):        

    def has_permission(self, request, view):
        # Allow only post requests
        if request.method == 'POST':
            return True

        return super().has_permission(request, view)