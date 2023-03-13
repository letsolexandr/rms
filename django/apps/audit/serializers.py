from rest_framework import serializers
from apps.core.api.base.serializers import SimpleUserSerializer
from apps.core.models import CoreUser
from .models import CRUDEvent, CRUDEventTypes


class HistoryUserSerializer(serializers.ModelSerializer):
    organization_name = serializers.StringRelatedField(
        source="organization",
        read_only=True
    )
    department_name = serializers.StringRelatedField(
        source="department",
        read_only=True
    )

    class Meta:
        model = CoreUser
        fields = ('first_name', 'last_name', 
                  'organization_name', 'department_name', 'state')


class HistorySerializer(serializers.ModelSerializer):
    user_detail = SimpleUserSerializer(source='user')
    day = serializers.CharField()
    event_type_name = serializers.SerializerMethodField()
    content_type_name = serializers.SerializerMethodField()


    class Meta:
        model = CRUDEvent
        fields = ['change_comment','user_as_string', 'user_detail', 'user_data', 'day','content_type_name','object_repr',
                  'datetime', 'event_type_name', 'changed_fields','hr_object_repr']

    def get_event_type_name(self, obj):
        return obj.get_event_type_display()
    
    def get_content_type_name(self, obj):
        return obj.content_type.name
