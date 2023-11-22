# -*- coding: utf-8 -*-

# Importa bibliotecas.
import sqlite3

from flask import Flask, Response, abort, json, jsonify, make_response, request

# Cria aplicativo Flask.
app = Flask(__name__)

# Configura o character set das transações HTTP para UTF-8.
json.provider.DefaultJSONProvider.ensure_ascii = False

# Especifica a base de dados SQLite3.
database = "./db/temp_db.db"

# Obtém todos os registros válidos de 'item'.
# Request method → GET
# Request endpoint → /items
# Response → JSON

def prefix_remove(prefix, data):
    new_data = {}
    for key, value in data.items():
        if key.startswith(prefix):
            new_key = key[len(prefix):]
            new_data[new_key] = value
        else:
            new_data[key] = value
    return new_data

@app.route("/items", methods=["GET"])
def get_all():
    try:
        # Conectar ao banco de dados SQLite.
        conn = sqlite3.connect(database)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Consulta SQL para selecionar todos os itens ativos.
        sql = "SELECT * FROM item WHERE item_status != 'off'"
        cursor.execute(sql)
        rows_data = cursor.fetchall()
        conn.close()

        # Converter os resultados em uma lista de dicionários.
        list_data = []
        for row_data in rows_data:
            list_data.append(dict(row_data))

        # Retornar os dados ou um erro se nenhum item for encontrado.
        if list_data:
            return list_data
        else:
            return {"error": "Nenhum item encontrado"}

    # Tratamento de exceções.
    except sqlite3.Error as error:
        return {"error": f"Erro ao acessar o banco de dados: {str(error)}"}
    except Exception as error:
        return {"error": f"Erro inesperado: {str(error)}"}

@app.route("/items", methods=["POST"])
def create():
    try:
        
        post_data = request.get_json()
        print(post_data)
        
        # Conectar ao banco de dados SQLite.
        conn = sqlite3.connect(database)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        sql = """
            INSERT INTO item 
                (item_name, item_description, item_location, item_owner) 
            VALUES (?, ?, ?, ?);
        """
        cursor.execute(sql, (
            post_data['item_name'],
            post_data['item_description'],
            post_data['item_location'],
            post_data['item_owner']
        ))
        conn.commit()
        conn.close()

        return ["success", "Item cadastrado com sucesso!"]
        
    # Tratamento de exceções.
    except sqlite3.Error as error:
        return {"error": f"Erro ao acessar o banco de dados: {str(error)}"}
    except Exception as error:
        return {"error": f"Erro inesperado: {str(error)}"}
    


@app.route("/items/<int:id>", methods=["GET"])
def get_one(id):
    try:
        conn = sqlite3.connect(database)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM item WHERE item_id = ? AND item_status = 'on'", (id,))
        
        item_row = cursor.fetchone()
        
        conn.close()
        
        if item_row:
            
            item = dict(item_row)
            
            new_item = prefix_remove('item_', item)
            
            return new_item, 200
        
        else:
            return {"success", "Item não encontrado!"}, 404
        
    except sqlite3.Error as error:
        return {"error": f"Erro ao acessar o banco de dados: {str(error)}"}, 500
    except Exception as error:
        return {"error": f"Erro inesperado: {str(error)}"}, 500

@app.route("/items/<int:id>", methods=["DELETE"])
def delete(id):
    try:
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        
        sql = "UPDATE item SET item_status = 'off' WHERE item_id = ?"
        
        cursor.execute(sql, (id,))
        
        conn.commit()
        
    except sqlite3.Error as e:
        return {"error": f"Erro ao acessar banco de dados: {str(e)}"}, 500
    
    except Exception as error:
        return {"error": f"Erro inesperado: {str(error)}"}, 500
    

# Roda aplicativo Flask.
if __name__ == "__main__":
    app.run(debug=True)

