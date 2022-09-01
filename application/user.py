import datetime
now = datetime.datetime.now()
now_str = now.strftime("%Y-%m-%d %H:%M:%S")

FETCH_USER = """
    SELECT users.user_id,users.name,users.phone_number,users.email FROM users
    WHERE 1=1 
"""

INSERT_USER = """
    INSERT INTO users VALUES ({user_id}, '{name}', '{password}', '{phone_number}', '{email}')
"""

FETCH_ADDRESS = """
    SELECT *
    FROM user_address ad
    WHERE
    {criteria} = {value}
"""

FETCH_PAYMENT = """
    SELECT py.payment_id, py.user_id, py.card_number, py.expiration_date
    FROM user_payment py
    WHERE
    {criteria} = {value}
"""

INSERT_ADDRESS = """
    INSERT INTO user_address VALUES ({address_id},'{user_id}',
    '{address_line1}','{address_line2}','{city}',
    '{state}','{postcode}','{phone_number}')
"""
INSERT_PAYMENT = """
    INSERT INTO user_payment VALUES ({payment_id},'{user_id}',
    '{card_number}','{expiration_date}')
"""

MAX_USR_ID = """
    SELECT MAX(user_id) FROM users
"""

MAX_ADDRESS_ID = """SELECT MAX(address_id) FROM user_address"""
MAX_PAYMENT_ID = """SELECT MAX(payment_id) FROM user_payment"""

queryMap = {
    'user_id': "AND users.user_id IN ({})",
    'name': " AND users.name LIKE '%%{}%%'",
    'phone_number': " AND users.phone_number LIKE '%%{}%%'",
    'email': " AND users.email LIKE '%%{}%%'"
}


def fetch_users(args):
    query = FETCH_USER
    query += queryMap['user_id'].format(args['user_id']) if 'user_id' in args and len(args['user_id']) > 0 else ""
    query += queryMap['name'].format(args['name']) if 'name' in args and len(args['name']) > 0 else ""
    query += queryMap['phone_number'].format(args['phone_number']) if 'phone_number' in args and len(args['phone_number']) > 0 else ""
    query += queryMap['email'].format(args['email']) if 'email' in args and len(args['email']) > 0 else ""
    return query

def add_users(usr_id, args):
    add_usr = INSERT_USER
    add_usr = add_usr.format(user_id = int(usr_id) + 1,
                             name = args['name'],
                             password = args['password'],
                             phone_number=args['phone_number'],
                             email=args['email'])
    return add_usr

def add_new_address(ad_id, usr_id, args):
    add_ad = INSERT_ADDRESS
    add_ad = add_ad.format(address_id = str(int(ad_id) + 1),
                           user_id = str(int(usr_id) + 1),
                           address_line1 = args['address_line1'],
                           address_line2 = args['address_line2'],
                           city=args['city'],
                           state=args['state'],
                           postcode=args['postcode'],
                           phone_number=args['phone_number'])
    return add_ad

def fetch_address(ad_id):
    post_ad = FETCH_ADDRESS
    post_ad = post_ad.format(criteria="ad.address_id",value=int(ad_id) + 1)
    return post_ad

# Allow user to add new payment records
def add_new_payment(py_id, usr_id, args):
    add_py = INSERT_PAYMENT
    add_py = add_py.format(payment_id = str(int(py_id) + 1),
                           user_id = str(int(usr_id) + 1),
                           card_number = args['card_number'],
                           expiration_date = args['expiration_date'])
    return add_py

def fetch_payment(py_id):
    post_py = FETCH_PAYMENT
    post_py = post_py.format(criteria="py.payment_id",value=int(py_id) + 1)
    return post_py