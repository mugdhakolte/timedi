ACTION_CHOICES = (
    ('reset_password', 'Reset Password'),
    ('register', 'Register'),
)

DEFAULT_GROUPS_CHOICES = (
    ('super_admin', 'Super_Admin'),
    ('admin', 'Admin'),
    ('external_user', 'External_User'),
    ('standard_user', 'Standard_User')
)

USER_PERMISSION =(
    ('read', 'Read'),
    ('write', 'Write')
)

LANGUAGE_CHOICES = (
    ('English', 'en'),
    ('Spanish', 'es'),
    ('Portuguese', 'pt'),
    ('French', 'fr'),
)

GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
)