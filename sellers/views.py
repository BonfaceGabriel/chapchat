from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import SellerProfile
from .serializers import SellerProfileSerializer
from django.http import Http404

class SellerProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    API view for retrieving and updating the authenticated retailer's profile.
    """
    serializer_class = SellerProfileSerializer
    permission_classes = [permissions.IsAuthenticated] # Only authenticated users can access

    def get_object(self):
        """
        Override get_object to ensure a retailer can only access their own profile.
        It tries to get the profile linked to the currently authenticated user.
        If one doesn't exist (e.g., due to an issue with signal or an old user),
        it could optionally create it, or raise a 404.
        The signal should have created it, so this should typically find one.
        """
        try:
            # self.request.user is the authenticated User instance (from accounts.User)
            # .retailer_profile is the reverse accessor from the OneToOneField
            return self.request.user.seller_profile
        except SellerProfile.DoesNotExist:
            # This case should be rare if the post_save signal is working correctly
            # for all user creations.
            # For robustness, you could create it here if it doesn't exist:
            # profile = RetailerProfile.objects.create(user=self.request.user)
            # return profile
            # Or, raise a proper error if a profile is always expected:
            raise Http404("Retailer profile not found for this user.")

    # Optional: Customize update response or add partial update (PATCH) logic
    # def update(self, request, *args, **kwargs):
    #     partial = kwargs.pop('partial', False)
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #     return Response(serializer.data)