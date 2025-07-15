from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from users.models import CustomUser, AuthToken
from articles.models import Article, Category
from .serializers import UserSerializer, ArticleSerializer, CategorySerializer
import json

class AuthView(APIView):
    @csrf_exempt
    def post(self, request):
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        user = authenticate(username=username, password=password)
        if user:
            token = AuthToken.objects.create(user=user)
            return Response({'token': token.token})
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_admin():
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response({'users': serializer.data})

    def post(self, request):
        if not request.user.is_admin():
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ArticleListView(APIView):
    def get(self, request):
        format = request.query_params.get('format', 'json')
        articles = Article.objects.filter(is_published=True)
        serializer = ArticleSerializer(articles, many=True)
        
        if format == 'xml':
            return Response(serializer.data, content_type='application/xml')
        return Response(serializer.data)

class CategoryArticleView(APIView):
    def get(self, request, category_id):
        format = request.query_params.get('format', 'json')
        category = Category.objects.get(id=category_id)
        articles = Article.objects.filter(category=category, is_published=True)
        serializer = ArticleSerializer(articles, many=True)
        
        if format == 'xml':
            return Response(serializer.data, content_type='application/xml')
        return Response({
            'category': CategorySerializer(category).data,
            'articles': serializer.data
        })