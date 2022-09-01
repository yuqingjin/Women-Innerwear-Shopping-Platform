FETCH_PRODUCT_NAME = """
    SELECT product.product_id,product.product_name,product.inventory,product.unit_price FROM product
    WHERE 1=1 
"""

FETCH_PRODUCT_CATEGORY = """
    WITH pd_bt AS(SELECT * FROM product NATURAL JOIN belong_to)
    SELECT pd_bt.product_id, pd_bt.product_name, pd_bt.inventory,pd_bt.unit_price,pd_bt.category_id
    FROM pd_bt
    WHERE pd_bt.category_id IN (SELECT category.category_id FROM category WHERE 1=1
"""

INSERT_PRODUCT_SHOPPINGCART ={
    "shopping_cart": "INSERT INTO shopping_cart VALUES ({sc_id}, '{user_id}', '{total}')",
    "shop_from": "INSERT INTO shop_from VALUES ('{sc_id}','{product_id}','{quantity}')"
}

FETCH_UNIT_PRICE =  """
    SELECT product.unit_price FROM product
    WHERE 1=1 
"""

FETCH_INVENTORY =  """
    SELECT product.inventory FROM product
    WHERE 1=1 
"""

FETCH_ADDED_SHOPPINGCART =  """
    SELECT * FROM shopping_cart
    WHERE 1=1 
"""

queryMap_product = {
    'product_name': " AND product.product_name LIKE '%%{}%%'"
}

queryMap_category = {
    'category_name': " AND category.category_name LIKE '%%{}%%')"
}

queryMap_unitprice = {
    'product_id': " AND product.product_id IN ({})"
}

queryMap_sc = {
    'user_id': " AND shopping_cart.user_id IN ({})"
}

MAX_ID_SHOPPINGCART = """SELECT MAX(sc_id) FROM shopping_cart"""

def fetch_product_name(args):
    query = FETCH_PRODUCT_NAME
    query += queryMap_product['product_name'].format(args['product_name']) if 'product_name' in args and len(args['product_name']) > 0 else ""
    return query

def fetch_product_category(args):
    query = FETCH_PRODUCT_CATEGORY
    query += queryMap_category['category_name'].format(args['category_name']) if 'category_name' in args and len(args['category_name']) > 0 else ""
    return query

def fetch_unit_price(args):
    query = FETCH_UNIT_PRICE
    query += queryMap_unitprice['product_id'].format(args['product_id']) if 'product_id' in args and len(args['product_id']) > 0 else ""
    return query

def fetch_inventory(args):
    query = FETCH_INVENTORY
    query += queryMap_unitprice['product_id'].format(args['product_id']) if 'product_id' in args and len(args['product_id']) > 0 else ""
    return query

def add_product_shoppingcart(sc_id, unit_price, args):
    add_sc = INSERT_PRODUCT_SHOPPINGCART["shopping_cart"]
    add_sc = add_sc.format(sc_id = int(sc_id) + 1, user_id = args['user_id'], total=unit_price*int(args['quantity']))
    return add_sc

def add_product_shopfrom(sc_id, args):
    add_sc = INSERT_PRODUCT_SHOPPINGCART["shop_from"]
    add_sc = add_sc.format(sc_id = int(sc_id) + 1, product_id = args['product_id'], quantity=args['quantity'])
    return add_sc

def fetch_sc(args):
    query = FETCH_ADDED_SHOPPINGCART
    query += queryMap_sc['user_id'].format(args['user_id']) if 'user_id' in args and len(args['user_id']) > 0 else ""
    return query