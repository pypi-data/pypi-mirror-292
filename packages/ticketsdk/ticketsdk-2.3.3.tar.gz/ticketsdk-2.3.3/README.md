# nh-ticket-sdk
Use:

```
pip install ticketsdk
from ticketsdk.seller import Connection

```

### Add new seller:
```
Connection(body = {
    "partner_code":"111",
    "email":"dan5@gmail.com",
    "cs_email": "tri.nm@nandhlogistics.vn",
    "lambda_type" :"map",
    "name":"name option",
    "company_name":"company_name option",
}).add_new_seller()
```
### Add ticket:
```
Connection(body = {
    "partner_code":"111",
    "ref_code":"test_23_03_2024",
    "ticket_name":"Lấy video đóng gói đơn hàng xxxx",
    "ticket_description" : "Lấy video đóng gói đơn hàng xxxx",
    "issue_code": "OUTBOUND",
    "from_system" : "WMS",
    "requested_email":"tri.nm@nandhlogistics.vn",
    "lambda_type" :"add",
    "attachments" :[],
    "requested_by_employee_email": "test@gmail",
    "requested_by_employee_name": "requested_by_employee_email"
}).add_new_ticket()

```

### List ticket:
```
Connection(body = {
    "lambda_type" :"list",
    "page":1
}
).list_ticket()

```

### Get detail ticket:
```
Connection(body = {
    "lambda_type" :"detail",
    "ticket_id":107
}).detail_ticket()

```

### GET comment ticket
```
Connection(body={ "lambda_type" :"get_comments", "ticket_id":107 }).list_comment_ticket()
```

### Add new comment ticket
```
Connection(body={ 
    "lambda_type" :"add_comments", 
    "ticket_id":283, 
    "content": "This is my text for customer source", 
    "attachments": [],
    "partner_code": "BS2X100004",
    "created_by_employee_email": "test@gmail",
    "created_by_employee_name": "OK"
}).create_comment_ticket()
```
### To upload a Python library to the Python Package Index (PyPI)

1. pip install twine
2. python setup.py sdist bdist_wheel
3. twine upload dist/*


