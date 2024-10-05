from django.core.exceptions import ValidationError
import re

class CustomPasswordValidator:
    def validate(self, password, user=None):
        if not re.findall(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                ("비밀번호에는 하나 이상의 특수문자가 포함되어야 합니다."),
                code='password_no_special',
            )

    def get_help_text(self):
        return ("비밀번호에는 하나 이상의 특수문자가 포함되어야 합니다.")