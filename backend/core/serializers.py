from rest_framework import serializers
from .models import SiteSettings, Skill, Experience, Education


class SiteSettingsSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    favicon_url = serializers.SerializerMethodField()
    author_photo_url = serializers.SerializerMethodField()
    about_cover_url = serializers.SerializerMethodField()

    class Meta:
        model = SiteSettings
        exclude = ['email_host_password', 'email_host_user', 'email_host', 'email_port', 'email_use_tls']

    def get_logo_url(self, obj):
        if obj.logo:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.logo.url) if request else obj.logo.url
        return None

    def get_favicon_url(self, obj):
        if obj.favicon:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.favicon.url) if request else obj.favicon.url
        return None

    def get_author_photo_url(self, obj):
        if obj.author_photo:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.author_photo.url) if request else obj.author_photo.url
        return None

    def get_about_cover_url(self, obj):
        if obj.about_cover:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.about_cover.url) if request else obj.about_cover.url
        return None


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = '__all__'


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = '__all__'
