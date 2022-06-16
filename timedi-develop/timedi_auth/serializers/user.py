from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from timedi_auth.models import *


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class UserPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTimediPermissionMap
        fields = '__all__'


class UserPermissionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTimediPermissionMap
        fields = "__all__"
        depth = 1


class UserListSerializer(serializers.ModelSerializer):
    role_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = User
        exclude = ("password", "last_login", "created_at", "updated_at", "profile_pic", "company_name",
                   "mobile_number", "assigned_hospital", "user_permissions", "timedi_permissions", "is_new_user",
                   "language", "username", "is_superuser", "is_staff", "role", "account", "groups")
        depth = 2

    def get_role_name(self, obj):
        serializer = UserRoleSerializer(instance=obj.role)
        return serializer.data['name']

    def get_email(self, obj):
        if obj.email:
            return obj.email
        else:
            try:
                admin = User.objects.filter(account__id=obj.account_id, role__name="admin").first()
                return admin.email
            except:
                super_admin = User.objects.filter(role__name="super_admin").first()
                return super_admin.email


class UserDetailSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()
    role_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        exclude = (
            "password", "last_login", "created_at", "updated_at", "user_permissions", "timedi_permissions",
            "is_new_user", "is_superuser", "is_staff", "role", "account", "groups")

    def get_role_name(self, obj):
        serializer = UserRoleSerializer(instance=obj.role)
        return serializer.data['name']

    def get_permissions(self, obj):
        user_permissions = [{'module_code': permission.permission.code,
                             'module_name': permission.permission.display_name,
                             'read': permission.read,
                             'write': permission.write,
                             } for permission in obj.permission_maps.all()]
        return user_permissions


class UserCreateSerializer(serializers.ModelSerializer):
    """
    This serializer creates user with role and account.
    """
    role_name = serializers.CharField(write_only=True)

    class Meta:
        model = User
        exclude = ("password", "last_login", "created_at", "updated_at", "user_permissions", "timedi_permissions",
                   "is_new_user", "is_superuser", "is_staff", "role", "account", "groups")

    def create(self, validated_data):
        role_id = Role.objects.get(name=validated_data.pop('role_name'))
        validated_data['role'] = role_id
        if role_id.name == "admin":
            if 'email' not in validated_data or validated_data['email'] is None:
                raise serializers.ValidationError({'email': _('email field is required')})
            else:
                matched_email_user = None
                try:
                    matched_email_user = User.objects.get(email=validated_data['email'])
                except:
                    pass
                if matched_email_user is not None:
                    raise serializers.ValidationError({'email': _('email already exist')})
        validated_data['account_id'] = self.context['request'].user.account_id
        return super(UserCreateSerializer, self).create(validated_data)


class UserUpdateSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(write_only=True)
    """
    This serializer creates user with list of permissions, role and account.
    """
    permissions = serializers.ListField(allow_empty=True, write_only=True)
    is_permission_changed = serializers.BooleanField(default=False)

    class Meta:
        model = User
        exclude = ("last_login", "created_at", "updated_at", "user_permissions", "timedi_permissions",
                   "is_new_user", "is_superuser", "is_staff", "role", "account", "groups")
        extra_kwargs = {
            "password": {"write_only": True,
                         "required": False},
        }

    def update(self, instance, validated_data):
        permissions_list = validated_data.pop('permissions', None)
        role_id = Role.objects.get(name=validated_data.pop('role_name'))
        validated_data['role'] = role_id
        try:
            if permissions_list and validated_data["is_permission_changed"]:
                for userperm in instance.timedi_permissions.constrained_target:
                    userperm.delete()
                for perm in permissions_list:
                    perm_id = TimediPermission.objects.get(code=perm['module_code'])
                    permissions_data = {"user": instance.id, "read": perm['read'], "write": perm['write'],
                                        "permission": perm_id.id}
                    ser = UserPermissionSerializer(data=permissions_data)
                    ser.is_valid(raise_exception=True)
                    ser.save()
            instance = super(UserUpdateSerializer, self).update(instance, validated_data)
            if validated_data.get('password', None):
                instance.set_password(validated_data.get('password'))
            instance.save()

        except Exception as e:
            raise serializers.ValidationError(e)

        return instance
