from faker import Faker
from random import *
import json
import re
import string
fake = Faker('nl_NL')

def create_rows_faker(num=1):
    def twochar():
        return choice(string.ascii_uppercase) + choice(string.ascii_uppercase)
    output = []
    for x in range(num):
        name = fake.unique.name()
        email = re.sub('\W+','', name.lower() )[:9] + "@ing.com"
        corpkey= twochar() + str(randint(11,99)) + twochar()
        output.append({"name":name,"email":email,"corpkey":corpkey})
    return json.dumps(output)

with open("userdata.json", "w") as outfile:
    outfile.write(create_rows_faker(50))