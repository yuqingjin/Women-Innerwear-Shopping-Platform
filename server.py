import os, sys
from flask import Flask, request, render_template, g, redirect, Response
from sqlalchemy import *
from sqlalchemy.pool import NullPool

import json
import datetime
import logging

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template')
# print(tmpl_dir)
conf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conf')
# print(conf_dir)
app = Flask(__name__, template_folder=tmpl_dir)
print(app)
sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app'))

import application.user
import application.admin
import application.user_view
import application.login
import application.product

# Import login details from configuration file.
# with open(conf_dir + '/configuration.json') as f:
#   config = json.load(f)

DATABASEURI = "postgresql://" + "hz2759" + ":" + "0703" + "@35.211.155.104/proj1part2"

engine = create_engine(DATABASEURI)

@app.before_request
def before_request():
    try:
        logging.debug("In-flight request: Attempting to establish connection to DB")
        g.conn = engine.connect()
        logging.debug("In-flight request: Connection established!")
    except:
        logging.ERROR("In-flight request: Error connectiong to database!")
        import traceback; traceback.print_exc()
        g.conn = None

@app.teardown_request
def teardown_request(exception):
    try:
        g.conn.close()
    except Exception as e:
        pass

@app.route('/')
def index():
    return render_template("Home.html")

@app.route('/Home')
def index_home():
    return render_template("Home.html")

@app.route('/user')
def index_usr():
    return render_template("user.html")

@app.route('/product')
def index_product():
    return render_template("product.html")

@app.route('/login')
def index_order():
    return render_template("login.html")

@app.route('/user_view')
def index_user_view():
    return render_template("user_view.html")

@app.route('/admin')
def index_admin():
    return render_template("admin.html")

# User webpage functions
# Allow admin to find registered users
@app.route("/search_user", methods=["POST", "GET"])
def find_user():
    if "POST" == request.method:
        # rows = ["User ID", "Name", "Phone Number", "Email"]
        print(request.form)
        query = application.user.fetch_users(request.form)
        # print(query)
        cursor = g.conn.execute(query)
        result_search = []
        for c in cursor:
            result_search.append(c)
        # print(result)
        return render_template("user.html", **dict(usr_search = result_search))
    return redirect("/")

# Add new user with their new payment and address
@app.route("/add_user", methods=["POST", "GET"])
def add_user():
    if "POST" == request.method:
        query = application.user.MAX_USR_ID
        print("query1 = ", query)
        cursor = g.conn.execute(query)
        usr_id = 0
        for c in cursor:
            usr_id = c
        print(usr_id)
        query = application.user.add_users(usr_id[0], request.form)
        print("query2= ", query)
        cursor = g.conn.execute(query)
        query = application.user.fetch_users(request.form)
        print("query3= ", query)
        cursor = g.conn.execute(query)
        result_usr = []
        for c in cursor:
            result_usr.append(c)
        print('result_usr = ', result_usr)

        # Add new address
        query = application.user.MAX_ADDRESS_ID
        print("query1 = ", query)
        cursor = g.conn.execute(query)
        ad_id = 0
        for c in cursor:
            ad_id = c
            print(ad_id)
        print(ad_id)

        query = application.user.add_new_address(ad_id[0], usr_id[0], request.form)
        print("query2 = ", query)
        cursor = g.conn.execute(query)
        query = application.user.fetch_address(ad_id[0])
        print("query3 = ", query)
        cursor = g.conn.execute(query)
        result_ad = []
        for c in cursor:
            result_ad.append(c)
        print("result = ", result_ad)

        # Add new payment
        # verify the expiration date
        currentTime = datetime.datetime.now()
        current_month = int(currentTime.strftime("%m"))
        current_year = int(currentTime.strftime("%y"))
        input_month = int(request.form['expiration_date'][0:2])
        print('input_month(int)', input_month)
        input_year = int(request.form['expiration_date'][-2::])
        if current_year > input_year or (current_year == input_year and current_month >= input_month):
            import pymsgbox
            response = pymsgbox.alert("expiration date in the past", "Error")
            # print(response)
            return redirect("/user")
        query = application.user.MAX_PAYMENT_ID
        print("query1 = ", query)
        cursor = g.conn.execute(query)
        py_id = 0
        for c in cursor:
            py_id = c
        print(py_id)
        query = application.user.add_new_payment(py_id[0], usr_id[0], request.form)
        print("query2 = ", query)
        cursor = g.conn.execute(query)
        query = application.user.fetch_payment(py_id[0])
        print("query3 = ", query)
        cursor = g.conn.execute(query)
        result_py = []
        for c in cursor:
            result_py.append(c)
        print("result = ", result_py)
        return render_template("/user.html", **dict(usr_add=result_usr),
                                             **dict(ad_add=result_ad),
                                             **dict(py_add=result_py))
    return redirect("/")


# Search products according to their name
@app.route("/search_product_name", methods=["POST", "GET"])
def find_product_name():
    if "POST" == request.method:
        # rows = ["User ID", "Name", "Phone Number", "Email"]
        # print(request.form)
        query = application.product.fetch_product_name(request.form)
        # print(query)
        cursor = g.conn.execute(query)
        result_name = []
        for c in cursor:
            result_name.append(c)
        # print(result)
        return render_template("product.html", **dict(apt_name = result_name))
    return redirect("/")

# Search products according to their category name
@app.route("/search_product_category", methods=["POST", "GET"])
def find_product_category():
    if "POST" == request.method:
        # rows = ["User ID", "Name", "Phone Number", "Email"]
        # print(request.form)
        query = application.product.fetch_product_category(request.form)
        # print(query)
        cursor = g.conn.execute(query)
        result_category = []
        for c in cursor:
            result_category.append(c)
        # print(result_category)
        return render_template("product.html", **dict(apt_category = result_category))
    return redirect("/")

# Add products into shopping cart (One shopping cart could only contain one product but could with multiple quantity)
@app.route("/add_product_shoppingcart", methods=["POST", "GET"])
def add_product_to_shoppingcart():
    if "POST" == request.method:
        query=application.product.fetch_unit_price(request.form)
        cursor= g.conn.execute(query)
        for c in cursor:
            unit_price = c
        # print(unit_price)
        query = application.product.fetch_inventory(request.form)
        cursor = g.conn.execute(query)
        for c in cursor:
            inventory = c
        query = application.product.MAX_ID_SHOPPINGCART
        cursor = g.conn.execute(query)
        sc_id = 0
        for c in cursor:
            sc_id = c
        # print(usr_id)
        if int(request.form["quantity"])>inventory[0]:
            import pymsgbox
            response = pymsgbox.alert("Out of Stock!", "Error")
            print(response)
            return redirect("/product")
        else:
            query = application.product.add_product_shoppingcart(sc_id[0], unit_price[0], request.form)
            cursor=g.conn.execute(query)
            query = application.product.add_product_shopfrom(sc_id[0], request.form)
            cursor=g.conn.execute(query)
            query=application.product.fetch_sc(request.form)
            cursor=g.conn.execute(query)
            result_shoppingcart = []
            for c in cursor:
                result_shoppingcart.append(c)
            return render_template("/product.html", **dict(apt_sc = result_shoppingcart))
    return redirect("/")

# Admin Webpage Functions
# Search addresses based on user_id or od_id
@app.route("/search_address", methods=["POST", "GET"])
def find_address():
    if "POST" == request.method:
        # rows = ["User ID", "Name", "Phone Number", "Email"]
        query = application.admin.fetch_address(request.form)
        print(request.form)
        print(query)
        cursor = g.conn.execute(query)
        result = []
        for c in cursor:
            result.append(c)
        print(result)
        return render_template("admin.html", **dict(usr_add = result))
    return redirect("/")

# Search payments based on user_id or od_id
@app.route("/search_payment", methods=["POST", "GET"])
def find_payment():
    if "POST" == request.method:
        query = application.admin.fetch_payment(request.form)
        print(request.form)
        print(query)
        cursor = g.conn.execute(query)
        result = []
        for c in cursor:
            result.append(c)
        print(result)
        return render_template("admin.html", **dict(usr_pay=result))
    return redirect("/")

# Search order information(what product ordered) based on od_id
@app.route("/search_order", methods=["POST", "GET"])
def find_order_info():
    if "POST" == request.method:
        query = application.admin.fetch_order(request.form)
        print(request.form)
        print(query)
        cursor = g.conn.execute(query)
        result = []
        for c in cursor:
            result.append(c)
        print(result)
        return render_template("admin.html", **dict(order=result))
    return redirect("/")

# Search shopping cart based on user_id or sc_id
@app.route("/search_shoppingcart", methods=["POST", "GET"])
def find_shopping_cart():
    if "POST" == request.method:
        # rows = ["User ID", "Name", "Phone Number", "Email"]
        query = application.admin.fetch_shopping_cart(request.form)
        print(request.form)
        print(query)
        cursor = g.conn.execute(query)
        result = []
        for c in cursor:
            result.append(c)
        print(result)
        return render_template("admin.html", **dict(sc=result))
    return redirect("/")

# Add Products
@app.route("/add_product", methods=["POST", "GET"])
def product_add():
    if "POST" == request.method:
        print('request.form = ', request.form)
        query = application.admin.MAX_PRODUCT_ID
        print("query1 = ", query)
        cursor = g.conn.execute(query)
        pd_id = 0
        for c in cursor:
          pd_id = c
        print(pd_id)
        query = application.admin.add_product(pd_id[0], request.form)
        print("query2 = ", query)
        cursor = g.conn.execute(query)
        query = application.admin.add_product_to_category(pd_id[0], request.form)
        print("query3 = ", query)
        cursor = g.conn.execute(query)
        query = application.admin.fetch_product(pd_id[0])
        print("query4 = ", query)
        cursor = g.conn.execute(query)
        result = []
        for c in cursor:
            result.append(c)
        print("result = ", result)
        return render_template("/admin.html", **dict(pd=result))
    return redirect("/")


# Add Categories
@app.route("/add_category", methods=["POST", "GET"])
def category_add():
    if "POST" == request.method:
        rows = ["Category ID", "Category Name"]
        query = application.admin.MAX_CATEGORY_ID
        print("query1 = ", query)
        cursor = g.conn.execute(query)
        cg_id = 0
        for c in cursor:
          cg_id = c
        print(cg_id)
        query = application.admin.add_category(cg_id[0], request.form)
        print("query2 = ", query)
        cursor = g.conn.execute(query)
        query = application.admin.fetch_category(request.form)
        print("query3 = ", query)
        cursor = g.conn.execute(query)
        result = []
        for c in cursor:
            result.append(c)
        print("result = ", result)
        return render_template("/admin.html", **dict(cg=result))
    return redirect("/")


# User_view webpage functions
# Search addresses based on user_id
@app.route("/search_my_address", methods=["POST", "GET"])
def find_my_address():
    if "POST" == request.method:
        print(request.form)
        query = application.user_view.fetch_my_address(request.form)
        print(query)
        cursor = g.conn.execute(query)
        result = []
        for c in cursor:
            result.append(c)
        print(result)
        return render_template("user_view.html", **dict(find_ad = result))
    return redirect("/")

# Search payments based on user_id
@app.route("/search_my_payment", methods=["POST", "GET"])
def find_my_payment():
    if "POST" == request.method:
        print(request.form)
        query = application.user_view.fetch_my_payment(request.form)
        print(query)
        cursor = g.conn.execute(query)
        result = []
        for c in cursor:
            result.append(c)
        print(result)
        return render_template("user_view.html", **dict(find_py=result))
    return redirect("/")

# Add new address
@app.route("/add_address", methods=["POST", "GET"])
def address_add():
    if "POST" == request.method:
        print(request.form)
        query = application.user_view.MAX_ADDRESS_ID
        print("query1 = ", query)
        cursor = g.conn.execute(query)
        ad_id = 0
        for c in cursor:
          ad_id = c
        print(ad_id)
        query = application.user_view.add_new_address(ad_id[0], request.form)
        print("query2 = ", query)
        cursor = g.conn.execute(query)
        query = application.user_view.fetch_address(ad_id[0])
        print("query3 = ", query)
        cursor = g.conn.execute(query)
        result = []
        for c in cursor:
            result.append(c)
        print("result = ", result)
        return render_template("/user_view.html", **dict(add_ad=result))
    return redirect("/")

# Add new payment
@app.route("/add_payment", methods=["POST", "GET"])
def payment_add():
    if "POST" == request.method:
        print(request.form)
        # verify the expiration date
        currentTime = datetime.datetime.now()
        current_month = int(currentTime.strftime("%m"))
        current_year = int(currentTime.strftime("%y"))
        input_month = int(request.form['expiration_date'][0:2])
        print('input_month(int)', input_month)
        input_year = int(request.form['expiration_date'][-2::])
        if current_year > input_year or (current_year == input_year and current_month >= input_month):
            # def showMessage(message, type='info', timeout=2500):
            #     import tkinter as tk
            #     from tkinter import messagebox as msgb
            #     root = tk.Tk()
            #     root.withdraw()
            #     try:
            #         root.after(timeout, root.destroy)
            #         if type == 'info':
            #             msgb.showinfo('Info', message, master=root)
            #     except:
            #         pass
            # showMessage("expiration date in the past", type='info', timeout=2500)
            import pymsgbox
            response = pymsgbox.alert("expiration date in the past", "Error",timeout=2500)
            print(response)
            return redirect("/user_view")
        query = application.user_view.MAX_PAYMENT_ID
        print("query1 = ", query)
        cursor = g.conn.execute(query)
        py_id = 0
        for c in cursor:
          py_id = c
        print(py_id)
        query = application.user_view.add_new_payment(py_id[0], request.form)
        print("query2 = ", query)
        cursor = g.conn.execute(query)
        query = application.user_view.fetch_payment(py_id[0])
        print("query3 = ", query)
        cursor = g.conn.execute(query)
        result = []
        for c in cursor:
            result.append(c)
        print("result = ", result)
        return render_template("/user_view.html", **dict(add_py=result))
    return redirect("/")

# Search shopping cart based on user_id
@app.route("/search_my_shoppingcart", methods=["POST", "GET"])
def find_my_sc():
    if "POST" == request.method:
        print(request.form)
        query = application.user_view.fetch_my_shopping_cart(request.form)
        print(query)
        cursor = g.conn.execute(query)
        result = []
        for c in cursor:
            result.append(c)
        print(result)
        return render_template("user_view.html", **dict(find_sc=result))
    return redirect("/")

# Search order detail based on user_id
@app.route("/search_my_order", methods=["POST", "GET"])
def find_my_od():
    if "POST" == request.method:
        print(request.form)
        query = application.user_view.fetch_my_order(request.form)
        print(query)
        cursor = g.conn.execute(query)
        result = []
        for c in cursor:
            result.append(c)
        print(result)
        return render_template("user_view.html", **dict(find_od=result))
    return redirect("/")


# Update shopping cart, add new order and fetch new order detail
@app.route("/update_my_shoppingcart", methods=["POST", "GET"])
def shoppingCart_update():
    if "POST" == request.method:
        print(request.form)

        # get max order id
        query = application.user_view.MAX_ORDER_DETAIL_ID
        print("query1 = ", query)
        cursor = g.conn.execute(query)
        od_id = 0
        for c in cursor:
          od_id = c
        print(od_id)

        # update info to shopping cart
        query = application.user_view.update_shoppingCart(request.form)
        print("query2 = ", query)
        cursor = g.conn.execute(query)

        if request.form['update_action'] == 'order':
            # add new order
            query = application.user_view.add_new_order(od_id[0], request.form)
            print("query3 = ", query)
            cursor = g.conn.execute(query)

            # update 'total' to the new order
            query = application.user_view.update_order(request.form)
            print("query4 = ", query)
            cursor = g.conn.execute(query)

            # update product inventory in product table
            query = application.user_view.fetch_quantity(request.form)
            print("query5 = ", query)
            cursor = g.conn.execute(query)
            quantity = 0
            for c in cursor:
                quantity = c
            print(quantity)

            query = application.user_view.update_inventory(quantity[0],request.form)
            print("query5 = ", query)
            cursor = g.conn.execute(query)

            # post the new order info to frontend
            query = application.user_view.fetch_order(od_id[0])
            print("query6 = ", query)
            cursor = g.conn.execute(query)
            result = []
            for c in cursor:
                result.append(c)
            print("result = ", result)
            return render_template("/user_view.html", **dict(update_sc=result))
        elif request.form['update_action'] == 'delete':
            import pymsgbox
            response = pymsgbox.alert("You have successfully deleted your shopping cart.", "Alert")
            print(response)
            return redirect("/user_view")
    return redirect("/")

# Login webpage Functions
# verify the user_id and password, then grant user previlege to search their own records
@app.route("/user_verification", methods=["POST", "GET"])
def user_verification():
    if "POST" == request.method:
        print(request.form)
        query = application.login.fetch_user_info(request.form)
        print(query)
        cursor = g.conn.execute(query)
        result = []
        for c in cursor:
            result.append(c)
        print(result)
        if result:
            return redirect("/user_view")
    return redirect("/")


if __name__ == "__main__":
    # app.run(debug=True)
    import click
    logging.basicConfig(filename='server.log', format= '%(asctime)s %(message)s', level=logging.DEBUG)
    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using:
            python server.py
        Show the help text using:
            python server.py --help
        """

        HOST, PORT = host, port
        print("running on %s:%d" % (HOST, PORT))
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

    run()
