from rest_framework import serializers
from django.core.files.base import ContentFile
import json

from diagrams.models import Category, DiagramLogs, DiagramFrame, DeployedDashboards, ITToolProduct
from django.contrib.auth import get_user_model


User = get_user_model()


class DiagramLogsSerializer(serializers.ModelSerializer):
    dt_created = serializers.DateTimeField(format="%d.%m.%Y %H:%M:%S")
    user = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = DiagramLogs
        fields = '__all__'
        
    







class ListDiagramFrameSerializer(serializers.ModelSerializer):
    updated_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M')
    class Meta:
        model = DiagramFrame
        fields = ["id", "title", "slug", "diagram_type", "updated_time", "updated_user_name"]
        
    
    def to_representation(self, instance):
        return super().to_representation(instance)





class ViewUpdateDiagramFrameSerializer(serializers.ModelSerializer):
    updated_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M', read_only=True)
    title = serializers.CharField(read_only=True)
    logs = DiagramLogsSerializer(many=True, read_only=True)
    source = serializers.JSONField()
    accessible_by = serializers.CharField(required=False, write_only=True)
    accessible_users = serializers.SerializerMethodField()
    passkey = serializers.CharField(write_only=True, required=False)
    has_password = serializers.SerializerMethodField()
    slug = serializers.SlugField(required=False, allow_blank=False)
    class Meta:
        model = DiagramFrame
        fields = [
            "id",
            "title",
            "slug",
            "diagram_type",
            "updated_time",
            "updated_user_name",
            "logs",
            "source",
            "is_protected",
            "passkey",
            "accessible_by",
            "accessible_users",
            "has_password"
        ]

    def validate(self, data: dict):
        user = self.context.get("user")
        slug = data.get("slug", None)
        diagram_type = data.get("diagram_type", None)
        source = data.get("source", None)
        passkey = data.get("passkey", None)
        protected = data.get("is_protected", False)
        
        if protected:
            if not passkey and not self.instance.passkey:
                raise serializers.ValidationError("passkey is required when protected is true")
        
        if not user:
            raise serializers.ValidationError("User is required")
        if not slug and not self.instance.slug:
            raise serializers.ValidationError("Slug is required")
        if not diagram_type:
            raise serializers.ValidationError("Diagram type is required")
        if not source:
            raise serializers.ValidationError("You trying to clear all content of this item. Use deletion instead.")
        
        if DiagramFrame.objects.filter(slug=slug).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError(f'The diagram with slug "{slug}" already exists')
        
        if self.instance.slug != slug:
            if DeployedDashboards.objects.filter(diagram_slug=self.instance.slug).exists():
                raise serializers.ValidationError('The diagram is deployed, The slug cannot be updated')
            
        if not isinstance(source, dict):
            raise serializers.ValidationError("Source must be a JSON object")
        
        
        data["updated_user_name"] = f'{user.username} ({user.first_name} {user.last_name})'

        return data
    
    def get_accessible_users(self, instance):
        emails = DiagramFrame.objects.filter(id=instance.id).first()
        if emails:
            if emails.accessible_by.exists():
                list_emails = list(emails.accessible_by.all().values_list("email", flat=True))
                return ','.join(list_emails)
        return []
    
    def update(self, instance, validated_data):
        source = validated_data.pop("source", None)
        accessible_by = validated_data.pop("accessible_by", [])
        passkey = validated_data.pop("passkey", None)
        log = DiagramLogs.objects.create(diagram=instance, changes={}, user=self.context.get("user"), path=instance.source)
        log.changes = self.re_construct_changes()
        log.save()
        instance = super().update(instance, validated_data)
        if passkey:
            instance.set_passkey(passkey)
            instance.save()
            request = self.context.get("request")
            request.session["current_passkey"] = passkey
            request.session.modified = True
        if accessible_by:
            instance.accessible_by.clear()
            for email in accessible_by:
                user = User.objects.filter(email=email).first()
                print("found user", user)
                if user:
                    instance.accessible_by.add(user)
        instance.source = ContentFile(json.dumps(source, indent=2), name=f"{instance.slug}.json")
        instance.save()
        return instance
    
    def get_has_password(self, instance):
        if instance.passkey:
            return True
        return False
    
    def validate_accessible_by(self, value):
        if not value:
            return value
        if not isinstance(value, str):
            raise serializers.ValidationError("accessible_by must be a string")
        emails = value.split(",")
        return emails
    
    def re_construct_changes(self):
        data = self.validated_data
        instance = self.instance
        changes = {}
        for k in data.keys():
            if k == "source":
                changes[k] = {
                    'old': None,
                    'new': None
                }
                continue
            if k == "passkey":
                continue
            if k == "accessible_by":
                old_list = list(instance.accessible_by.all().values_list("email", flat=True))
                new_list = list(data[k])
                changes[k] = {
                    'old': old_list,
                    'new': new_list
                }
                continue
            if k in data:
                if data[k] != getattr(instance, k):
                    changes[k] = {
                        'old': getattr(instance, k),
                        'new': data[k]
                    }
        return changes

    def to_representation(self, instance):
        rp = super().to_representation(instance)
        rp["source"] = json.loads(instance.source.read())

        return rp
    





class CreateUpdateDiagramFrameSerializer(serializers.ModelSerializer):
    updated_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M', read_only=True)
    passkey = serializers.CharField(write_only=True, required=False)
    source = serializers.JSONField()
    accessible_by = serializers.CharField(write_only=True, required=False, allow_blank=True)
    class Meta:
        model = DiagramFrame
        fields = [
            "id",
            "title",
            "slug",
            "diagram_type",
            "source",
            "updated_time",
            "updated_user_name",
            "is_protected",
            "passkey",
            "accessible_by",
        ]

    def validate(self, data):
        title = data.get("title", None)
        user = self.context.get("user")
        slug = data.get("slug", None)
        diagram_type = data.get("diagram_type", None)
        source = data.get("source", None)
        passkey = data.get("passkey", None)
        protected = data.get("is_protected", False)
        
        if protected and not passkey:
            raise serializers.ValidationError("passkey is required when protected is true")
        if not user:
            raise serializers.ValidationError("User is required")
        if not title:
            raise serializers.ValidationError("Title is required")
        if not slug:
            raise serializers.ValidationError("Slug is required")
        if not diagram_type:
            raise serializers.ValidationError("Diagram type is required")
        if not source:
            raise serializers.ValidationError("Source is required")
        
        if not isinstance(source, dict):
            raise serializers.ValidationError("Source must be a JSON object")
        
        if DiagramFrame.objects.filter(slug=slug).exists():
            raise serializers.ValidationError(f'The diagram with slug "{slug}" already exists')
        
        source = ContentFile(json.dumps(source, indent=2), name=f"{slug}.json")
        
        data["source"] = source
        data["user"] = user
        data["updated_user_name"] = f'{user.username} ({user.first_name} {user.last_name})'
        return data

    def validate_accessible_by(self, value):
        if not value:
            return value
        if not isinstance(value, str):
            raise serializers.ValidationError("accessible_by must be a string")
        emails = value.split(",")
        return emails
    
    def create(self, validated_data:dict):
        request = self.context.get("request")
        passkey = validated_data.pop("passkey", None)
        accessible_by = validated_data.pop("accessible_by", [])
        instance = DiagramFrame.objects.create(**validated_data)
        for email in accessible_by:
            user = User.objects.filter(email=email).first()
            if user:
                instance.accessible_by.add(user)
        instance.save()
        if passkey:
            instance.set_passkey(passkey)
            instance.save()
            request.session["current_passkey"] = passkey
            request.session.modified = True
            
        return instance



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ITToolProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = ITToolProduct
        fields = ['id', 'user', 'title', 'image', 'description', 'demo_link', 'category', 'create_link', 'file_example', 'created_at', 'updated_at']

class CreateUpdateITToolProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=True)
    
    class Meta:
        model = ITToolProduct
        fields = ['user', 'title', 'image', 'description', 'demo_link', 'category', 'create_link', 'file_example']

    # Custom validation method for title uniqueness
    def validate_title(self, value):
        # Check if an ITToolProduct with the same title exists
        if ITToolProduct.objects.filter(title=value).exists():
            raise serializers.ValidationError("This title has already been used.")
        return value
    
    # Custom validation logic
    def validate(self, data):
        if 'title' not in data or not data['title']:
            raise serializers.ValidationError({"title": "This field is required."})
        
        if 'image' not in data or not data['image']:
            raise serializers.ValidationError({"image": "This field is required."})

        if 'create_link' not in data or not data['create_link']:
            raise serializers.ValidationError({"create_link": "This field is required."})

        if 'file_example' not in data or not data['file_example']:
            raise serializers.ValidationError({"file_example": "This field is required."})
            
        return data

    def create(self, validated_data):
        user = self.context['request'].user  
        validated_data['user'] = user 
        return ITToolProduct.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.image = validated_data.get('image', instance.image)
        instance.description = validated_data.get('description', instance.description)
        instance.demo_link = validated_data.get('demo_link', instance.demo_link)
        instance.category = validated_data.get('category', instance.category)
        instance.create_link = validated_data.get('create_link', instance.create_link)
        instance.file_example = validated_data.get('file_example', instance.file_example)
        
        instance.save()
        return instance