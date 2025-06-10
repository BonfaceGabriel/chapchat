from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .serializers import UserRegistrationSerializer
from django.contrib.auth import get_user_model
# If you want to return tokens immediately upon registration:
# from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    """
    API view for seller user registration.
    Allows any user to create a new seller account.
    """
    queryset = User.objects.all() # Required for CreateAPIView, though not strictly used for creation logic here
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny] # Anyone can access this endpoint to register

    # Optional: Customize the response after successful creation
    # If you want to return tokens immediately after registration, you can uncomment and adapt this.
    # For MVP, just returning a success message is fine, and they can log in separately.
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True) # This will run your validate methods
        user = serializer.save() # This calls serializer.create()

        # You could generate tokens here if desired:
        # refresh = RefreshToken.for_user(user)
        # data = {
        #     'refresh': str(refresh),
        #     'access': str(refresh.access_token),
        #     'user': serializer.data # Or a simpler representation of the user
        # }
        # return Response(data, status=status.HTTP_201_CREATED)

        # For now, a simple success message:
        user_data = serializer.data # This will contain username, email, first_name, last_name (but not passwords)
        return Response(
            {
                "message": "User registered successfully. Please proceed to login.",
                "user": { # Return some basic user info (excluding password)
                    "username": user_data.get('username'),
                    "email": user_data.get('email'),
                    "first_name": user_data.get('first_name'),
                    "last_name": user_data.get('last_name')
                }
            },
            status=status.HTTP_201_CREATED
        )