
from rest_framework import viewsets
from django.db.models import Q
from api.base import UnifiedModelViewSet
from django.contrib.auth import get_user_model
from rest_framework.permissions import DjangoModelPermissions


from rest_framework import viewsets
from django.db.models import Q
from api.base import UnifiedModelViewSet
from django.contrib.auth import get_user_model
from rest_framework.permissions import DjangoModelPermissions
from users.models import User as CustomUser

class BaseViewSet(UnifiedModelViewSet):
    """
    Base ViewSet that implements centralized Data Visibility logic.
    Inherits from UnifiedModelViewSet to keep existing unified behavior.
    """
    
    def get_queryset(self):
        # 1. Get the base queryset from the specific ViewSet
        queryset = super().get_queryset()
        

        user = self.request.user
        
        # 2. If user is not authenticated, standard DRF permissions will handle rejection later,
        #    but we can just return none or let it pass to permissions.
        if not user.is_authenticated:
             return queryset


        # Force fetch the correct User model instance to ensure we have all fields (like data_visibility)
        # This handles cases where request.user might be a SimpleLazyObject or a base model instance in MTI scenarios.
        extended_user = user
        try:
            # Try to get the extended user (child model) which holds the extra fields
            if user.id:
                 extended_user = CustomUser.objects.get(id=user.id)
        except CustomUser.DoesNotExist:
            # If no extended user exists (e.g. legacy admin user), fall back to base user
            pass
        
        # 3. Superusers see everything
        if extended_user.is_superuser:
            return queryset


        # 4. Check Data Visibility Permission
        
        # Robustly get visibility from the EXTENDED user
        # If attribute missing or empty/None, default to 'self'
        raw_visibility = getattr(extended_user, 'data_visibility', None)
        
        # DEBUG LOGGING RAW
        print(f"DEBUG MTI: ID={user.id} BaseUser={user.username}, ExtendedUser={extended_user.username} (IsCustom={isinstance(extended_user, CustomUser)}), Visibility={repr(raw_visibility)}")

        visibility = raw_visibility
        if not visibility:
            visibility = 'self'
            

        # DEBUG LOGGING (Remove in production)
        # print(f"DEBUG VISIBILITY: ID={user.id} User={user.username}, Role='{visibility}', Superuser={user.is_superuser}, Model={self.queryset.model.__name__}")

        if visibility == 'all':
            return queryset

        elif visibility == 'department':
            # Case A: We are querying the User model itself
            # Check against CustomUser, or if the queryset model IS the extended user model
            if issubclass(self.queryset.model, get_user_model()) or self.queryset.model == CustomUser:
                # Users see other users in their same structures
                user_structures = extended_user.stractures.all()
                if not user_structures.exists():
                     # If I am not in any structure, and I ask for department -> I see nothing or just myself?
                     # Let's say I see just myself to be safe/consistent
                     return queryset.filter(id=extended_user.id)
                     
                return queryset.filter(stractures__in=user_structures).distinct()
            
            # Case B: We are querying a standard business model (inheriting BaseModel)
            # We assume it has a 'created_by' field pointing to a User
            elif hasattr(self.queryset.model, 'created_by'):
                # See records created by users who are in the same structures OR created by the user themselves
                user_structures = extended_user.stractures.all()
                
                if not user_structures.exists():
                    # If I am not in any structure, I only see my own data
                    return queryset.filter(created_by=user)

                # Use a subquery/filter to find valid users first
                # This avoids potential issues with MTI traversal in filter(created_by__stractures__in=...)
                users_in_same_structures = CustomUser.objects.filter(stractures__in=user_structures)

                return queryset.filter(
                    Q(created_by=user) | Q(created_by__in=users_in_same_structures)
                ).distinct()
            
            # Case C: Model doesn't have created_by?
            else:
                 return queryset

        elif visibility == 'self':
            # Case A: We are querying the User model
            if issubclass(self.queryset.model, get_user_model()) or self.queryset.model == CustomUser:
                # I can only see myself
                return queryset.filter(id=user.id)
            
            # Case B: Standard model
            elif hasattr(self.queryset.model, 'created_by'):
                return queryset.filter(created_by=user)
            
            else:
                return queryset

        # Fallback
        return queryset

