from flask import Flask, render_template, request, json, redirect, jsonify
from flaskext.mysql import MySQL
from flask import session
import hashlib

app = Flask(__name__)

mysql = MySQL()
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Cookies1357'
app.config['MYSQL_DATABASE_DB'] = 'mydb'
app.config['MYSQL_DATABASE_HOST'] = 'saklia1.ccefyzhtcoeb.us-east-2.rds.amazonaws.com'
app.config['MYSQL_DATABASE_PORT'] = 3306
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

@app.route('/userHomepageLink')
def userHomepageLink():
    return render_template('userHome.html')

@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('error.html',error = 'Unauthorized Access')

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
                return redirect('/userHome')
            else:
                return render_template('errorLogin.html',error = 'Wrong password. Try again')
        else:
            return render_template('errorLogin.html',error = 'Could not find your account. Try again')


    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        con.close()

    
@app.route('/signUp',methods=['POST'])
def signUp():
 
    # read the posted values from the UI
    _firstname = request.form['inputName']
    _lastname = request.form['inputLastName']
    _email = request.form['inputEmail']
    _password = request.form['inputPassword']
    _confirmPassword = request.form['confirm_password']
    _customerType = "2"

    _passwordHashed = hashPass(_password)

    # validate the received values
    if _firstname and _lastname and _email and _password:

        conn = mysql.connect()
        cursor = conn.cursor()

        # print("FirstName: ", _firstname)
        # print("LastName: ", _lastname)
        # print("Email: ", _email)
        # print("Password: ", _password)
        # print("PasswordHashed: ", _passwordHashed)
        # print("ConfirmPassword: ", _confirmPassword)
        # print("CustomerType: ", _customerType)

        if(_password != _confirmPassword):
            return render_template("errorSignup.html",error="Passwords do not match")

        try:
            cursor.execute("INSERT INTO mydb.customer(first_name, last_name, email, password, customer_type_id) VALUES (%s, %s, %s, %s, %s)", (_firstname, _lastname, _email, str(_passwordHashed), _customerType))
            data = cursor.fetchall()

            if len(data) == 0:
                conn.commit()
                return redirect('/userHome')
        except:
            return render_template("errorSignup.html",error="Email already exists")
                
    else:
        return json.dumps({'html':'<span>Enter the required fields!</span>'})

@app.route('/addItem',methods=['POST'])
def addItem():
    if session.get('user'):
        _title = request.form['inputTitle']
        _description = request.form['inputDescription']
        _user = session.get('user')
        
        conn = mysql.connect()
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO tbl_todo(title, description, userid) VALUES (%s, %s, %s)", (_title, _description, _user))
        data = cursor.fetchall()
        
        if len(data) == 0:
            conn.commit()
            return redirect('/userHome')
            
        else:
            return render_template('error.html',error= 'An error occurred!')
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
            return redirect('/userHome')
            
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
            return redirect('/userHome')
            
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

@app.route('/delete/<id>',methods=['GET'])
def deleteItem(id):
    if session.get('user'):
        conn = mysql.connect()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM TodoList.tbl_todo WHERE id = %s", (id))
        data = cursor.fetchall()
        
        if len(data) == 0:
            conn.commit()
            return redirect('/userHome')
            
        else:
            return render_template('error.html',error= 'An error occurred!')
    else:
        return render_template('error.html',error = 'Unauthorized Access')

if __name__ == "__main__":
    app.run()   