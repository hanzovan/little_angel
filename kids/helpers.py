from datetime import datetime, timedelta, date
from .models import User, Kid, Course, Aspect, Evaluation, Expectation

def strong_password(s):
    special_list = [
        "~", "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "_", "+", "[", "]", "{", "}", "?"
    ]
    number = 0
    special = 0
    alphabet = 0
    for i in s:
        if i in special_list:
            special += 1
        if i.isnumeric():
            number += 1
        if i.isalpha():
            alphabet += 1

    if number > 0 and special > 0 and alphabet > 0 and len(s) > 6:
        return True
    else:
        return False

def days_between(d1, d2):
    d1 = datetime.strptime(d1, '%Y-%m-%d')
    d2 = datetime.strptime(d2, '%Y-%m-%d')

    # Return normal value
    return (d2 - d1).days

    # Return absolute value
    # return abs((d2 - d1).days)

