import pymysql
from app import app
from config import mysql
from flask import jsonify, request, session
from flask_bcrypt import Bcrypt
from werkzeug.security  import check_password_hash
bcrypt = Bcrypt(app)

@app.route('/')
def home():
	if 'username' in session:
		return jsonify({'message' : 'You are already logged in','username' : session['username'], 'role' : session['role']})
	else:
		resp = jsonify({'message' : 'Unauthorized'})
		resp.status_code = 401
		return resp

@app.route('/login', methods=['POST'])
def login():
	conn = None;
	cursor = None;
	
	try:
		_json = request.json
		_username = _json['username']
		_password = _json['password']
		
		# validate the received values
		if _username and _password:
            # generate_password_hash( _password ,'pbkdf2:sha1', 15)
			#check user exists			
			conn = mysql.connect()
			cursor = conn.cursor()
			
			sql = "SELECT * FROM user WHERE username=%s"
			sql_where = (_username,)
			
			cursor.execute(sql, sql_where)
			row = cursor.fetchone()
        
			if row:
                
				if bcrypt.check_password_hash(row[2], _password):
					session['username'] = _username;session['role'] = row[3]
					#cursor.close()
					#conn.close()
					return jsonify({'username' : session['username'], 'role' : session['role']})
				else:
					resp = jsonify({'message' : 'Bad Request - invalid password'})
					resp.status_code = 400
					return resp
		else:
			resp = jsonify({'message' : 'Bad Request - invalid credendtials'})
			resp.status_code = 400
			return resp

	except Exception as e:
		print(e)

	finally:
		if cursor and conn:
			cursor.close()
			conn.close()
		
@app.route('/logout')
def logout():
	if 'username' in session:
		session.pop('username', None)
	return jsonify({'message' : 'You successfully logged out'})

@app.route('/create', methods=['POST'])
def create_emp():
    try:        
        _json = request.json
        _name = _json['name']
        _email = _json['email']
        _phone = _json['phone']
        _address = _json['address']	
        if _name and _email and _phone and _address and request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)		
            sqlQuery = "INSERT INTO emp(name, email, phone, address) VALUES(%s, %s, %s, %s)"
            bindData = (_name, _email, _phone, _address)            
            cursor.execute(sqlQuery, bindData)
            conn.commit()
            respone = jsonify('Employee added successfully!')
            respone.status_code = 200
            return respone
        else:
            return showMessage()
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        conn.close()          
     
@app.route('/emp')
def emp():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT id, name, email, phone, address FROM emp")
        empRows = cursor.fetchall()
        respone = jsonify(empRows)
        respone.status_code = 200
        return respone
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        conn.close()  

@app.route('/emp/<int:emp_id>')
def emp_details(emp_id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT id, name, email, phone, address FROM emp WHERE id =%s", emp_id)
        empRow = cursor.fetchone()
        respone = jsonify(empRow)
        respone.status_code = 200
        return respone
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        conn.close() 

@app.route('/update', methods=['PUT'])
def update_emp():
    try:
        _json = request.json
        _id = _json['id']
        _name = _json['name']
        _email = _json['email']
        _phone = _json['phone']
        _address = _json['address']
        if _name and _email and _phone and _address and _id and request.method == 'PUT':			
            sqlQuery = "UPDATE emp SET name=%s, email=%s, phone=%s, address=%s WHERE id=%s"
            bindData = (_name, _email, _phone, _address, _id,)
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sqlQuery, bindData)
            conn.commit()
            respone = jsonify('Employee updated successfully!')
            respone.status_code = 200
            return respone
        else:
            return showMessage()
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        conn.close() 

@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_emp(id):
	try:
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute("DELETE FROM emp WHERE id =%s", (id,))
		conn.commit()
		respone = jsonify('Employee deleted successfully!')
		respone.status_code = 200
		return respone
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()
        
       
@app.errorhandler(404)
def showMessage(error=None):
    message = {
        'status': 404,
        'message': 'Record not found: ' + request.url,
    }
    respone = jsonify(message)
    respone.status_code = 404
    return respone
        
if __name__ == "__main__":
    app.run()