from django.core.validators import RegexValidator

phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                             message="Phone number must be entered in the format: '+999999999'."
                                     " Up to 15 digits allowed.")

national_code_regex = RegexValidator(regex=r'^\d{10}$', message="National code has exactly 10 digits.")
