from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs

User = get_user_model()

@database_sync_to_async
def get_user_from_token(token_string):
    """
    Asynchronously gets a user from a JWT access token.
    """
    try:
        # Validate the token
        access_token = AccessToken(token_string)
        # Get the user ID from the token's payload
        user_id = access_token.get('user_id')
        # Fetch the user from the database
        return User.objects.get(id=user_id)
    except (InvalidToken, TokenError, User.DoesNotExist):
        # If token is invalid or user doesn't exist, return AnonymousUser
        return AnonymousUser()

class TokenAuthMiddleware:
    """
    Custom middleware for Django Channels that authenticates users using a JWT token
    passed in the query string.
    """
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # `scope` is the connection information dictionary
        # The query string is a bytes object, so we decode it
        query_string = scope.get('query_string', b'').decode('utf-8')
        # Parse the query string into a dictionary
        query_params = parse_qs(query_string)
        
        # Get the token from the query parameters
        token = query_params.get('token', [None])[0]

        if token:
            # If a token was provided, try to get the user
            scope['user'] = await get_user_from_token(token)
        else:
            scope['user'] = AnonymousUser()

        # Call the next middleware or consumer in the stack
        return await self.inner(scope, receive, send)