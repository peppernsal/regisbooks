from regisbooks import Client

API_KEY = "abcdefg"

regis = Client(API_KEY)

MY_USER_ID = "abcd123"

carl = regis.get_user(MY_USER_ID)

print(carl.name)