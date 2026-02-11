
from django.test import TestCase
import hashlib
import datetime
import re
# Create your tests here.
def check_phone_number(self,phone):
        mess = None
        if not(phone):mess = "Enter Phone Number"
        elif not(re.search(r'\+', phone[:1]) and phone.replace('+','00').isnumeric() or phone.isnumeric()):mess = "Phone Number Must Be Numbers Or Numbers With `+` In Start"
        elif not(phone.__len__()<=14):mess = "Phone Number Must Be 14 Or Less Then 14 Numbers"
        # elif not(phone.startswith(('77','78','73','71','70'))):mess = "Phone Number Must Start With One Of (77,78,73,71,70)"
        return mess