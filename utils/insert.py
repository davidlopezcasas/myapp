import pandas as pd
import pymysql

# Configuración de la base de datos
db_config = {
    'host': 'database-1.c3k4aaugutfg.eu-west-3.rds.amazonaws.com',
    'user': 'admin',
    'password': 'poporu2015',
    'database': 'lopezcazas'
}

# Conexión a la base de datos
connection = pymysql.connect(**db_config)

# Leer el archivo Excel
excel_path = '/Users/david/Downloads/ARTICULOS.xlsx'  # e.g., 'productos.xlsx'
df = pd.read_excel(excel_path)

# Verificar las columnas esperadas
if 'numero' not in df.columns or 'nombre' not in df.columns:
    raise ValueError("El archivo Excel debe contener las columnas 'numero' y 'nombre'.")

# Crear un cursor para ejecutar las consultas SQL
cursor = connection.cursor()

# Insertar los datos en la tabla
insert_query = "INSERT INTO producto (producto_id, nombreProducto) VALUES (%s, %s)"

for index, row in df.iterrows():
    cursor.execute(insert_query, (row['numero'], row['nombre']))

# Guardar los cambios
connection.commit()

# Cerrar el cursor y la conexión
cursor.close()
connection.close()

print("Datos insertados exitosamente.")
