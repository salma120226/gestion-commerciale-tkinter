
import mysql.connector
from mysql.connector import Error


def connect_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="Nova2026!",
            database="GestionCommerciale"
        )

        return connection

    except Error as e:
        print(f"Erreur de connexion : {e}")
        return None


def fetch_data(query, values=None):
    connection = connect_db()

    if connection is None:
        return []

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, values or ())
        result = cursor.fetchall()
        cursor.close()
        return result

    except Error as e:
        print(f"Erreur SQL : {e}")
        return []

    finally:
        connection.close()


def execute_query(query, values=None):
    connection = connect_db()

    if connection is None:
        return False

    try:
        cursor = connection.cursor()
        cursor.execute(query, values or ())
        connection.commit()
        cursor.close()
        return True

    except Error as e:
        print(f"Erreur SQL : {e}")
        connection.rollback()
        return False

    finally:
        connection.close()


def call_procedure(procedure, values=None):
    connection = connect_db()

    if connection is None:
        return []

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.callproc(procedure, values or ())

        results = []

        for result in cursor.stored_results():
            results.append(result.fetchall())

        connection.commit()
        cursor.close()

        return results

    except Error as e:
        print(f"Erreur Procedure : {e}")
        connection.rollback()
        return []

    finally:
        connection.close()
def run_query(query, values=None):
    connection = connect_db()

    if connection is None:
        return {"ok": False, "error": "Connexion à la base de données impossible.", "errno": None, "id": None}

    try:
        cursor = connection.cursor()
        cursor.execute(query, values or ())
        connection.commit()
        last_id = cursor.lastrowid
        cursor.close()
        return {"ok": True, "error": None, "errno": None, "id": last_id}

    except Error as e:
        connection.rollback()
        return {"ok": False, "error": getattr(e, "msg", str(e)), "errno": getattr(e, "errno", None), "id": None}

    finally:
        connection.close()


def run_procedure(procedure, values=None):
    connection = connect_db()

    if connection is None:
        return {"ok": False, "error": "Connexion à la base de données impossible.", "args": [], "results": []}

    try:
        cursor = connection.cursor(dictionary=True)
        args = cursor.callproc(procedure, values or ())
        results = [result.fetchall() for result in cursor.stored_results()]
        connection.commit()
        cursor.close()
        return {"ok": True, "error": None, "args": list(args), "results": results}

    except Error as e:
        connection.rollback()
        return {"ok": False, "error": getattr(e, "msg", str(e)), "args": [], "results": []}

    finally:
        connection.close()