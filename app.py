from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
import mysql.connector
from mysql.connector import Error
from my_password import my_password

app = Flask(__name__)
ma = Marshmallow(app)

class MemberSchema(ma.Schema):
    name = fields.String(required=True)
    age = fields.String(required=True)
    
    class Meta:
        fields = ('name', 'age', 'id')
        
member_schema = MemberSchema()
members_schema = MemberSchema(many=True)

# Task 1: Setting Up the Flask Environment and Database Connection
def get_db_connection():
    db_name = "e_commerce_db"
    user = "root"
    password = my_password
    host = "localhost"
    
    try:
        conn = mysql.connector.connect(
            database = db_name,
            user = user,
            password = password,
            host = host
        )
        
        print("Connection to MySQL DB successful")
        return conn
    
    except Error as e:
        print(f"Error: {e}")
        return None
    
# --------------------------------------------------------------------------------
# Task 2: Implementing CRUD Operations for Members

@app.route('/members', methods=['GET'])
def get_members():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM members"
        
        cursor.execute(query)
        
        members = cursor.fetchall()
        
        return members_schema.jsonify(members)
    
    except Error as e:
        print("Error: {e}")
        return jsonify({"Error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# --------------------------------------------------------------------------------

@app.route('/members/<int:id>', methods=['GET'])
def get_member(id):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM members WHERE id = %s"
        
        cursor.execute(query, (id,))
        
        member = cursor.fetchone()
        
        if member:
            return member_schema.jsonify(member)
        else:
            return jsonify({"error": "Member not found"}), 404
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# --------------------------------------------------------------------------------

@app.route("/members", methods=["POST"])
def add_member():
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Internal Server Error"}), 500
        cursor = conn.cursor(dictionary=True)
        
        new_member = (member_data["name"], member_data["age"])
        query = "INSERT INTO members (name, age) VALUES (%s, %s)"
        
        cursor.execute(query, new_member)
        conn.commit()
        
        return jsonify({"message": "New member added successfully."}), 201
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# --------------------------------------------------------------------------------

@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Internal Server Error"}), 500
        cursor = conn.cursor(dictionary=True)
        
        updated_customer = (member_data['name'], member_data['age'], id)
        
        query = "UPDATE members SET name=%s, age = %s WHERE id=%s"
        
        cursor.execute(query, updated_customer)
        conn.commit()
        
        return jsonify({"message": "Updated customer successfully"}), 201
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            
# --------------------------------------------------------------------------------

@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Internal Server Error"}), 500
        cursor = conn.cursor(dictionary=True)
        
        member_to_remove = (id,)
        
        cursor.execute("select * from members where id = %s", member_to_remove)
        member = cursor.fetchone()
        if not member:
            return jsonify({"error": "Member not found"}), 404
        
        query = "delete from members where id = %s"
        cursor.execute(query, member_to_remove)
        conn.commit()
        
        return jsonify({"message": "Member removed successfully"}), 200
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    app.run(debug=True)