#Autor: AvalonTM
#version: 0.0.1
#Tecnológico Nacional de México Campus Ensenada
#Clase de sistemas computacionales 4SS

#para instalar la libreria usar el comando: pip install mysql-connector-python

#Funciones basicas para MYSQL (QUERY, INSERT, UPDATE, DELETE)
#Eres bienvenido para colaborar con el codigo

import mysql.connector as _mysql
from mysql.connector import Error

class create:
    """
    Esta clase proporciona una interfaz para interactuar con una base de datos MySQL.
    Permite realizar operaciones como conexión, inserción, actualización, eliminación y cierre de la conexión.
    """
    
    # Constructor de la clase
    def __init__(self):
        """
        Inicializa una nueva instancia de la clase `lib_avalontm_mysql`.
        """
        self.conexion = None  # Atributo de la clase
        
    def conectar(self, _host = 'localhost', _port = 3306, _user = 'root', _password = '', _db = None):
        """
        Conecta a la base de datos MySQL con los parámetros especificados.

        :param _host: Dirección del host de la base de datos.
        :param _port: Puerto de la base de datos.
        :param _user: Nombre de usuario de la base de datos.
        :param _password: Contraseña del usuario.
        :param _db: Nombre de la base de datos.
        :return: `True` si la conexión es exitosa, `False` en caso de error.
        """
        try:
                
            self.conexion = _mysql.connect(host = _host,
                                            user = _user,
                                            password = _password,
                                            db = _db,
                                            port = _port
                                            )

            return self.conexion.is_connected()
                    
        except Error as e:
            print(f"Error: {e}")
            self.conexion = None
            return False
                
                
    def query(self, query):
        """
        Ejecuta una consulta SQL en la base de datos y devuelve los resultados.

        :param query: La consulta SQL que se desea ejecutar.
        :return: Una lista de tuplas con los resultados de la consulta o `None` en caso de error.
        """
        if not self.conexion or not self.conexion.is_connected():
            print("No hay conexión a la base de datos.")
            return None
        try:
            
            #ejecutamos un query
            cursor = self.conexion.cursor()
            cursor.execute(query)
                        
            #obtenemos los resultados
            resultado = cursor.fetchall()
                        
            return resultado
        except Error as e:
            print(f"Error al insertar datos: {e}")
            return None
    
    
    def insert(self, tabla, columnas, valores):
        """
        Inserta un nuevo registro en la tabla especificada.

        :param tabla: Nombre de la tabla en la que se insertará el registro.
        :param columnas: Lista de columnas en las que se insertarán los valores.
        :param valores: Lista de valores que se insertarán en las columnas.
        :return: El ID del último registro insertado o `None` en caso de error.
        """
        if not self.conexion or not self.conexion.is_connected():
            print("No hay conexión a la base de datos.")
            return None
       
        try:
            # Crear un cursor para ejecutar la consulta
            cursor = self.conexion.cursor()
            
            # Definir la consulta SQL para insertar datos
            columnas_placeholder = ', '.join(columnas)
            valores_placeholder = ', '.join(['%s'] * len(valores))
            insertar = f"INSERT INTO {tabla} ({columnas_placeholder}) VALUES ({valores_placeholder})"

            # Ejecutar la consulta
            cursor.execute(insertar, valores)
            
            #confirmar la transaccion
            self.conexion.commit()
            
            return cursor.lastrowid
        except Error as e:
            print(f"Error al insertar datos: {e}")
            return None
    
    def update(self, tabla, columnas, valores, condicion):
        """
        Actualiza registros en la tabla especificada basándose en la condición dada.

        :param tabla: Nombre de la tabla en la que se actualizarán los registros.
        :param columnas: Lista de columnas que se actualizarán.
        :param valores: Lista de nuevos valores correspondientes a las columnas.
        :param condicion: Condición para seleccionar los registros a actualizar.
        :return: Número de filas afectadas o `None` en caso de error.
        """
        if not self.conexion or not self.conexion.is_connected():
            print("No hay conexión a la base de datos.")
            return None

        try:
            # Crear un cursor para ejecutar la consulta
            cursor = self.conexion.cursor()

            # Construir la cláusula SET dinámicamente
            set_clause = ', '.join([f"{columna} = %s" for columna in columnas])
            update_query = f"UPDATE {tabla} SET {set_clause} WHERE {condicion}"

            # Ejecutar la consulta con los valores
            cursor.execute(update_query, valores)

            # Confirmar la transacción
            self.conexion.commit()

            # Retornar el número de filas afectadas
            return cursor.rowcount
        except Error as e:
            print(f"Error al actualizar datos: {e}")
            return None
    
    def delete(self, tabla, condicion):
        """
        Elimina registros de la tabla especificada basándose en la condición dada.

        :param tabla: Nombre de la tabla de la que se eliminarán los registros.
        :param condicion: Condición para seleccionar los registros a eliminar.
        :return: Número de filas afectadas o `None` en caso de error.
        """
        if not self.conexion or not self.conexion.is_connected():
            print("No hay conexión a la base de datos.")
            return None

        try:
            # Crear un cursor para ejecutar la consulta
            cursor = self.conexion.cursor()

            # Definir la consulta SQL para eliminar datos
            delete_query = f"DELETE FROM {tabla} WHERE {condicion}"

            # Ejecutar la consulta
            cursor.execute(delete_query)

            # Confirmar la transacción
            self.conexion.commit()

            # Retornar el número de filas afectadas
            return cursor.rowcount
        except Error as e:
            print(f"Error al eliminar datos: {e}")
            return None
                
    def close(self):
        """
        Cierra la conexión a la base de datos si está activa.
        """
        if not self.conexion or not self.conexion.is_connected():
            print("No hay conexión a la base de datos.")
            return None
    
        self.conexion.close()
        return self.conexion.is_connected()
