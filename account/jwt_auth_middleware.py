from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model
from channels.middleware import BaseMiddleware

User = get_user_model()

class JWTWebsocketMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Extract token from query string
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]
        
        # Also check headers (alternative method)
        if not token:
            headers = dict(scope.get('headers', []))
            for key, value in headers.items():
                if key == b'authorization':
                    token = value.decode().split(' ')[1] if ' ' in value.decode() else None
                    break
        
        # Authenticate user with JWT
        scope['user'] = await self.get_user_from_token(token)
        
        return await super().__call__(scope, receive, send)
    
    @database_sync_to_async
    def get_user_from_token(self, token):
        print('token****',token)
        try:
            if not token:
                return AnonymousUser()
            
            # Validate token
            UntypedToken(token)
            
            # Get user from token
            jwt_auth = JWTAuthentication()
            validated_token = jwt_auth.get_validated_token(token)
            user = jwt_auth.get_user(validated_token)
            
            return user
            
        except (InvalidToken, TokenError, Exception) as e:
            print(f"JWT Authentication error: {e}")
            return AnonymousUser()