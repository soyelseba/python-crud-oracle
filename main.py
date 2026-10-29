from db import conexion

with conexion.abrir() as resultado:
  print("Conexión exitosa")

def crear_tabla_personas():
  query = """CREATE TABLE PERSONAS(
    id NUMBER PRIMARY KEY,
    nombre_completo VARCHAR2(64),
    correo VARCHAR2(64),
    fecha_nacimiento DATE
  )
  """
  cursor = conexion.cursor()
  cursor.execute(query)
  conexion.commit()