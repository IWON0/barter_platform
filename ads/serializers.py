from rest_framework import serializers
from .models import Ad, ExchangeProposal

class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = ('id', 'user', 'title', 'description', 'image_url', 'category', 'condition', 'created_at')

class ExchangeProposalSerializer(serializers.ModelSerializer):
    ad_sender = serializers.PrimaryKeyRelatedField(queryset=Ad.objects.all())
    ad_receiver = serializers.PrimaryKeyRelatedField(queryset=Ad.objects.all())

    class Meta:
        model = ExchangeProposal
        fields = ('id', 'ad_sender', 'ad_receiver', 'comment', 'status', 'created_at')
        read_only_fields = ('status', 'created_at')
