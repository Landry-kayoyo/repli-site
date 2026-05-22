from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer
from .models import TipCategory, Tip


class TipCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TipCategory
        fields = '__all__'


class TipListSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Tip
        fields = ['id', 'title', 'subtitle', 'slug', 'author_name', 'category', 'category_name',
                  'cover_image_url', 'excerpt', 'tags', 'difficulty', 'status',
                  'is_featured', 'views_count', 'published_at', 'created_at']

    def get_cover_image_url(self, obj):
        if obj.cover_image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.cover_image.url) if request else obj.cover_image.url
        return None


class TipDetailSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    category_detail = TipCategorySerializer(source='category', read_only=True)
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Tip
        fields = '__all__'

    def get_cover_image_url(self, obj):
        if obj.cover_image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.cover_image.url) if request else obj.cover_image.url
        return None
