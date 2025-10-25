from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import UserProfile
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    ChangePasswordSerializer, UserProfileSerializer,
    AuthTokenObtainPairSerializer
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User management.
    
    Endpoints:
    - GET /api/v1/users/ - List all users
    - POST /api/v1/users/ - Create a new user
    - GET /api/v1/users/{id}/ - Retrieve a user
    - PUT /api/v1/users/{id}/ - Update a user
    - DELETE /api/v1/users/{id}/ - Delete a user
    - POST /api/v1/users/register/ - Register a new user
    - POST /api/v1/users/{id}/change-password/ - Change password
    - GET /api/v1/users/me/ - Get current user
    """
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['role', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'first_name']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'register':
            return UserCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return UserUpdateSerializer
        elif self.action == 'change_password':
            return ChangePasswordSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action == 'register':
            return [AllowAny()]
        return super().get_permissions()
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """Register a new user."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current authenticated user."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        """Change user password."""
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'old_password': 'Senha incorreta.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response(
            {'detail': 'Senha alterada com sucesso.'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get', 'put', 'patch'])
    def profile(self, request, pk=None):
        """Get or update user profile."""
        user = self.get_object()
        profile = user.profile
        
        if request.method == 'GET':
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class AuthLoginView(TokenObtainPairView):
    """Authenticate user and return JWT tokens along with user details."""

    permission_classes = [AllowAny]
    serializer_class = AuthTokenObtainPairSerializer


class AuthRegisterView(APIView):
    """Handle user registration requests."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )


class AuthMeView(APIView):
    """Return the currently authenticated user."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class AuthLogoutView(APIView):
    """Acknowledge logout requests so clients can clear their tokens."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response(
            {'detail': 'Logout realizado com sucesso.'},
            status=status.HTTP_200_OK
        )

