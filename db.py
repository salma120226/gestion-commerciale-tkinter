import os
from decimal import Decimal

import mysql.connector
from mysql.connector import Error

CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "3308")),
    "user": os.getenv("DB_USER", "gestion"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": "GestionCommerciale",
    "charset": "utf8mb4",
    "autocommit": True,
}

class DBError(Exception):
    pass

def _msg(e):
    return getattr(e, "msg", None) or str(e)


def _clean(v):
   
    return float(v) if isinstance(v, Decimal) else v


def _connect():
    return mysql.connector.connect(**CONFIG)


def query(sql, params=None):

    conn = None
    try:
        conn = _connect()
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        rows = [{k: _clean(v) for k, v in r.items()} for r in cur.fetchall()]
        cur.close()
        return rows
    except Error as e:
        raise DBError(_msg(e)) from e
    finally:
        if conn is not None and conn.is_connected():
            conn.close()


def execute(sql, params=None):
    conn = None
    try:
        conn = _connect()
        cur = conn.cursor()
        cur.execute(sql, params or ())
        n = cur.rowcount
        cur.close()
        return n
    except Error as e:
        raise DBError(_msg(e)) from e
    finally:
        if conn is not None and conn.is_connected():
            conn.close()


def call_proc(name, args=()):
    
    conn = None
    try:
        conn = _connect()
        cur = conn.cursor()
        out = cur.callproc(name, list(args))
        results = []
        for rs in cur.stored_results():
            cols = rs.column_names
            results.append(
                [{c: _clean(v) for c, v in zip(cols, row)} for row in rs.fetchall()]
            )
        cur.close()
        return list(out), results
    except Error as e:
        raise DBError(_msg(e)) from e
    finally:
        if conn is not None and conn.is_connected():
            conn.close()
