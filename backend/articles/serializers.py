from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer
from .models import Category, Article


class CategorySerializer(serializers.ModelSerializer):
    articles_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = '__all__'

    def get_articles_count(self, obj):
        return obj.articles.filter(status='published').count()


class ArticleListSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['id', 'title', 'subtitle', 'slug', 'author_name', 'category', 'category_name',
                  'category_color', 'cover_image_url', 'excerpt', 'tags', 'status',
                  'is_featured', 'views_count', 'read_time', 'published_at', 'created_at']

    def get_cover_image_url(self, obj):
        if obj.cover_image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.cover_image.url) if request else obj.cover_image.url
        return None


class ArticleDetailSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    category_detail = CategorySerializer(source='category', read_only=True)
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = '__all__'

    def get_cover_image_url(self, obj):
        if obj.cover_image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.cover_image.url) if request else obj.cover_image.url
        return None
