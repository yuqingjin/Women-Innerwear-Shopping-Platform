FETCH_ADDRESS = """
     WITH od_ad AS(
SELECT
	*
FROM
	order_detail od NATURAL JOIN 
	user_address ad
)
SELECT
    od_ad.od_id,
	od_ad.address_id,
	od_ad.user_id,
	od_ad.address_line1,
	od_ad.address_line2,
	od_ad.city,
	od_ad.state,
	od_ad.postcode,
	od_ad.phone_number
FROM 
	od_ad
WHERE
    {criteria1} = {value1}
    AND
    {criteria2} = {value2}
"""

FETCH_PAYMENT = """
     WITH od_pay AS(
SELECT
	*
FROM
	order_detail od NATURAL JOIN 
	user_payment pay
)
SELECT
    od_pay.od_id,
	od_pay.payment_id,
	od_pay.user_id,
	od_pay.card_number,
	od_pay.expiration_date
FROM 
	od_pay
WHERE
    {criteria1} = {value1}
    AND
    {criteria2} = {value2}
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
    {criteria1} = {value1}
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
	sc_info.total
FROM 
	sc_info
WHERE
    {criteria1} = {value1}
    AND
    {criteria2} = {value2}
"""

FETCH_PRODUCT = """
    WITH pd_cg AS(
SELECT
	*
FROM
	product pd NATURAL JOIN 
	category cg NATURAL JOIN 
	belong_to
)
    SELECT 
    pd_cg.category_id,
    pd_cg.category_name,
    pd_cg.product_id,
    pd_cg.product_name,
    pd_cg.inventory,
    pd_cg.unit_price
    FROM pd_cg
    WHERE 1 = 1 
"""

queryMap2 = {
    'product_id': " AND pd_cg.product_id IN ({})"}

INSERT_PRODUCT = """
    INSERT INTO product VALUES ({product_id},'{product_name}','{inventory}','{unit_price}')
"""

MAX_PRODUCT_ID = """
    SELECT MAX(product_id) FROM product
"""

INSERT_PRODUCT_TO_CATEGORY = """
    INSERT INTO belong_to VALUES ({product_id},'{category_id}')
"""


FETCH_CATEGORY = """
    SELECT * FROM category cg
    WHERE 1 = 1 
"""

queryMap = {
    'category_id': " AND cg.category_id IN ({})",
    'category_name': " AND cg.category_name LIKE '%%{}%%'"
}

INSERT_CATEGORY = """
    INSERT INTO category VALUES ({category_id},'{category_name}')
"""

MAX_CATEGORY_ID = """
    SELECT MAX(category_id) FROM category
"""

# Allow administrator to find address via only order_id or only user_id or both of them.
# Could not find address info not in order_detail table
def fetch_address(args):
    query = FETCH_ADDRESS
    if ('od_id' in args and len(args['od_id']) > 0) and ('user_id' in args and len(args['user_id']) > 0):
        query = query.format(criteria1 = "od_ad.od_id",
                             value1 = args["od_id"],
                             criteria2 = "od_ad.user_id",
                             value2 = args["user_id"])

    elif ('od_id' in args and len(args['od_id']) > 0) and ("user_id" not in args or len(args['user_id']) == 0):
        query = query.format(criteria1="od_ad.od_id",
                             value1=args["od_id"],
                             criteria2="1",
                             value2="1")

    elif ('user_id' in args and len(args['user_id']) > 0) and ("od_id" not in args or len(args['od_id']) == 0):
        query = query.format(criteria1="1",
                             value1="1",
                             criteria2="od_ad.user_id",
                             value2=args["user_id"])
    else:
        query = query.format(criteria1="1",
                             value1="2",
                             criteria2="1",
                             value2="2")
    return query

# Allow administrator to find payment via only order_id or only user_id or both of them.
# Could not find payment info did not appear in order_detail table
def fetch_payment(args):
    # query = FETCH_PAYMENT
    # query += queryMap2['od_id'].format(args['od_id']) if 'od_id' in args and len(args['od_id']) > 0 else ""
    # query += queryMap2['user_id'].format(args['user_id']) if 'user_id' in args and len(args['user_id']) > 0 else ""
    query = FETCH_PAYMENT
    if 'od_id' in args and len(args['od_id']) > 0 and 'user_id' in args and len(args['user_id']) > 0:
        query = query.format(criteria1 = "od_pay.od_id",
                             value1 = args["od_id"],
                             criteria2 = "od_pay.user_id",
                             value2 = args["user_id"])

    elif ('od_id' in args and len(args['od_id']) > 0) and ("user_id" not in args or len(args['user_id']) == 0):
        query = query.format(criteria1="od_pay.od_id",
                             value1=args["od_id"],
                             criteria2="1",
                             value2="1")

    elif ('user_id' in args and len(args['user_id']) > 0) and ("od_id" not in args or len(args['od_id']) == 0):
        query = query.format(criteria1="1",
                             value1="1",
                             criteria2="od_pay.user_id",
                             value2=args["user_id"])
    else:
        query = query.format(criteria1="1",
                             value1="2",
                             criteria2="1",
                             value2="2")
    return query

# Allow administrator to search order detail(what product users bought) via order_id
def fetch_order(args):
    query = FETCH_ORDER
    if 'od_id' in args and len(args['od_id']) > 0:
        query = query.format(criteria1 = "od_info.od_id",
                             value1 = args["od_id"])
    return query

# Allow administrator to find shoppingcart via only sc_id or only user_id or both of them.
def fetch_shopping_cart(args):
    query = FETCH_SHOPPING_CART
    if 'sc_id' in args and len(args['sc_id']) > 0 and 'user_id' in args and len(args['user_id']) > 0:
        query = query.format(criteria1 = "sc_info.sc_id",
                             value1 = args["sc_id"],
                             criteria2 = "sc_info.user_id",
                             value2 = args["user_id"])

    elif ('sc_id' in args and len(args['sc_id']) > 0) and ("user_id" not in args or len(args['user_id']) == 0):
        query = query.format(criteria1="sc_info.sc_id",
                             value1=args["sc_id"],
                             criteria2="1",
                             value2="1")

    elif ('user_id' in args and len(args['user_id']) > 0) and ("sc_id" not in args or len(args['sc_id']) == 0):
        query = query.format(criteria1="1",
                             value1="1",
                             criteria2="sc_info.user_id",
                             value2=args["user_id"])
    else:
        query = query.format(criteria1="1",
                             value1="2",
                             criteria2="1",
                             value2="2")
    return query

# Allow administrator to add products
# First we need to add into database,
# and then fetch it and post in the table to show the successful upload
def fetch_product(pd_id):
    query = FETCH_PRODUCT
    query += queryMap2['product_id'].format(str(int(pd_id) + 1))
    # query += queryMap2['product_name'].format(args['product_name']) if 'product_name' in args and len(args['product_name']) > 0 else ""
    # query += queryMap2['inventory'].format(args['inventory']) if 'inventory' in args and len(args['inventory']) > 0 else ""
    # query += queryMap2['unit_price'].format(args['unit_price']) if 'unit_price' in args and len(args['unit_price']) > 0 else ""
    return query

def add_product(pd_id, args):
    add_pd = INSERT_PRODUCT
    add_pd = add_pd.format(product_id = str(int(pd_id) + 1),
                           product_name = args['product_name'],
                           inventory = args['inventory'],
                           unit_price = args['unit_price'])
    return add_pd

# Allow administrator to add products into certain category
def add_product_to_category(pd_id, args):
    attach_pd = INSERT_PRODUCT_TO_CATEGORY
    attach_pd = attach_pd.format(product_id = str(int(pd_id) + 1),
                                 category_id = args['category_id'])
    return attach_pd


# Allow administrator to add category
# First we need to add into database,
# and then fetch it and post in the table to show the successful upload
def fetch_category(args):
    query = FETCH_CATEGORY
    query += queryMap['category_id'].format(args['category_id']) if 'category_id' in args and len(args['category_id']) > 0 else ""
    query += queryMap['category_name'].format(args['category_name']) if 'category_name' in args and len(args['category_name']) > 0 else ""
    return query

def add_category(cg_id, args):
    add_cg = INSERT_CATEGORY
    add_cg = add_cg.format(category_id = str(int(cg_id) + 1),
                           category_name = args['category_name'])
    return add_cg