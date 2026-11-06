from datetime import date
from decimal import Decimal
import os
import oracledb
from dotenv import load_dotenv


load_dotenv()

ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD")
ORACLE_DSN = os.getenv("ORACLE_DSN")


class ConexionOracle:
    __conexion = None

    @classmethod
    def conectar(cls):
        try:
            if not ORACLE_USER or not ORACLE_PASSWORD or not ORACLE_DSN:
                raise RuntimeError("Faltan variables de Oracle en el archivo .env.")

            cls.__conexion = oracledb.connect(
                user=ORACLE_USER,
                password=ORACLE_PASSWORD,
                dsn=ORACLE_DSN
            )
        except oracledb.Error as error:
            print(f"Error de Oracle en conectar: {error}")
            conexion = getattr(ConexionOracle, "_ConexionOracle__conexion", None)
            if conexion is not None:
                try:
                    conexion.rollback()
                except oracledb.Error:
                    pass
            return False
        except (ValueError, TypeError, RuntimeError) as error:
            print(f"Error en conectar: {error}")
            return False

    @classmethod
    def obtener_conexion(cls):
        try:
            if cls.__conexion is None:
                raise RuntimeError("Primero debe conectarse a Oracle.")
            return cls.__conexion
        except oracledb.Error as error:
            print(f"Error de Oracle en obtener_conexion: {error}")
            conexion = getattr(ConexionOracle, "_ConexionOracle__conexion", None)
            if conexion is not None:
                try:
                    conexion.rollback()
                except oracledb.Error:
                    pass
            return None
        except (ValueError, TypeError, RuntimeError) as error:
            print(f"Error en obtener_conexion: {error}")
            return None

    @classmethod
    def cerrar(cls):
        try:
            if cls.__conexion is not None:
                cls.__conexion.close()
                cls.__conexion = None
        except oracledb.Error as error:
            print(f"Error de Oracle en cerrar: {error}")
            conexion = getattr(ConexionOracle, "_ConexionOracle__conexion", None)
            if conexion is not None:
                try:
                    conexion.rollback()
                except oracledb.Error:
                    pass
            return False
        except (ValueError, TypeError, RuntimeError) as error:
            print(f"Error en cerrar: {error}")
            return False


class Empleado:
    def __init__(self, nombre, direccion, telefono, correo_electronico,
                 fecha_inicio_contrato, salario, nombre_usuario,
                 contrasena_hash, rol="EMPLEADO", id_empleado=None):
        self.__id_empleado = id_empleado
        self.__nombre = nombre
        self.__direccion = direccion
        self.__telefono = telefono
        self.__correo_electronico = correo_electronico
        self.__fecha_inicio_contrato = fecha_inicio_contrato
        self.__salario = Decimal(salario)
        self.__nombre_usuario = nombre_usuario
        self.__contrasena_hash = contrasena_hash
        self.__rol = rol

    def get_id_empleado(self): return self.__id_empleado
    def set_id_empleado(self, valor): self.__id_empleado = valor
    def get_nombre(self): return self.__nombre
    def set_nombre(self, valor): self.__nombre = valor
    def get_direccion(self): return self.__direccion
    def set_direccion(self, valor): self.__direccion = valor
    def get_telefono(self): return self.__telefono
    def set_telefono(self, valor): self.__telefono = valor
    def get_correo_electronico(self): return self.__correo_electronico
    def set_correo_electronico(self, valor): self.__correo_electronico = valor
    def get_fecha_inicio_contrato(self): return self.__fecha_inicio_contrato
    def set_fecha_inicio_contrato(self, valor): self.__fecha_inicio_contrato = valor
    def get_salario(self): return self.__salario
    def set_salario(self, valor): self.__salario = Decimal(valor)
    def get_nombre_usuario(self): return self.__nombre_usuario
    def set_nombre_usuario(self, valor): self.__nombre_usuario = valor
    def get_contrasena_hash(self): return self.__contrasena_hash
    def set_contrasena_hash(self, valor): self.__contrasena_hash = valor
    def get_rol(self): return self.__rol
    def set_rol(self, valor): self.__rol = valor

    def actualizar_datos(self, direccion, telefono, correo):
        self.__direccion = direccion
        self.__telefono = telefono
        self.__correo_electronico = correo

    def autenticar(self, contrasena_hash):
        return self.__contrasena_hash == contrasena_hash

    def tiene_permiso(self, modulo):
        return modulo.upper() == self.__rol.upper()

    def registrar_tiempo(self, proyecto, fecha, horas, descripcion):
        return RegistroTiempo(fecha, horas, descripcion, self, proyecto)


class Administrador(Empleado):
    def __init__(self, nombre, direccion, telefono, correo_electronico,
                 fecha_inicio_contrato, salario, nombre_usuario,
                 contrasena_hash, area_administrada, id_empleado=None):
        super().__init__(nombre, direccion, telefono, correo_electronico,
                         fecha_inicio_contrato, salario, nombre_usuario,
                         contrasena_hash, "ADMINISTRADOR", id_empleado)
        self.__area_administrada = area_administrada

    def get_area_administrada(self): return self.__area_administrada
    def set_area_administrada(self, valor): self.__area_administrada = valor

    def gestionar_empleados(self, gestor): return gestor
    def gestionar_departamentos(self, gestor): return gestor
    def gestionar_proyectos(self, gestor): return gestor

    def generar_reporte(self, tipo):
        return Reporte(tipo, date.today(), "")


class Gerente(Empleado):
    def __init__(self, nombre, direccion, telefono, correo_electronico,
                 fecha_inicio_contrato, salario, nombre_usuario,
                 contrasena_hash, fecha_asignacion, id_empleado=None):
        super().__init__(nombre, direccion, telefono, correo_electronico,
                         fecha_inicio_contrato, salario, nombre_usuario,
                         contrasena_hash, "GERENTE", id_empleado)
        self.__fecha_asignacion = fecha_asignacion

    def get_fecha_asignacion(self): return self.__fecha_asignacion
    def set_fecha_asignacion(self, valor): self.__fecha_asignacion = valor


class Departamento:
    def __init__(self, nombre, gerente=None, empleados=None, id_departamento=None):
        self.__id_departamento = id_departamento
        self.__nombre = nombre
        self.__gerente = gerente
        self.__empleados = empleados if empleados is not None else []

    def get_id_departamento(self): return self.__id_departamento
    def set_id_departamento(self, valor): self.__id_departamento = valor
    def get_nombre(self): return self.__nombre
    def set_nombre(self, valor): self.__nombre = valor
    def get_gerente(self): return self.__gerente
    def set_gerente(self, valor): self.__gerente = valor
    def get_empleados(self): return self.__empleados

    def asignar_gerente(self, gerente): self.__gerente = gerente
    def agregar_empleado(self, empleado):
        if empleado not in self.__empleados: self.__empleados.append(empleado)
    def remover_empleado(self, empleado):
        if empleado in self.__empleados: self.__empleados.remove(empleado)
    def buscar_empleado(self, id_empleado):
        for empleado in self.__empleados:
            if empleado.get_id_empleado() == id_empleado: return empleado
        return None


class Proyecto:
    def __init__(self, nombre, descripcion, fecha_inicio, estado="PLANIFICADO",
                 empleados=None, id_proyecto=None):
        self.__id_proyecto = id_proyecto
        self.__nombre = nombre
        self.__descripcion = descripcion
        self.__fecha_inicio = fecha_inicio
        self.__estado = estado
        self.__empleados = empleados if empleados is not None else []

    def get_id_proyecto(self): return self.__id_proyecto
    def set_id_proyecto(self, valor): self.__id_proyecto = valor
    def get_nombre(self): return self.__nombre
    def set_nombre(self, valor): self.__nombre = valor
    def get_descripcion(self): return self.__descripcion
    def set_descripcion(self, valor): self.__descripcion = valor
    def get_fecha_inicio(self): return self.__fecha_inicio
    def set_fecha_inicio(self, valor): self.__fecha_inicio = valor
    def get_estado(self): return self.__estado
    def set_estado(self, valor): self.__estado = valor
    def get_empleados(self): return self.__empleados

    def actualizar_datos(self, nombre, descripcion, fecha_inicio):
        self.__nombre = nombre
        self.__descripcion = descripcion
        self.__fecha_inicio = fecha_inicio

    def asignar_empleado(self, empleado):
        if empleado not in self.__empleados: self.__empleados.append(empleado)
    def desasignar_empleado(self, empleado):
        if empleado in self.__empleados: self.__empleados.remove(empleado)


class RegistroTiempo:
    def __init__(self, fecha, horas_trabajadas, descripcion_tarea,
                 empleado, proyecto, id_registro=None):
        self.__id_registro = id_registro
        self.__fecha = fecha
        self.__horas_trabajadas = Decimal(horas_trabajadas)
        self.__descripcion_tarea = descripcion_tarea
        self.__empleado = empleado
        self.__proyecto = proyecto

    def get_id_registro(self): return self.__id_registro
    def set_id_registro(self, valor): self.__id_registro = valor
    def get_fecha(self): return self.__fecha
    def set_fecha(self, valor): self.__fecha = valor
    def get_horas_trabajadas(self): return self.__horas_trabajadas
    def set_horas_trabajadas(self, valor): self.__horas_trabajadas = Decimal(valor)
    def get_descripcion_tarea(self): return self.__descripcion_tarea
    def set_descripcion_tarea(self, valor): self.__descripcion_tarea = valor
    def get_empleado(self): return self.__empleado
    def set_empleado(self, valor): self.__empleado = valor
    def get_proyecto(self): return self.__proyecto
    def set_proyecto(self, valor): self.__proyecto = valor

    def validar_horas(self):
        return Decimal("0") < self.__horas_trabajadas <= Decimal("24")

    def actualizar_registro(self, fecha, horas, descripcion):
        self.__fecha = fecha
        self.__horas_trabajadas = Decimal(horas)
        self.__descripcion_tarea = descripcion

    def obtener_resumen(self):
        return f"{self.__fecha}: {self.__horas_trabajadas} horas - {self.__descripcion_tarea}"


class Reporte:
    def __init__(self, tipo, fecha_generacion, contenido, id_reporte=None):
        self.__id_reporte = id_reporte
        self.__tipo = tipo
        self.__fecha_generacion = fecha_generacion
        self.__contenido = contenido

    def get_id_reporte(self): return self.__id_reporte
    def set_id_reporte(self, valor): self.__id_reporte = valor
    def get_tipo(self): return self.__tipo
    def set_tipo(self, valor): self.__tipo = valor
    def get_fecha_generacion(self): return self.__fecha_generacion
    def set_fecha_generacion(self, valor): self.__fecha_generacion = valor
    def get_contenido(self): return self.__contenido
    def set_contenido(self, valor): self.__contenido = valor
    def generar_contenido(self): return self.__contenido


class GestorEmpleado:
    def __init__(self):
        self.__empleados = []

    def registrar_empleado(self, empleado):
        try:
            conexion = ConexionOracle.obtener_conexion()
            cursor = conexion.cursor()
            nuevo_id = cursor.var(oracledb.NUMBER)
            cursor.execute("""INSERT INTO empleado
                (nombre,direccion,telefono,correo_electronico,fecha_inicio_contrato,
                 salario,nombre_usuario,contrasena_hash,rol,area_administrada,fecha_asignacion)
                VALUES (:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11)
                RETURNING id_empleado INTO :12""",
                [empleado.get_nombre(), empleado.get_direccion(), empleado.get_telefono(),
                 empleado.get_correo_electronico(), empleado.get_fecha_inicio_contrato(),
                 empleado.get_salario(), empleado.get_nombre_usuario(),
                 empleado.get_contrasena_hash(), empleado.get_rol(),
                 empleado.get_area_administrada() if isinstance(empleado, Administrador) else None,
                 empleado.get_fecha_asignacion() if isinstance(empleado, Gerente) else None,
                 nuevo_id])
            empleado.set_id_empleado(int(nuevo_id.getvalue()[0]))
            conexion.commit(); cursor.close()
            return empleado
        except oracledb.Error as error:
            print(f"Error de Oracle en registrar_empleado: {error}")
            conexion = getattr(ConexionOracle, "_ConexionOracle__conexion", None)
            if conexion is not None:
                try:
                    conexion.rollback()
                except oracledb.Error:
                    pass
            return None
        except (ValueError, TypeError, RuntimeError) as error:
            print(f"Error en registrar_empleado: {error}")
            return None

    def buscar_empleado(self, id_empleado):
        try:
            conexion = ConexionOracle.obtener_conexion(); cursor = conexion.cursor()
            cursor.execute("SELECT * FROM empleado WHERE id_empleado=:1", [id_empleado])
            fila = cursor.fetchone(); cursor.close()
            return self.__crear_objeto(fila) if fila else None
        except oracledb.Error as error:
            print(f"Error de Oracle en buscar_empleado: {error}")
            conexion = getattr(ConexionOracle, "_ConexionOracle__conexion", None)
            if conexion is not None:
                try:
                    conexion.rollback()
                except oracledb.Error:
                    pass
            return None
        except (ValueError, TypeError, RuntimeError) as error:
            print(f"Error en buscar_empleado: {error}")
            return None

    def listar_empleados(self):
        try:
            conexion = ConexionOracle.obtener_conexion(); cursor = conexion.cursor()
            cursor.execute("SELECT * FROM empleado ORDER BY id_empleado")
            objetos = [self.__crear_objeto(fila) for fila in cursor.fetchall()]
            cursor.close(); return objetos
        except oracledb.Error as error:
            print(f"Error de Oracle en listar_empleados: {error}")
            conexion = getattr(ConexionOracle, "_ConexionOracle__conexion", None)
            if conexion is not None:
                try:
                    conexion.rollback()
                except oracledb.Error:
                    pass
            return []
        except (ValueError, TypeError, RuntimeError) as error:
            print(f"Error en listar_empleados: {error}")
            return []

    def editar_empleado(self, empleado):
        try:
            conexion = ConexionOracle.obtener_conexion(); cursor = conexion.cursor()
            cursor.execute("""UPDATE empleado SET nombre=:1,direccion=:2,telefono=:3,
                correo_electronico=:4,fecha_inicio_contrato=:5,salario=:6,
                nombre_usuario=:7,contrasena_hash=:8,rol=:9,area_administrada=:10,
                fecha_asignacion=:11 WHERE id_empleado=:12""",
                [empleado.get_nombre(), empleado.get_direccion(), empleado.get_telefono(),
                 empleado.get_correo_electronico(), empleado.get_fecha_inicio_contrato(),
                 empleado.get_salario(), empleado.get_nombre_usuario(),
                 empleado.get_contrasena_hash(), empleado.get_rol(),
                 empleado.get_area_administrada() if isinstance(empleado, Administrador) else None,
                 empleado.get_fecha_asignacion() if isinstance(empleado, Gerente) else None,
                 empleado.get_id_empleado()])
            ok = cursor.rowcount == 1; conexion.commit(); cursor.close(); return ok
        except oracledb.Error as error:
            print(f"Error de Oracle en editar_empleado: {error}")
            conexion = getattr(ConexionOracle, "_ConexionOracle__conexion", None)
            if conexion is not None:
                try:
                    conexion.rollback()
                except oracledb.Error:
                    pass
            return False
        except (ValueError, TypeError, RuntimeError) as error:
            print(f"Error en editar_empleado: {error}")
            return False

    def eliminar_empleado(self, id_empleado):
        try:
            return self.__eliminar("DELETE FROM empleado WHERE id_empleado=:1", id_empleado)
        except oracledb.Error as error:
            print(f"Error de Oracle en eliminar_empleado: {error}")
            conexion = getattr(ConexionOracle, "_ConexionOracle__conexion", None)
            if conexion is not None:
                try:
                    conexion.rollback()
                except oracledb.Error:
                    pass
            return False
        except (ValueError, TypeError, RuntimeError) as error:
            print(f"Error en eliminar_empleado: {error}")
            return False

    def asignar_departamento(self, empleado, departamento):
        try:
            conexion = ConexionOracle.obtener_conexion(); cursor = conexion.cursor()
            cursor.execute("UPDATE empleado SET id_departamento=:1 WHERE id_empleado=:2",
                           [departamento.get_id_departamento(), empleado.get_id_empleado()])
            conexion.commit(); cursor.close(); departamento.agregar_empleado(empleado)
        except oracledb.Error as error:
            print(f"Error de Oracle en asignar_departamento: {error}")
            conexion = getattr(ConexionOracle, "_ConexionOracle__conexion", None)
            if conexion is not None:
                try:
                    conexion.rollback()
                except oracledb.Error:
                    pass
            return False
        except (ValueError, TypeError, RuntimeError) as error:
            print(f"Error en asignar_departamento: {error}")
            return False

    def reasignar_departamento(self, empleado, departamento):
        try:
            self.asignar_departamento(empleado, departamento)
        except oracledb.Error as error:
            print(f"Error de Oracle en reasignar_departamento: {error}")
            conexion = getattr(ConexionOracle, "_ConexionOracle__conexion", None)
            if conexion is not None:
                try:
                    conexion.rollback()
                except oracledb.Error:
                    pass
            return False
        except (ValueError, TypeError, RuntimeError) as error:
            print(f"Error en reasignar_departamento: {error}")
            return False

    def validar_datos(self, empleado):
        try:
            return empleado.get_nombre() != "" and empleado.get_salario() >= 0
        except oracledb.Error as error:
            print(f"Error de Oracle en validar_datos: {error}")
            conexion = getattr(ConexionOracle, "_ConexionOracle__conexion", None)
            if conexion is not None:
                try:
                    conexion.rollback()
                except oracledb.Error:
                    pass
            return None
        except (ValueError, TypeError, RuntimeError) as error:
            print(f"Error en validar_datos: {error}")
            return None

    def __eliminar(self, sql, identificador):
        conexion = ConexionOracle.obtener_conexion(); cursor = conexion.cursor()
        cursor.execute(sql, [identificador]); ok = cursor.rowcount == 1
        conexion.commit(); cursor.close(); return ok

    def __crear_objeto(self, f):
        base = [f[1], f[2], f[3], f[4], f[5], f[6], f[7], f[8]]
        if f[9] == "ADMINISTRADOR": return Administrador(*base, f[10], f[0])
        if f[9] == "GERENTE": return Gerente(*base, f[11], f[0])
        return Empleado(*base, f[9], f[0])


class GestorDepartamento:
    def __init__(self): self.__departamentos = []

    def crear_departamento(self, departamento):
        try:
            conexion = ConexionOracle.obtener_conexion(); cursor = conexion.cursor()
            nuevo_id = cursor.var(oracledb.NUMBER)
            gerente = departamento.get_gerente()
            cursor.execute("""INSERT INTO departamento(nombre,id_gerente)
                VALUES(:1,:2) RETURNING id_departamento INTO :3""",
                [departamento.get_nombre(), gerente.get_id_empleado() if gerente else None, nuevo_id])
            departamento.set_id_departamento(int(nuevo_id.getvalue()[0]))
            conexion.commit(); cursor.close(); return departamento
        except oracledb.Error as error:
            print(f"Error de Oracle en crear_departamento: {error}")
            conexion = getattr(ConexionOracle, "_ConexionOracle__conexion", None)
            if conexion is not None:
                try:
                    conexion.rollback()
                except oracledb.Error:
                    pass
            return None
        except (ValueError, TypeError, RuntimeError) as error:
            print(f"Error en crear_departamento: {error}")
            return None

    def buscar_departamento(self, id_departamento):
        try:
            conexion = ConexionOracle.obtener_conexion(); cursor = conexion.cursor()
            cursor.execute("SELECT id_departamento,nombre,id_gerente FROM departamento WHERE id_departamento=:1", [id_departamento])
            fila = cursor.fetchone(); cursor.close()
            if not fila: return None
            gerente = GestorEmpleado().buscar_empleado(fila[2]) if fila[2] else None
            return Departamento(fila[1], gerente, [], fila[0])
        except oracledb.Error as error:
            print(f"Error de Oracle en buscar_departamento: {error}")
            conexion = getattr(ConexionOracle, "_ConexionOracle__conexion", None)
            if conexion is not None:
                try:
                    conexion.rollback()
                except oracledb.Error:
                    pass
            return None
        except (ValueError, TypeError, RuntimeError) as error:
            print(f"Error en buscar_departamento: {error}")
            return None

    def listar_departamentos(self):
        try:
            conexion = ConexionOracle.obtener_conexion(); cursor = conexion.cursor()
            cursor.execute("SELECT id_departamento,nombre,id_gerente FROM departamento ORDER BY id_departamento")
            filas = cursor.fetchall(); cursor.close()
            return [Departamento(f[1], GestorEmpleado().buscar_empleado(f[2]) if f[2] else None, [], f[0]) for f in filas]
        except oracledb.Error as error:
            print(f"Error de Oracle en listar_departamentos: {error}")
            conexion = getattr(ConexionOracle, "_ConexionOracle__conexion", None)
            if conexion is not None:
                try:
                    conexion.rollback()
                except oracledb.Error:
                    pass
            return []
        except (ValueError, TypeError, RuntimeError) as error:
            print(f"Error en listar_departamentos: {error}")
            return []

    def editar_departamento(self, departamento):
        try:
            conexion = ConexionOracle.obtener_conexion(); cursor = conexion.cursor(); gerente = departamento.get_gerente()
            cursor.execute("UPDATE departamento SET nombre=:1,id_gerente=:2 WHERE id_departamento=:3",
                           [departamento.get_nombre(), gerente.get_id_empleado() if gerente else None, departamento.get_id_departamento()])
            ok = cursor.rowcount == 1; conexion.commit(); cursor.close(); return ok
        except oracledb.Error as error:
            print(f"Error de Oracle en editar_departamento: {error}")
            conexion = getattr(ConexionOracle, "_ConexionOracle__conexion", None)
            if conexion is not None:
                try:
                    conexion.rollback()
                except oracledb.Error:
                    pass
            return False
        except (ValueError, TypeError, RuntimeError) as error:
            print(f"Error en editar_departamento: {error}")
            return False

    def eliminar_departamento(self, id_departamento):
        try:
            conexion = ConexionOracle.obtener_conexion(); cursor = conexion.cursor()
            cursor.execute("DELETE FROM departamento WHERE id_departamento=:1", [id_departamento])
            ok = cursor.rowcount == 1; conexion.commit(); cursor.close(); return ok
        except oracledb.Error as error:
            print(f"Error de Oracle en eliminar_departamento: {error}")
            conexion = getattr(ConexionOracle, "_ConexionOracle__conexion", None)
            if conexion is not None:
                try:
                    conexion.rollback()
                except oracledb.Error:
                    pass
            return False
        except (ValueError, TypeError, RuntimeError) as error:
            print(f"Error en eliminar_departamento: {error}")
            return False

    def asignar_gerente(self, departamento, gerente):
        try:
            departamento.asignar_gerente(gerente); return self.editar_departamento(departamento)
        except oracledb.Error as error:
            print(f"Error de Oracle en asignar_gerente: {error}")
            conexion = getattr(ConexionOracle, "_ConexionOracle__conexion", None)
            if conexion is not None:
                try:
                    conexion.rollback()
                except oracledb.Error:
                    pass
            return False
        except (ValueError, TypeError, RuntimeError) as error:
            print(f"Error en asignar_gerente: {error}")
            return False


class GestorProyecto:
    def __init__(self): self.__proyectos = []

    def crear_proyecto(self, proyecto):
        try:
            conexion = ConexionOracle.obtener_conexion(); cursor = conexion.cursor(); nuevo_id = cursor.var(oracledb.NUMBER)
            cursor.execute("""INSERT INTO proyecto(nombre,descripcion,fecha_inicio,estado)
                VALUES(:1,:2,:3,:4) RETURNING id_proyecto INTO :5""",
                [proyecto.get_nombre(), proyecto.get_descripcion(), proyecto.get_fecha_inicio(), proyecto.get_estado(), nuevo_id])
            proyecto.set_id_proyecto(int(nuevo_id.getvalue()[0])); conexion.commit(); cursor.close(); return proyecto
        except oracledb.Error as error:
            print(f"Error de Oracle en crear_proyecto: {error}")
            conexion = getattr(ConexionOracle, "_ConexionOracle__conexion", None)
            if conexion is not None:
                try:
                    conexion.rollback()
                except oracledb.Error:
                    pass
            return None
        except (ValueError, TypeError, RuntimeError) as error:
            print(f"Error en crear_proyecto: {error}")
            return None

    def buscar_proyecto(self, id_proyecto):
        try:
            conexion = ConexionOracle.obtener_conexion(); cursor = conexion.cursor()
            cursor.execute("SELECT id_proyecto,nombre,descripcion,fecha_inicio,estado FROM proyecto WHERE id_proyecto=:1", [id_proyecto])
            f = cursor.fetchone(); cursor.close()
            return Proyecto(f[1], f[2], f[3], f[4], [], f[0]) if f else None
        except oracledb.Error as error:
            print(f"Error de Oracle en buscar_proyecto: {error}")
            conexion = getattr(ConexionOracle, "_ConexionOracle__conexion", None)
            if conexion is not None:
                try:
                    conexion.rollback()
                except oracledb.Error:
                    pass
            return None
        except (ValueError, TypeError, RuntimeError) as error:
            print(f"Error en buscar_proyecto: {error}")
            return None

    def listar_proyectos(self):
        try:
            conexion = ConexionOracle.obtener_conexion(); cursor = conexion.cursor()
            cursor.execute("SELECT id_proyecto,nombre,descripcion,fecha_inicio,estado FROM proyecto ORDER BY id_proyecto")
            objetos = [Proyecto(f[1], f[2], f[3], f[4], [], f[0]) for f in cursor.fetchall()]
            cursor.close(); return objetos
        except oracledb.Error as error:
            print(f"Error de Oracle en listar_proyectos: {error}")
            conexion = getattr(ConexionOracle, "_ConexionOracle__conexion", None)
            if conexion is not None:
                try:
                    conexion.rollback()
                except oracledb.Error:
                    pass
            return []
        except (ValueError, TypeError, RuntimeError) as error:
            print(f"Error en listar_proyectos: {error}")
            return []

    def editar_proyecto(self, proyecto):
        try:
            conexion = ConexionOracle.obtener_conexion(); cursor = conexion.cursor()
            cursor.execute("""UPDATE proyecto SET nombre=:1,descripcion=:2,fecha_inicio=:3,
                estado=:4 WHERE id_proyecto=:5""",
                [proyecto.get_nombre(), proyecto.get_descripcion(), proyecto.get_fecha_inicio(), proyecto.get_estado(), proyecto.get_id_proyecto()])
            ok = cursor.rowcount == 1; conexion.commit(); cursor.close(); return ok
        except oracledb.Error as error:
            print(f"Error de Oracle en editar_proyecto: {error}")
            conexion = getattr(ConexionOracle, "_ConexionOracle__conexion", None)
            if conexion is not None:
                try:
                    conexion.rollback()
                except oracledb.Error:
                    pass
            return False
        except (ValueError, TypeError, RuntimeError) as error:
            print(f"Error en editar_proyecto: {error}")
            return False

    def eliminar_proyecto(self, id_proyecto):
        try:
            conexion = ConexionOracle.obtener_conexion(); cursor = conexion.cursor()
            cursor.execute("DELETE FROM proyecto WHERE id_proyecto=:1", [id_proyecto])
            ok = cursor.rowcount == 1; conexion.commit(); cursor.close(); return ok
        except oracledb.Error as error:
            print(f"Error de Oracle en eliminar_proyecto: {error}")
            conexion = getattr(ConexionOracle, "_ConexionOracle__conexion", None)
            if conexion is not None:
                try:
                    conexion.rollback()
                except oracledb.Error:
                    pass
            return False
        except (ValueError, TypeError, RuntimeError) as error:
            print(f"Error en eliminar_proyecto: {error}")
            return False

    def asignar_empleado(self, proyecto, empleado):
        try:
            conexion = ConexionOracle.obtener_conexion(); cursor = conexion.cursor()
            cursor.execute("INSERT INTO empleado_proyecto(id_empleado,id_proyecto) VALUES(:1,:2)",
                           [empleado.get_id_empleado(), proyecto.get_id_proyecto()])
            conexion.commit(); cursor.close(); proyecto.asignar_empleado(empleado)
        except oracledb.Error as error:
            print(f"Error de Oracle en asignar_empleado: {error}")
            conexion = getattr(ConexionOracle, "_ConexionOracle__conexion", None)
            if conexion is not None:
                try:
                    conexion.rollback()
                except oracledb.Error:
                    pass
            return False
        except (ValueError, TypeError, RuntimeError) as error:
            print(f"Error en asignar_empleado: {error}")
            return False

    def desasignar_empleado(self, proyecto, empleado):
        try:
            conexion = ConexionOracle.obtener_conexion(); cursor = conexion.cursor()
            cursor.execute("DELETE FROM empleado_proyecto WHERE id_empleado=:1 AND id_proyecto=:2",
                           [empleado.get_id_empleado(), proyecto.get_id_proyecto()])
            conexion.commit(); cursor.close(); proyecto.desasignar_empleado(empleado)
        except oracledb.Error as error:
            print(f"Error de Oracle en desasignar_empleado: {error}")
            conexion = getattr(ConexionOracle, "_ConexionOracle__conexion", None)
            if conexion is not None:
                try:
                    conexion.rollback()
                except oracledb.Error:
                    pass
            return False
        except (ValueError, TypeError, RuntimeError) as error:
            print(f"Error en desasignar_empleado: {error}")
            return False


class GestorRegistroTiempo:
    def crear_registro(self, registro):
        try:
            if not registro.validar_horas(): raise ValueError("Horas no validas.")
            conexion = ConexionOracle.obtener_conexion(); cursor = conexion.cursor(); nuevo_id = cursor.var(oracledb.NUMBER)
            cursor.execute("""INSERT INTO registro_tiempo(fecha,horas_trabajadas,
                descripcion_tarea,id_empleado,id_proyecto) VALUES(:1,:2,:3,:4,:5)
                RETURNING id_registro INTO :6""",
                [registro.get_fecha(), registro.get_horas_trabajadas(), registro.get_descripcion_tarea(),
                 registro.get_empleado().get_id_empleado(), registro.get_proyecto().get_id_proyecto(), nuevo_id])
            registro.set_id_registro(int(nuevo_id.getvalue()[0])); conexion.commit(); cursor.close(); return registro
        except oracledb.Error as error:
            print(f"Error de Oracle en crear_registro: {error}")
            conexion = getattr(ConexionOracle, "_ConexionOracle__conexion", None)
            if conexion is not None:
                try:
                    conexion.rollback()
                except oracledb.Error:
                    pass
            return None
        except (ValueError, TypeError, RuntimeError) as error:
            print(f"Error en crear_registro: {error}")
            return None

    def buscar_registro(self, id_registro):
        try:
            conexion = ConexionOracle.obtener_conexion(); cursor = conexion.cursor()
            cursor.execute("SELECT id_registro,fecha,horas_trabajadas,descripcion_tarea,id_empleado,id_proyecto FROM registro_tiempo WHERE id_registro=:1", [id_registro])
            f = cursor.fetchone(); cursor.close()
            if not f: return None
            return RegistroTiempo(f[1], f[2], f[3], GestorEmpleado().buscar_empleado(f[4]), GestorProyecto().buscar_proyecto(f[5]), f[0])
        except oracledb.Error as error:
            print(f"Error de Oracle en buscar_registro: {error}")
            conexion = getattr(ConexionOracle, "_ConexionOracle__conexion", None)
            if conexion is not None:
                try:
                    conexion.rollback()
                except oracledb.Error:
                    pass
            return None
        except (ValueError, TypeError, RuntimeError) as error:
            print(f"Error en buscar_registro: {error}")
            return None

    def editar_registro(self, registro):
        try:
            conexion = ConexionOracle.obtener_conexion(); cursor = conexion.cursor()
            cursor.execute("""UPDATE registro_tiempo SET fecha=:1,horas_trabajadas=:2,
                descripcion_tarea=:3,id_empleado=:4,id_proyecto=:5 WHERE id_registro=:6""",
                [registro.get_fecha(), registro.get_horas_trabajadas(), registro.get_descripcion_tarea(),
                 registro.get_empleado().get_id_empleado(), registro.get_proyecto().get_id_proyecto(), registro.get_id_registro()])
            ok = cursor.rowcount == 1; conexion.commit(); cursor.close(); return ok
        except oracledb.Error as error:
            print(f"Error de Oracle en editar_registro: {error}")
            conexion = getattr(ConexionOracle, "_ConexionOracle__conexion", None)
            if conexion is not None:
                try:
                    conexion.rollback()
                except oracledb.Error:
                    pass
            return False
        except (ValueError, TypeError, RuntimeError) as error:
            print(f"Error en editar_registro: {error}")
            return False

    def eliminar_registro(self, id_registro):
        try:
            conexion = ConexionOracle.obtener_conexion(); cursor = conexion.cursor()
            cursor.execute("DELETE FROM registro_tiempo WHERE id_registro=:1", [id_registro])
            ok = cursor.rowcount == 1; conexion.commit(); cursor.close(); return ok
        except oracledb.Error as error:
            print(f"Error de Oracle en eliminar_registro: {error}")
            conexion = getattr(ConexionOracle, "_ConexionOracle__conexion", None)
            if conexion is not None:
                try:
                    conexion.rollback()
                except oracledb.Error:
                    pass
            return False
        except (ValueError, TypeError, RuntimeError) as error:
            print(f"Error en eliminar_registro: {error}")
            return False
