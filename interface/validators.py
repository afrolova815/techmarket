from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
import re


@deconstructible
class FilledAndPatternValidator:
    pattern = re.compile(r'^[A-Za-zА-Яа-яЁё0-9 -]+$')

    def __init__(self, message_empty=None, message_pattern=None):
        self.message_empty = message_empty or "Поле не должно быть пустым"
        self.message_pattern = message_pattern or "Недопустимые символы"

    def __call__(self, value):
        if value is None or not str(value).strip():
            raise ValidationError(self.message_empty)
        if not self.pattern.match(str(value)):
            raise ValidationError(self.message_pattern)
