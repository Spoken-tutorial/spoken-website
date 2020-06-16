import re
from django.core import validators
from django.utils.translation import gettext_lazy as _

class ASCIIValidator(validators.RegexValidator):
    regex = r'^[\w .@+-]+\Z'
    flags = re.ASCII