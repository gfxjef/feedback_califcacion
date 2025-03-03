# roles_menu.py
from flask import Blueprint, jsonify, request
from . import get_db_connection, TABLE_NAME  # Asegúrate de que estas importaciones sean correctas para tu estructura

roles_menu_bp = Blueprint('roles_menu_bp', __name__)

# Endpoint para consultar todos los registros
@roles_menu_bp.route('/roles_menu', methods=['GET'])
def get_roles_menu():
    cnx = get_db_connection()
    if cnx is None:
        return jsonify({'status': 'error', 'message': 'No se pudo conectar a la base de datos.'}), 500

    try:
        cursor = cnx.cursor(dictionary=True)
        query = f"SELECT * FROM `{TABLE_NAME}`;"
        cursor.execute(query)
        records = cursor.fetchall()
        return jsonify({'status': 'success', 'records': records}), 200
    except Exception as err:
        return jsonify({'status': 'error', 'message': str(err)}), 500
    finally:
        cursor.close()
        cnx.close()

# Endpoint para agregar un nuevo registro
@roles_menu_bp.route('/roles_menu', methods=['POST'])
def add_roles_menu():
    data = request.get_json()
    cnx = get_db_connection()
    if cnx is None:
        return jsonify({'status': 'error', 'message': 'No se pudo conectar a la base de datos.'}), 500

    try:
        cursor = cnx.cursor()
        query = f"""
            INSERT INTO `{TABLE_NAME}` 
            (
                menu1_Inventario,
                submenu1_agregar_inventario,
                menu2_Feedback,
                submenu2_generador_encuestas,
                submenu3_respuestas_comentarios,
                menu3_Solicitud_Merchandising,
                submenu4_nueva_solicitud,
                submenu5_confirmados,
                submenu6_entregados,
                menu4_Administracion,
                submenu7_roles
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            data.get('menu1_Inventario'),
            data.get('submenu1_agregar_inventario'),
            data.get('menu2_Feedback'),
            data.get('submenu2_generador_encuestas'),
            data.get('submenu3_respuestas_comentarios'),
            data.get('menu3_Solicitud_Merchandising'),
            data.get('submenu4_nueva_solicitud'),
            data.get('submenu5_confirmados'),
            data.get('submenu6_entregados'),
            data.get('menu4_Administracion'),
            data.get('submenu7_roles'),
        )
        cursor.execute(query, values)
        cnx.commit()
        new_id = cursor.lastrowid
        return jsonify({'status': 'success', 'message': 'Registro agregado', 'id': new_id}), 201
    except Exception as err:
        cnx.rollback()
        return jsonify({'status': 'error', 'message': str(err)}), 500
    finally:
        cursor.close()
        cnx.close()

# Endpoint para editar un registro existente
@roles_menu_bp.route('/roles_menu/<int:id>', methods=['PUT'])
def edit_roles_menu(id):
    data = request.get_json()
    cnx = get_db_connection()
    if cnx is None:
        return jsonify({'status': 'error', 'message': 'No se pudo conectar a la base de datos.'}), 500

    try:
        cursor = cnx.cursor()
        query = f"""
            UPDATE `{TABLE_NAME}` SET
                menu1_Inventario = %s,
                submenu1_agregar_inventario = %s,
                menu2_Feedback = %s,
                submenu2_generador_encuestas = %s,
                submenu3_respuestas_comentarios = %s,
                menu3_Solicitud_Merchandising = %s,
                submenu4_nueva_solicitud = %s,
                submenu5_confirmados = %s,
                submenu6_entregados = %s,
                menu4_Administracion = %s,
                submenu7_roles = %s
            WHERE id = %s
        """
        values = (
            data.get('menu1_Inventario'),
            data.get('submenu1_agregar_inventario'),
            data.get('menu2_Feedback'),
            data.get('submenu2_generador_encuestas'),
            data.get('submenu3_respuestas_comentarios'),
            data.get('menu3_Solicitud_Merchandising'),
            data.get('submenu4_nueva_solicitud'),
            data.get('submenu5_confirmados'),
            data.get('submenu6_entregados'),
            data.get('menu4_Administracion'),
            data.get('submenu7_roles'),
            id
        )
        cursor.execute(query, values)
        cnx.commit()
        return jsonify({'status': 'success', 'message': 'Registro actualizado'}), 200
    except Exception as err:
        cnx.rollback()
        return jsonify({'status': 'error', 'message': str(err)}), 500
    finally:
        cursor.close()
        cnx.close()

# Endpoint para eliminar un registro
@roles_menu_bp.route('/roles_menu/<int:id>', methods=['DELETE'])
def delete_roles_menu(id):
    cnx = get_db_connection()
    if cnx is None:
        return jsonify({'status': 'error', 'message': 'No se pudo conectar a la base de datos.'}), 500

    try:
        cursor = cnx.cursor()
        query = f"DELETE FROM `{TABLE_NAME}` WHERE id = %s"
        cursor.execute(query, (id,))
        cnx.commit()
        return jsonify({'status': 'success', 'message': 'Registro eliminado'}), 200
    except Exception as err:
        cnx.rollback()
        return jsonify({'status': 'error', 'message': str(err)}), 500
    finally:
        cursor.close()
        cnx.close()
