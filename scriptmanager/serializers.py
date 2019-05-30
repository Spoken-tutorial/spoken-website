from creation.models import ContributorRole
from rest_framework import serializers

class ContributorRoleSerializer(serializers.ModelSerializer):
  class Meta:
    model = ContributorRole
    fields = ('foss_category', 'language', 'user', 'status')