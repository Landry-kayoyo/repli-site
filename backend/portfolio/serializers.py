from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer
from .models import PortfolioCategory, PortfolioItem, PortfolioImage


class PortfolioCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioCategory
        fields = '__all__'


class PortfolioImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = PortfolioImage
        fields = '__all__'

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None


class PortfolioItemSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    images_detail = PortfolioImageSerializer(source='images', many=True, read_only=True)
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = PortfolioItem
        fields = '__all__'

    def get_cover_image_url(self, obj):
        if obj.cover_image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.cover_image.url) if request else obj.cover_image.url
        return None
