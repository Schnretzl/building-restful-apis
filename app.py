from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
import mysql.connector
from mysql.connector import Error

class MemberSchema(ma.Schema):
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)
    
    class Meta:
        fields = ('name', 'age')
        
member_schema = MemberSchema()
members_schema = MemberSchema(many=True)

def get_db_connection():
    db_name = "e_commerce_db"
    user = "root"
    password = input("Enter your password: ")
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