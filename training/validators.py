import re
from django.core import validators
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
import csv
from validate_email import validate_email

class ASCIIValidator(validators.RegexValidator):
    regex = r'^[\w .@+-]+\Z'
    flags = re.ASCII


class LastNameValidator(validators.RegexValidator):
    regex = r'^[\w ./()\-]+\Z'
    flags = re.ASCII
    message = _("Last name must contain only letters, numbers, spaces, dots, hyphens, slashes, or parentheses.")



def validate_csv_file(csv_file):
    try:
        file_data = csv_file.read().splitlines()
    except Exception:
        raise ValidationError('Csv file could not be read.')
    row_count = len(file_data)
    if row_count > 0:
        line = 0
        error_lines = []
        for row in file_data:
            error = dict(line_no=None, fname=None, lname=None, email=None, gender=None,unicode_error=None, extra_errors=None)
            try:
                row_str = row.decode('utf-8') if isinstance(row, bytes) else str(row)
            except UnicodeDecodeError:
                error.update(dict(line_no="Row: "+str(line+1), unicode_error="Encoding error: only UTF-8 encoded CSV files are supported."))
                error_lines.append(error)
                line+=1
                continue
            try:
                ASCIIValidator(regex = r'^[\w .,@+/()\-]+\Z')(row_str)
            except:
                error.update(dict(line_no="Row: "+str(line+1), unicode_error="You have a invalid character in this row. Only English characters, digits and special characters like '@.-_' are allowed. Please check all the fields in this row."))
                error_lines.append(error)
                line+=1
                continue
            try:
                data = list(csv.reader([row_str], delimiter=',', quotechar='|'))
            except csv.Error:
                error.update(dict(line_no="Row: "+str(line+1), extra_errors="Invalid CSV formatting in this row."))
                error_lines.append(error)
                line+=1
                continue
            
            for col in data:
                if len(col) < 4:
                    error.update(dict(extra_errors="Row format is invalid: missing required columns."))
                    break
                try:
                    ASCIIValidator()(col[0].strip())
                except:
                    error.update(dict(fname="First name: "+ col[0] +" has errors."))
                try:
                    LastNameValidator()(col[1].strip())
                except:
                    error.update(dict(lname="Last Name: " + col[1] +" has errors."))
                try:
                    EmailValidator()(col[2].strip())
                    ASCIIUsernameValidator()(col[2].strip())
                    if not validate_email(col[2].strip()):
                        error.update(dict(email="Email: "+ col[2] +" has errors."))
                except:
                    error.update(dict(email="Email: "+ col[2] +" has errors."))
                try:
                    ASCIIValidator()(col[3].strip())
                except:
                    error.update(dict(gender="Gender: " +col[3] +" has errors."))
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
    try:
        return [f.decode('utf-8') if isinstance(f, bytes) else str(f) for f in file_data]
    except UnicodeDecodeError:
        raise ValidationError('Csv file contains invalid characters or encoding.')

