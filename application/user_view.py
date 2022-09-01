import datetime
now = datetime.datetime.now()
now_str = now.strftime("%Y-%m-%d %H:%M:%S")
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

FETCH_SHOPPING_CART = """
     WITH sc_info AS(
SELECT
	*
FROM
	shop_from sf NATURAL JOIN 
	product pd NATURAL JOIN 
	shopping_cart sc
)
SELECT
    sc_info.sc_id,
	sc_info.user_id,
	sc_info.product_id,
	sc_info.product_name,
	sc_info.quantity,
	sc_info.total,
	sc_info.ordered
FROM 
	sc_info
    WHERE
    {criteria} = {value}
"""

FETCH_ORDER = """
     WITH od_info AS(
SELECT
	*
FROM
	order_detail od NATURAL JOIN 
	shop_from sf NATURAL JOIN
	product pd
)
SELECT
    od_info.od_id,
	od_info.user_id,
	od_info.sc_id,
	od_info.address_id,
	od_info.payment_id,
	od_info.created_time,
	od_info.product_id,
	od_info.product_name,
	od_info.quantity,
	od_info.total
FROM 
	od_info
WHERE
    {criteria} = {value}
"""

UPDATE_SHOPPING_CART = """
UPDATE shopping_cart
SET ordered = '1'
WHERE sc_id = {sc_id}
"""

UPDATE_PRODUCT = """
"""

DELETE_SHOPPING_CART = """
DELETE FROM shop_from
WHERE sc_id = {sc_id};
DELETE FROM shopping_cart
WHERE sc_id = {sc_id}
"""

DELETE_SHOP_FROM = """
DELETE FROM shop_from
WHERE shop_from.sc_id = {sc_id}
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

INSERT_ORDER_DETAIL = """
    INSERT INTO order_detail VALUES ({od_id},'{sc_id}',
    '{user_id}','{address_id}','{payment_id}',
    '{created_time}','{total}')
"""

UPDATE_ORDER = """
UPDATE order_detail
SET total = (
SELECT shopping_cart.total
FROM shopping_cart
WHERE shopping_cart.sc_id = {sc_id1})
WHERE order_detail.sc_id = {sc_id2}
"""

UPDATE_INVENTORY = """
UPDATE product 
SET inventory = inventory - {quantity}
WHERE product.product_id = 
(SELECT shop_from.product_id 
 FROM shop_from
 WHERE shop_from.sc_id = {sc_id})
"""

MAX_ADDRESS_ID = """SELECT MAX(address_id) FROM user_address"""
MAX_PAYMENT_ID = """SELECT MAX(payment_id) FROM user_payment"""
MAX_ORDER_DETAIL_ID = """SELECT MAX(od_id) FROM order_detail"""

# To decline the past expiration date of payment method
# TRGIGGERS = {
#     "meds": """
#             UPDATE medicine M
#             SET current_stock = current_stock - 1
#             WHERE M.fda_id = {fda_id}
#     """
# }

# Allow user to add new address records
def add_new_address(ad_id, args):
    add_ad = INSERT_ADDRESS
    add_ad = add_ad.format(address_id = str(int(ad_id) + 1),
                           user_id = args['user_id'],
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
def add_new_payment(py_id, args):
    add_py = INSERT_PAYMENT
    add_py = add_py.format(payment_id = str(int(py_id) + 1),
                           user_id = args['user_id'],
                           card_number = args['card_number'],
                           expiration_date = args['expiration_date'])
    return add_py

def fetch_payment(py_id):
    post_py = FETCH_PAYMENT
    post_py = post_py.format(criteria="py.payment_id",value=int(py_id) + 1)
    return post_py

# Allow user to find their own address records via their user_id
def fetch_my_address(args):
    query = FETCH_ADDRESS
    if ('user_id' in args and len(args['user_id']) > 0):
        query = query.format(criteria="ad.user_id",
                             value=args["user_id"])
    else:
        query = query.format(criteria="1",
                             value="2")
    return query

# Allow user to find their own payment records via their user_id
def fetch_my_payment(args):
    query = FETCH_PAYMENT
    if ('user_id' in args and len(args['user_id']) > 0):
        query = query.format(criteria="py.user_id",
                             value=args["user_id"])
    else:
        query = query.format(criteria="1",
                             value="2")
    return query


# Allow user to find their own shopping cart records via their user_id
def fetch_my_shopping_cart(args):
    query = FETCH_SHOPPING_CART
    if ('user_id' in args and len(args['user_id']) > 0):
        query = query.format(criteria="sc_info.user_id",
                             value=args["user_id"])
    else:
        query = query.format(criteria="1",
                             value="2")
    return query


# Allow user to find their own order records via their user_id
def fetch_my_order(args):
    query = FETCH_ORDER
    if ('user_id' in args and len(args['user_id']) > 0):
        query = query.format(criteria="od_info.user_id",
                             value=args["user_id"])
    else:
        query = query.format(criteria="1",
                             value="2")
    return query

# Allow user to update their shopping cart: make it an order or delete it
def update_shoppingCart(args):
    if ('update_action' in args and len(args['update_action']) > 0):
        if args['update_action'] == 'order':
            update_sc = UPDATE_SHOPPING_CART
            update_sc = update_sc.format(sc_id = args['sc_id'])
        elif args["update_action"] == 'delete':
            update_sc = DELETE_SHOPPING_CART
            update_sc = update_sc.format(sc_id = args['sc_id'])
        return update_sc


def add_new_order(od_id, args):
    add_od = INSERT_ORDER_DETAIL
    add_od = add_od.format(od_id = str(int(od_id) + 1),
                           sc_id = args['sc_id'],
                           user_id = args['user_id'],
                           address_id = args['address_id'],
                           payment_id=args['payment_id'],
                           created_time=now_str,
                           total = 0)
    return add_od



def update_order(args):
    update_od = UPDATE_ORDER
    if ('sc_id' in args and len(args['sc_id']) > 0):
        update_od = update_od.format(sc_id1 = args['sc_id'],sc_id2 = args['sc_id'])
        return update_od

def fetch_order(od_id):
    query = FETCH_ORDER
    query = query.format(criteria="od_info.od_id",value=int(od_id) + 1)
    return query


def update_inventory(quantity, args):
    update_od = UPDATE_INVENTORY
    if ('sc_id' in args and len(args['sc_id']) > 0):
        update_od = update_od.format(quantity = quantity,sc_id = args['sc_id'])
        return update_od

FETCH_QUANTITY = """
SELECT shop_from.quantity
FROM shop_from
WHERE shop_from.sc_id = {sc_id}
"""

def fetch_quantity(args):
    query = FETCH_QUANTITY
    query = query.format(sc_id=args['sc_id'])
    return query
