from rest_framework import permissions

class isMentor(permissions.BasePermission):
    def has_permission(self,request,view):
        if request.method in permissions.SAFE_METHODS:
            return True

        else:
            print(str(request.user.profile))
            return (
                request.user.is_authenticated
                and hasattr(request.user,"profile")  
                and request.user.profile.role == "Mentor")