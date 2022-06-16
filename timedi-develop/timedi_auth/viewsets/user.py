from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.views import Response
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from notifications.utils import send_new_user_email
from timedi_auth.serializers import *
from timedi_auth.permissions import CheckPermission
from timedi_auth.utils import CustomJSONRenderer


class UserListViewSet(mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated, CheckPermission]
    http_method_names = ['get']
    renderer_classes = (CustomJSONRenderer,)
    required_permission = ["manage_users", ]

    def get_queryset(self):
        if self.request.user.role.name == "super_admin":
            return User.objects.all().exclude(role__name="super_admin")
        elif self.request.user.role.name == "admin":
            return User.objects.filter(account__id=self.request.user.account_id).exclude(role__name="super_admin")
        return []


class UserViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [IsAuthenticated, CheckPermission]
    renderer_classes = (CustomJSONRenderer,)
    required_permission = ["manage_users", ]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserDetailSerializer
        if self.action == 'update':
            return UserUpdateSerializer
        return self.serializer_class

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if request.data["role_name"] == "admin":
            try:
                matched_user = User.objects.get(account=request.user.account_id, role__name=request.data["role_name"])
                if matched_user:
                    return Response(
                        {'message': _('Another admin present with this account. Can not proceed with this request.')}
                        , status=status.HTTP_400_BAD_REQUEST)
            except:
                pass
        user = serializer.save()
        permissions_list = request.data.get('permissions', None)
        if permissions_list:
            for perm in permissions_list:
                perm_id = TimediPermission.objects.get(code=perm['module_code'])
                permissions_data = {"user": user.id, "read": perm['read'], "write": perm['write'],
                                    "permission": perm_id.id}
                ser = UserPermissionSerializer(data=permissions_data)
                ser.is_valid(raise_exception=True)
                ser.save()
        random_password = User.objects.make_random_password()
        if request.data["role_name"] == "admin":
            send_new_user_email(user, user.username, random_password)
        elif request.data["role_name"] in ["external_user", "standard_user"]:
            try:
                admin_user = request.user.account.users.filter(role__name="admin").first()
                send_new_user_email(admin_user, user.username, random_password)
            except:
                super_admin = request.user.account.users.filter(role__name="super_admin").first()
                send_new_user_email(super_admin, user.username, random_password)
        user.set_password(random_password)
        user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.id == instance.id:
            data = {"message": _("You cannot delete own account.")}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            self.perform_destroy(instance)
            data = {"message": _("User deleted successfully.")}
            return Response(data, status=status.HTTP_204_NO_CONTENT)
