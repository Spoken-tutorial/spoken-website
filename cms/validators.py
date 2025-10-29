import re
from django.core import validators
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
import csv

class ASCIIValidator(validators.RegexValidator):
    regex = r'^[\w .@+-]+\Z'
    flags = re.ASCII



def validate_csv_file(csv_file):
    file_data = csv_file.read().splitlines()
    row_count = len(file_data)
    if row_count > 0:
        line = 0
        error_lines = []
        for row in file_data:
            error = dict(line_no=None, fname=None, lname=None, email=None, gender=None,unicode_error=None, extra_errors=None)
            try:
                ASCIIValidator(regex = r'^[\w .,@+-]+\Z')(row)
            except:
                error.update(dict(line_no="Row: "+str(line+1), unicode_error="You have a invalid character in this row. Only English characters, digits and special characters like '@.-_' are allowed. Please check all the fields in this row."))
                error_lines.append(error)
                line+=1
                continue
            data = csv.reader([row.decode('utf-8')], delimiter=',', quotechar='|')
            for col in data:
                if len(col) ==4:
                    try:
                        ASCIIValidator()(col[0].strip())
                    except:
                        error.update(dict(fname="First name: "+ col[0] +" has errors."))
                    try:
                        ASCIIValidator()(col[1].strip())
                    except:
                        error.update(dict(lname="Last Name: " + col[1] +" has errors."))
                    try:
                        EmailValidator()(col[2].strip())
                        ASCIIUsernameValidator()(col[2].strip())
                    except:
                        error.update(dict(lname="Email: "+ col[2] +" has errors."))
                    try:
                        ASCIIValidator()(col[3].strip())
                    except:
                        error.update(dict(lname="Gender: " +col[3] +" has errors."))
                else:
                    error.update(dict(extra_errors="Only four fields must be available in this row."))
            for e in error.values():
                if e:
                    error.update(dict(line_no= "Row: "+str(line+1)))
                    error_lines.append(error)
                    break
            line+=1
        if len(error_lines) > 0:
            error_string = ""
            for el in error_lines:
                for i in el.values():
                    if i:
                        error_string += str(i+ "  ")
                error_string+="\n"
            raise ValidationError(error_string)
    else:
        raise ValidationError(('Csv file is empty.'))
    return [f.decode('utf-8') for f in file_data]