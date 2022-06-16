from rest_framework.routers import DefaultRouter
from timedi_auth.viewsets import (LoginViewSet, ResetPasswordViewSet, LogoutView, ImpersonateViewSet,
                                  ChangePasswordViewSet, ForgotPasswordViewSet,
                                  UserListViewSet, UserViewSet, ValidateTokenViewSet)

router = DefaultRouter()

router.register('users', UserListViewSet, basename='users')
router.register('user', UserViewSet, basename='user')

router.register('auth/login', LoginViewSet, base_name='login')
router.register('auth/logout', LogoutView, base_name='logout')
router.register('auth/impersonate', ImpersonateViewSet, base_name='impersonate_user')
router.register('auth/reset-password', ResetPasswordViewSet, base_name='reset_password')
router.register('auth/change-password', ChangePasswordViewSet, base_name='change_password')
router.register('auth/forgot-password', ForgotPasswordViewSet, base_name='forgot_password')
router.register('auth/validate-token', ValidateTokenViewSet, base_name='validate_token')

urlpatterns = router.urls
