from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from articles.models import Article, Category
from users.models import CustomUser, AuthToken
from .serializers import ArticleSerializer, CategorySerializer, UserSerializer

class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Article.objects.filter(is_published=True).order_by('-pub_date')
    serializer_class = ArticleSerializer
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        category_id = request.query_params.get('category')
        if not category_id:
            return Response({'error': 'Category parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        category = get_object_or_404(Category, id=category_id)
        articles = self.queryset.filter(category=category)
        serializer = self.get_serializer(articles, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def grouped_by_category(self, request):
        categories = Category.objects.all()
        result = []
        
        for category in categories:
            articles = self.queryset.filter(category=category)
            if articles.exists():
                serializer = self.get_serializer(articles, many=True)
                result.append({
                    'category': CategorySerializer(category).data,
                    'articles': serializer.data
                })
        
        return Response(result)

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]
    
    def list(self, request, *args, **kwargs):
        if not request.user.is_admin():
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        return super().list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        if not request.user.is_admin():
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

class AuthenticateView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        if user is not None:
            token = AuthToken.create_token(user)
            return Response({'token': token.token}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)