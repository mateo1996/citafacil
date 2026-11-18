
from infrastructure.database.mysql_db import obtain_conection


def probar_conexion():
    conexion = obtain_conection()

    if conexion is None:
        print("Error: no fue posible conectar con MySQL.")
        return

    try:
        cursor = conexion.cursor()

        cursor.execute("SELECT DATABASE()")
        resultado = cursor.fetchone()

        print("¡Conexión exitosa con MySQL!")
        print(f"Base de datos conectada: {resultado[0]}")

        cursor.close()

    except Exception as error:
        print(f"Error durante la consulta: {error}")

    finally:
        conexion.close()


if __name__ == "__main__":
    probar_conexion()
