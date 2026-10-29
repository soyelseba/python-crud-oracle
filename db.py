import oracledb
import os
from dotenv import load_dotenv

load_dotenv()

ORACLE_USER= os.getenv("ORACLE_USER")
ORACLE_PASSWORD= os.getenv("ORACLE_PASSWORD")
ORACLE_DSN= os.getenv("ORACLE_DSN")

class ConexionOracle:
  def __init__(self, user, password, dsn):
    self.__user = user
    self.__password = password
    self.__dsn = dsn

  def abrir(self):
    return oracledb.connect(
      user=self.__user,
      password=self.__password,
      dsn=self.__dsn
    )

conexion = ConexionOracle(
  user = ORACLE_USER,
  password = ORACLE_PASSWORD,
  dsn = ORACLE_DSN
)
  