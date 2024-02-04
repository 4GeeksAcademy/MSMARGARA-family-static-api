"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from utils import APIException, generate_sitemap
from datastructures import FamilyStructure
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

# create the jackson family object
jackson_family = FamilyStructure("Jackson")

#Miembros iniciales
jackson_family.add_member({
    "first_name": "John",
    "age": 33,
    "lucky_numbers": [7, 13, 22]
})
jackson_family.add_member({
    "first_name": "Jane",
    "age": 35,
    "lucky_numbers": [10, 14, 3]
})
jackson_family.add_member({
    "first_name": "Jimmy",
    "age": 5,
    "lucky_numbers": [1]
})

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

## ENPOINTS ##

#Obtener todos los miembros de la familia
@app.route('/members', methods=['GET'])
def get_all_members():
    try:
        members = jackson_family.get_all_members()
        if not members:
            return jsonify({'error': 'No hay miembros en la familia'}), 400
        return jsonify(members), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Obtener un miembro por su ID
@app.route('/member/<int:id>', methods=['GET'])
def get_member(id):
    try:
        member = jackson_family.get_member(id)
        if member:
            return jsonify(member), 200
        else:
            return jsonify({"error": "Miembro no encontrado"}), 400
    except Exception as e:
        return jsonify({"error": "Error interno del servidor: {}".format(str(e))}), 500

#Agregar un nuevo miembro a la estructura de la familia
@app.route('/member', methods=['POST'])
def add_member():
    data = request.get_json()
    required_fields = ['id', 'first_name', 'age', 'lucky_numbers']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Formato incorrecto del cuerpo de la solicitud"}), 400
    try:
        member_id = jackson_family.add_member(data)
        return jsonify({"id": member_id}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Error interno del servidor: {}".format(str(e))}), 500
    
# Eliminar un miembro por su ID
@app.route('/member/<int:id>', methods=['DELETE'])
def delete_member_route(id):
    try:
        success = jackson_family.delete_member(id)
        if success:
            return jsonify({"done": True}), 200
        else:
            return jsonify({"error": "Miembro no encontrado"}), 400
    except Exception as e:
        return jsonify({"error": "Error interno del servidor: {}".format(str(e))}), 500

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
