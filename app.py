from flask import Flask, render_template, request, json, redirect, jsonify
from flaskext.mysql import MySQL
from flask import session
import hashlib

app = Flask(__name__)

edit_item = 0

mysql = MySQL()
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Cookies1357'
app.config['MYSQL_DATABASE_DB'] = 'mydb'
app.config['MYSQL_DATABASE_HOST'] = 'saklia1.ccefyzhtcoeb.us-east-2.rds.amazonaws.com'
app.config['MYSQL_DATABASE_PORT'] = 3306
_storeId = 1
mysql.init_app(app)

app.secret_key = 'secret key can be anything!'

def hashPass(password):
    return (hashlib.md5(password.encode())).hexdigest()

@app.route("/")
def main():
    return render_template('homepage.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/showUpdate/<id>')
def showUpdate(id):
    return render_template('update.html',id = id)

@app.route('/showSignIn')
def showSignin():
    return render_template('signin.html')

@app.route('/showHomePage')
def showHomePage():
    return render_template('homepage.html')


@app.route('/userCart')
def userCart():
    return render_template('userShoppingCart.html')

@app.route('/shoppingCart')
def shoppingCart():
    if session.get('user') :
        return render_template('userShoppingcart.html')
    else :
        return render_template('shoppingcart.html')

@app.route('/userhome')
def userhome():
    if session.get('user'):
        return render_template('userhome.html')
    else:
        return render_template('errorLogin.html',error = 'Unauthorized Access! Please Sign in.')

@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')

@app.route('/showAddItem')
def showAddItem():
    return render_template('addItem.html')


@app.route('/validateLogin', methods=['POST'])
def validateLogin():
    try:
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']
    
        con = mysql.connect()
        cursor = con.cursor()

        passwordHashed = hashPass(_password)
        
        cursor.execute("SELECT * FROM mydb.customer WHERE email = %s", (_email))

        data = cursor.fetchall()

        if len(data) > 0:
            if str(data[0][3]) == passwordHashed:
                session['user'] = data[0][0]
                _session_id = session.get('user')
                id = data[0][0]
                userType = data[0][12]
                cursor.execute("UPDATE mydb.customer SET session_id = %s WHERE customer_id = %s", (_session_id,id))
                con.commit()
                createCart(data[0][0])
                if(userType == 2):
                    return redirect('/userhome')
                else:
                    return redirect('/admin')
            else:
                return render_template('errorLogin.html',error = 'Wrong password! Try again.')
        else:
            return render_template('errorLogin.html',error = 'Could not find your account! Try again.')


    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        con.close()

    
@app.route('/signUp',methods=['GET','POST'])
def signUp():
    # read the posted values from the UI
    _firstname = request.form['inputName']
    _lastname = request.form['inputLastName']
    _email = request.form['inputEmail']
    _password = request.form['inputPassword']
    _customerType = "2"

    _passwordHashed = hashPass(_password)

    # validate the received values
    if _firstname and _lastname and _email and _password:

        conn = mysql.connect()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO mydb.customer(first_name, last_name, email, password, customer_type_id) VALUES (%s, %s, %s, %s, %s)", (_firstname, _lastname, _email, str(_passwordHashed), _customerType))
            data = cursor.fetchall()
          
            if len(data) == 0:
                conn.commit()
                return redirect('/showSignIn')
        except:
            return render_template("errorSignup.html",error="Email already exists!")
                
    else:
        return json.dumps({'html':'<span>Enter the required fields!</span>'})

@app.route('/addToCart/<productId>',methods=['POST','GET'])
def addItemToCart(productId):
    if session.get('user'):
        product_id = productId
        session_id = session.get('user')
        store_id = "1"
        
        conn = mysql.connect()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT customer_id FROM mydb.customer WHERE session_id=%s",(session_id))
            data = cursor.fetchall()
            customer_id = data[0][0]

            cursor.execute("SELECT cart_id FROM mydb.cart WHERE customer_id=%s",(customer_id))
            data = cursor.fetchall()
            cart_id = data[0][0]
            
            cursor.execute("INSERT into mydb.cart_detail (cart_id, store_id, product_id) VALUES (%s, %s, %s)", (cart_id,store_id,productId))

            data = cursor.fetchall()
            
            if len(data) == 0:
                conn.commit()
                return redirect('/showProductUser')
                
            else:
                return render_template('error.html',error= 'An error occurred!')
        except Exception as e:
            return render_template('error.html',error = str(e))
    else:
        return render_template('error.html',error = 'Unauthorized Access')


@app.route('/updateItem/<id>',methods=['POST'])
def updateItem(id):
    if session.get('user'):
        _title = request.form['updateTitle']
        _description = request.form['updateDescription']
        
        conn = mysql.connect()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE TodoList.tbl_todo SET title = %s, description = %s WHERE id = %s", (_title, _description, id))
        data = cursor.fetchall()
        
        if len(data) == 0:
            conn.commit()
            return redirect('/userhome')
            
        else:
            return render_template('error.html',error= 'An error occurred!')
    else:
        return render_template('error.html',error = 'Unauthorized Access')

@app.route('/updateCompletionStatus/<id>/<completed>',methods=['GET','POST'])
def updateCompletionStatus(id,completed):
    if session.get('user'):
        _completed = completed
        conn = mysql.connect()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE TodoList.tbl_todo SET completed = %s WHERE id = %s", (_completed,id))
        data = cursor.fetchall()
        
        if len(data) == 0:
            conn.commit()
            return redirect('/userhome')
            
        else:
            return render_template('error.html',error= 'An error occurred!')
    else:
        return render_template('error.html',error = 'Unauthorized Access')


@app.route('/itemsByUser',methods=['GET'])
def getItemsByUser():
    if session.get('user'):
        _user = session.get('user')
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM TodoList.tbl_todo WHERE userid = %s",(_user))
        data = cursor.fetchall()
        item = []
        content = {}
        conn.commit()
        for result in data:
            content = {'id': result[0], 'title': result[1], 'description': result[2], 'userid': result[3], 'completed': result[4]}
            item.append(content)
            content = {}
        return jsonify(item)
    else:
        return render_template('error.html',error = 'Unauthorized Access')

# @app.route('/delete/<id>',methods=['GET'])
# def deleteItem(id):
#     if session.get('user'):
#         conn = mysql.connect()
#         cursor = conn.cursor()
        
#         #update mydb.inventory set deleted = 1 where inventory_id = (param)id
#         cursor.execute("UPDATE mydb.invetory set deleted = 1 where inventory_id = %s", id)
#         data = cursor.fetchall()
        
#         if len(data) == 0:
#             conn.commit()
#             return redirect('/adminhome.html')
            
#         else:
#             return render_template('errorLogin.html',error= 'An error occurred!')
#     else:
#         return render_template('errorLogin.html',error = 'Unauthorized Access')

@app.route('/admin')
def colors():

    # Get the data from the database
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM mydb.inventory_vw")
    data = cursor.fetchall()
    #print("Data: ", data, "\n")
    return render_template('adminhome.html')
    
    #if len(data) == 0:
    #    conn.commit()
    #    return render_template('adminhome.html')
    #else:
    #    return render_template('errorLogin.html',error= 'An error occurred!')

# def getProductId(pName):
#     conn = mysql.connect()
#     cursor = conn.cursor()

#     #cursor.execute("SELECT * FROM mydb.customer WHERE email = %s", (_email))
#     cursor.execute("SELECT product_id FROM mydb.product WHERE product_name = %s", (pName))
#     productId = cursor.fetchall()
#     return productId

def getCustomerId(customer_id):
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT customer_id FROM mydb.customer WHERE customer_id = %s", (customer_id))
    customerId = cursor.fetchall()
    return customerId

def insertInventory(pName, quantity):
    conn = mysql.connect()
    cursor = conn.cursor()
    productId = getProductId(pName)
    cursor.execute("INSERT into mydb.inventory (store_id, product_id, inventory_quantity) VALUES (%s, %s, %s)", (_storeId, productId, quantity))
    data = cursor.fetchall()
    
    if len(data) == 0:
        conn.commit()
        return True

def createCart(customer_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("INSERT into mydb.cart (customer_id) VALUES (%s)", (customer_id))
    data = cursor.fetchall()
    
    if len(data) == 0:
        conn.commit()
        return True


@app.route('/addItem',methods=['POST'])
def addItem():
    #if session.get('user'):
    xproduct_name = request.form['ProductName']
    xdescription = request.form['inputDescription']
    xcost = request.form['inputCost']
    ximage = request.form['inputImg']
    xinventory_quantity = request.form['inputQuantity']
    xcategory_id = request.form['inlineRadioOptions']
    _user = session.get('user')
    
    conn = mysql.connect()
    cursor = conn.cursor()

    #What will be inserted into the db
    #ProductName, Cost, Image, Quanity, Store, Category, Description

    # insert:
    # insert into mydb.product (product_name, cost, category_id, full_image, description) values ('xproduct', 'xcost', xcategory_id, 'ximage', 'xdescription');
    # insert into mydb.inventory (store_id, product_id, inventory_quantity) values (xstore_id, xproduct_id, xinventory_quantity)
    #Category will be radio buttons
    
    cursor.execute("INSERT into mydb.product (product_name, cost, category_id, full_image, description) VALUES (%s, %s, %s, %s, %s)", (xproduct_name, xcost, xcategory_id, ximage, xdescription))

    

    #cursor.execute("INSERT into mydb.inventory (store_id, product_id, inventory_quantity) VALUES (%s, %s, %s)", (_storeId, 19, xinventory_quantity))
    
    data = cursor.fetchall()
    
    if len(data) == 0:
        conn.commit()
        insertInventory(xproduct_name, xinventory_quantity)
        return redirect('/admin')
            
        #else:
        #    return render_template('error.html',error= 'An error occurred!')
    #else:
       # return render_template('error.html',error = 'Unauthorized Access')

@app.route('/adminHomes')
def adminHomes():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mydb.inventory_vw")
    data = cursor.fetchall()
    return json.dumps(data)

@app.route("/showProduct")
def showProduct():
    return render_template('products.html')

@app.route("/showProductUser")
def showProductUser():
    return render_template('userProducts.html')

@app.route("/showAddForm")
def showAddForm():
    return render_template('template.html')


@app.route("/showEdit")
def showEdit():
    global edit_item
    edit_item = request.args.get('editTask', type = int)
    return render_template('template2.html')

@app.route('/getEditTask',methods=['GET'])
def getEditTask():
    try:
        _id = request.args.get('editTask', type = int)
        con = mysql.connect()
        cursor = con.cursor()
        cursor.execute("SELECT * FROM mydb.inventory_vw WHERE product_id = %s", edit_item)
        data = cursor.fetchall()
        return json.dumps(data)

    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        con.close()       

def updateInventory(quantity, productId, storeId):
    conn = mysql.connect()
    cursor = conn.cursor()
    #cursore.execute(update mydb.inventory set quantity = xquantity, store_id = xstore_id where inventory_id = xinventory_id)
    cursor.execute("UPDATE mydb.inventory SET inventory_quantity = %s, store_id = %s WHERE product_id = %s AND store_id = %s", (quantity,storeId,productId,storeId))
    data = cursor.fetchall()
    if len(data) == 0:
        conn.commit()
        return True
    return False

@app.route('/editItem/<productId>/<storeId>',methods=['POST'])
def editItem(productId, storeId):
    try:
        xproduct_name = request.form['ProductName']
        xdescription = request.form['inputDescription']
        xcost = request.form['inputCost']
        ximage = request.form['inputImg']
        xinventory_quantity = request.form['inputQuantity']
        xcategory_id = request.form['inlineRadioOptions']

        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute("UPDATE mydb.product SET product_name = %s, description = %s, full_image = %s, cost = %s, category_id = %s WHERE product_id = %s",(xproduct_name,xdescription,ximage,xcost,xcategory_id,productId))
        data = cursor.fetchall()
        if len(data) == 0:
            conn.commit()
            if updateInventory(xinventory_quantity, productId, storeId):
                return redirect('/admin')
            
            else:
                return render_template('error.html', error = 'Could not update selected product!')        
    except Exception as e:
        return render_template('error.html', error = str(e))   

@app.route("/deleteItem",methods=['POST'])
def deleteItem():
    try:
        _id = int(request.form['deleteItem'])
        con = mysql.connect()
        cursor = con.cursor()

        cursor.execute("UPDATE mydb.product set deleted = %s WHERE product_id = %s", (1, _id))
        con.commit()
        return redirect('/admin')

    except Exception as e:
        return render_template('errorLogin.html',error = str(e))
    finally:
        cursor.close()
        con.close()

    
@app.route("/deleteCartItem/<id>",methods=['POST'])
def deleteCartItem(id):
    try:
        #_id = int(request.form['deleteItem'])
        con = mysql.connect()
        cursor = con.cursor()
        _userId = session.get('user')

        cursor.execute("SELECT cart_id FROM mydb.cart WHERE customer_id=%s", (_userId))
        data = cursor.fetchall()

        cart_id = data[0][0]

        cursor.execute("UPDATE mydb.cart_detail set deleted = %s WHERE cart_id = %s AND product_id = %s", (1, cart_id, id))
        con.commit()
        return redirect('/admin')

    except Exception as e:
        return render_template('errorLogin.html',error = str(e))
    finally:
        cursor.close()
        con.close()

@app.route("/getCart")
def getCart():
    if session.get('user'):
        _userId = session.get('user')
        try:
            con = mysql.connect()
            cursor = con.cursor()

            cursor.execute("SELECT * FROM mydb.cart_detail_vw WHERE customer_id = %s", (_userId))
            data = cursor.fetchall()
            print("DATA ", data)
            return json.dumps(data)
        except Exception as e:
            return False
    else :
        return render_template('errorLogin.html',error = str(e))


@app.route("/spring")
def spring():
    return render_template('spring.html')

@app.route("/summer")
def summer():
    return render_template('summer.html')

@app.route("/fall")
def fall():
    return render_template('fall.html')

@app.route("/winter")
def winter():
    return render_template('winter.html')

@app.route("/userspring")
def Userspring():
    return render_template('userSpring.html')

@app.route("/usersummer")
def usersummer():
    return render_template('userSummer.html')

@app.route("/userfall")
def userfall():
    return render_template('userFall.html')

@app.route("/userwinter")
def userWinter():
    return render_template('userWinter.html')

if __name__ == "__main__":
    app.run()   