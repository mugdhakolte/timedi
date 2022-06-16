"""Module for Authentication services viewset ."""

from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.views import Response
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import translation

from timedi_auth.utils import CustomJSONRenderer
from timedi_auth.serializers import *
from timedi_auth.utils import create_token
from notifications.utils import send_forgot_password_email


class LoginViewSet(ViewSet):
    """Check email and password and returns an timedi_auth token."""

    permission_classes = (AllowAny,)

    def create(self, request):
        """
        For logging user.

        :param request:
        :return:
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = request.data['username']
            try:
                User.objects.get(username=username)
            except ObjectDoesNotExist:
                return Response({'message': _('Username {} does not exist.').format(username)},
                                status=status.HTTP_400_BAD_REQUEST)

            password = request.data['password']
            user = authenticate(username=username, password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                AccessToken.objects.create(token=access_token, user=user)
                translation.activate(user.language)
                request.session[translation.LANGUAGE_SESSION_KEY] = user.language
                return Response({'message': _('User logged in successfully'),
                                 'data': {
                                     'refresh_token': str(refresh),
                                     'access_token': access_token,
                                     'name': user.name,
                                     'profile_pic': user.profile_pic or None,
                                     'username': user.username,
                                     'email': user.email,
                                     'id': user.id,
                                     'gender': user.gender,
                                     'company_name': user.company_name,
                                     'mobile_number': user.mobile_number,
                                     'assigned_hospital': user.assigned_hospital,
                                     'is_new_user': user.is_new_user,
                                     'role': user.role.name,
                                     'permissions': [{'module_code': permission.permission.code,
                                                      'module_name': permission.permission.display_name,
                                                      'read': permission.read,
                                                      'write': permission.write,
                                                      }
                                                     for permission in user.permission_maps.all()],
                                     'language': user.language
                                 }},
                                status=status.HTTP_200_OK
                                )
        return Response({'message': _('Please enter valid credentials.')},
                        status=status.HTTP_400_BAD_REQUEST)


class ImpersonateViewSet(ViewSet):
    """Check email and password and returns an auth token."""

    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, pk=None):
        if request.user.is_superuser:
            try:
                user = User.objects.get(pk=pk)
            except User.DoesNotExist:
                return Response({'message': _('Please enter valid credentials.')},
                                status=status.HTTP_400_BAD_REQUEST)
            if user:
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                AccessToken.objects.create(token=access_token, user=user)
                return Response({'message': _('Impersonated User Session'),
                                 'data': {
                                     'refresh_token': str(refresh),
                                     'access_token': access_token,
                                     'name': user.name,
                                     'profile_pic': user.profile_pic or None,
                                     'username': user.username,
                                     'email': user.email,
                                     'id': user.id,
                                     'gender': user.gender,
                                     'company_name': user.company_name,
                                     'mobile_number': user.mobile_number,
                                     'assigned_hospital': user.assigned_hospital,
                                     'is_new_user': user.is_new_user,
                                     'role': user.role.name,
                                     'permissions': [{'module_code': permission.permission.code,
                                                      'module_name': permission.permission.display_name,
                                                      'read': permission.read,
                                                      'write': permission.write,
                                                      }
                                                     for permission in user.permission_maps.all()],
                                     'language': user.language
                                 }},
                                status=status.HTTP_200_OK
                                )
        return Response({'message': _('Please enter valid credentials.')},
                        status=status.HTTP_400_BAD_REQUEST)


class LogoutView(ViewSet):
    serializer_class = LogoutSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request):
        token = request.META['HTTP_AUTHORIZATION'].split()[1]
        sz = self.serializer_class(data={'refresh': request.data['refresh'], 'access': token})
        sz.is_valid(raise_exception=True)
        sz.save()
        return Response(
            {'message': _('User Successfully Logout')},
            status=status.HTTP_200_OK)


class ForgotPasswordViewSet(ViewSet):
    """Class for forgot password."""

    permission_classes = (AllowAny,)

    def create(self, request):
        """
        Method will create and send forgot password link.

        :param request:
        :return: response
        """
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data['username']
        try:
            user = User.objects.get(username=username)
            token = create_token(user, 'forgot_password')
            if user.role.name in ['super_admin', 'admin']:
                send_forgot_password_email(user, user.username, token)
                return Response(
                    {'message': _('Password reset link successfully sent to your email:{}').format(user.email)},
                    status=status.HTTP_200_OK)

            else:
                try:
                    admin_user = user.account.users.filter(role__name="admin").first()
                    send_forgot_password_email(admin_user, username, token)
                    return Response({
                        'message': _('Password reset link successfully sent to your email:{}').format(
                            admin_user.email)},
                        status=status.HTTP_200_OK)
                except:
                    super_admin = user.account.users.filter(role__name="super_admin").first()
                    send_forgot_password_email(super_admin, username, token)
                    return Response({
                        'message': _('Password reset link successfully sent to your email:{}').format(
                            super_admin.email)},
                        status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"data": {'username': [_('Username {} does not exist.').format(username)]}},
                            status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordViewSet(ViewSet):
    """Class to reset password."""

    permission_classes = (AllowAny,)

    def create(self, request):
        """
        To reset password.

        :param request:
        :return: response
        """
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            new_password = request.data['new_password']
            token = request.data['token']
            token = Token.objects.get(token=token)
            user = token.user
            user.set_password(new_password)
            user.is_new_user = False
            user.save()
            token.delete()
            return Response({'message': _('Successfully updated the password.')},
                            status=status.HTTP_200_OK)
        return Response({'message': _('Invalid Reset Link. Please try again.')},
                        status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordViewSet(ViewSet):
    """Class to change password."""

    permission_classes = (IsAuthenticated,)
    renderer_classes = (CustomJSONRenderer,)

    def create(self, request):
        """
        To change password.

        :param request:
        :return:response
        """
        if request.user.is_new_user:
            serializer_class = ChangePasswordSerializer(data=request.data, context={'request': request})
            serializer_class.is_valid(raise_exception=True)
            new_password = request.data.get('new_password')
            request.user.set_password(new_password)
            request.user.is_new_user = False
            request.user.save()
            return Response({'message': _('Password has been changed')},
                            status=status.HTTP_200_OK)
        else:
            return Response({'message': _('This is not a new user')},
                            status=status.HTTP_400_BAD_REQUEST)


class ValidateTokenViewSet(ViewSet):
    """Class to ValidateToken"""

    permission_classes = (AllowAny,)

    def list(self, request):
        token = request.query_params.get('access', None)
        try:
            token = Token.objects.get(token=token)
            return Response({'message': _('Success')},
                            status=status.HTTP_200_OK)
        except:
            return Response({'message': _('Link is expired, Please try again!')},
                            status=status.HTTP_400_BAD_REQUEST)
