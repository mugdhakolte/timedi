from django.contrib import admin
from django.core.exceptions import ValidationError
from notifications.utils import send_new_user_email
from timedi_auth.models import (TimediPermission, AccessToken, Role, UserTimediPermissionMap,
                                BlacklistedAccessToken, User, Account)


class UserAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        if obj.role.name in ["external_user", "standard_user","admin"] and obj.is_new_user:
            random_password = User.objects.make_random_password()
            if obj.role.name == "admin":
                send_new_user_email(obj, obj.username, random_password)
            else:
                try:
                    admin_user = obj.account.users.filter(role__name="admin").first()
                    if admin_user:
                        send_new_user_email(admin_user, obj.username, random_password)
                except:
                    super_admin = obj.account.users.filter(role__name="super_admin").first()
                    if super_admin:
                        send_new_user_email(super_admin, obj.username, random_password)
            obj.set_password(random_password)
            obj.save()
        # elif obj.role.name == "admin":
        #     matched_user = obj.account.users.filter(role__name=obj.role.name)
        #     if matched_user:
        #        raise ValidationError('Another admin present with this account. Can not proceed with this request')
        return super(UserAdmin, self).save_model(request, obj, form, change)


admin.site.register(User, UserAdmin)
admin.site.register(Account)
admin.site.register(TimediPermission)
admin.site.register(UserTimediPermissionMap)
admin.site.register(Role)
admin.site.register(AccessToken)
admin.site.register(BlacklistedAccessToken)
