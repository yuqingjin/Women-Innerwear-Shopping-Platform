FETCH_USER = """
    SELECT users.user_id, users.password
    FROM users
    WHERE 1 = 1
"""

queryMap = {
    'user_id': " AND users.user_id IN ({})",
    'password': " AND users.password LIKE '%%{}%%'"
}


def fetch_user_info(args):
    query = FETCH_USER
    if 'user_id' in args and len(args['user_id']) > 0 and 'password' in args and len(args['password']) > 0:
        query += queryMap['user_id'].format(args['user_id'])
        query += queryMap['password'].format(args['password'])
    else:
        query += ' AND 1 = 2'

    return query
        
