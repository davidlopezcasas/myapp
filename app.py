from flask import Flask, render_template, request, redirect, url_for
import pymysql

app = Flask(__name__)


def get_db_connection():
    connection = pymysql.connect(
        host='database-1.c3k4aaugutfg.eu-west-3.rds.amazonaws.com',
        user='admin',
        password='poporu2015',
        db='lopezcazas',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection


@app.route('/')
def index():
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM albaran")
        albaranes = cursor.fetchall()
    connection.close()
    return render_template('index.html', albaranes=albaranes)


@app.route('/create', methods=['GET', 'POST'])
def create_albaran():
    connection = get_db_connection()
    if request.method == 'POST':
        albaran_id = request.form['albaran_id']
        cliente_id = request.form['cliente_id']
        portestotales = request.form['portestotales']

        try:
            with connection.cursor() as cursor:
                # Insertar albarán
                cursor.execute(
                    "INSERT INTO albaran (albaran_id, cliente_id, portestotales) VALUES (%s, %s, %s)",
                    (albaran_id, cliente_id, portestotales)
                )

                # Insertar líneas de producto
                nombreproducto = request.form.getlist('nombreproducto[]')
                intervalopesos = request.form.getlist('intervalopesos[]')
                descripcion = request.form.getlist('descripcion[]')
                numerocajas = request.form.getlist('numerocajas[]')
                tipocaja = request.form.getlist('tipocaja[]')
                kilos = request.form.getlist('kilos[]')
                precio = request.form.getlist('precio[]')
                preciocompra = request.form.getlist('preciocompra[]')
                porteskg = request.form.getlist('porteskg[]')
                beneficiokg = request.form.getlist('beneficiokg[]')

                for i in range(len(nombreproducto)):
                    linea_id = i + 1  # Suponiendo que cada nueva línea se asigna de manera secuencial
                    cursor.execute(
                        """INSERT INTO lineas_producto (albaran_id, linea_id, nombreproducto, intervalopesos, descripcion, 
                        numerocajas, tipocaja, kilos, precio, preciocompra, porteskg, beneficiokg) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (albaran_id, linea_id, nombreproducto[i], intervalopesos[i], descripcion[i],
                         numerocajas[i], tipocaja[i], kilos[i], precio[i], preciocompra[i], porteskg[i], beneficiokg[i])
                    )

                    # Insertar etiquetas asociadas a cada línea de producto
                    etiqueta_kilos = request.form.getlist(f'etiqueta_kilos_{i}[]')
                    qretiqueta = request.form.getlist(f'qretiqueta_{i}[]')
                    qretiquetacompra = request.form.getlist(f'qretiquetacompra_{i}[]')

                    for j in range(len(etiqueta_kilos)):
                        cursor.execute(
                            "INSERT INTO etiqueta (kilos, qretiqueta, qretiquetacompra) VALUES (%s, %s, %s)",
                            (etiqueta_kilos[j], qretiqueta[j], qretiquetacompra[j])
                        )
                        etiqueta_id = cursor.lastrowid
                        cursor.execute(
                            "INSERT INTO linea_producto_etiqueta (albaran_id, linea_id, etiqueta_id) VALUES (%s, %s, %s)",
                            (albaran_id, linea_id, etiqueta_id)
                        )

            connection.commit()
        finally:
            connection.close()
        return redirect(url_for('index'))

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM cliente")
        clientes = cursor.fetchall()
        cursor.execute("SELECT * FROM producto")
        productos = cursor.fetchall()
        cursor.execute("SELECT * FROM descripcion")
        descripciones = cursor.fetchall()
        cursor.execute("SELECT * FROM tipocaja")
        tipos_caja = cursor.fetchall()
    connection.close()
    return render_template('create_albaran.html', clientes=clientes, productos=productos, descripciones=descripciones,
                           tipos_caja=tipos_caja)


@app.route('/edit/<int:albaran_id>', methods=['GET', 'POST'])
def edit_albaran(albaran_id):
    connection = get_db_connection()
    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        portestotales = request.form['portestotales']

        try:
            with connection.cursor() as cursor:
                # Actualizar albarán
                cursor.execute(
                    "UPDATE albaran SET cliente_id = %s, portestotales = %s WHERE albaran_id = %s",
                    (cliente_id, portestotales, albaran_id)
                )

                # Actualizar líneas de producto
                cursor.execute("DELETE FROM lineas_producto WHERE albaran_id = %s", (albaran_id,))
                cursor.execute("DELETE FROM linea_producto_etiqueta WHERE albaran_id = %s", (albaran_id,))

                nombreproducto = request.form.getlist('nombreproducto[]')
                intervalopesos = request.form.getlist('intervalopesos[]')
                descripcion = request.form.getlist('descripcion[]')
                numerocajas = request.form.getlist('numerocajas[]')
                tipocaja = request.form.getlist('tipocaja[]')
                kilos = request.form.getlist('kilos[]')
                precio = request.form.getlist('precio[]')
                preciocompra = request.form.getlist('preciocompra[]')
                porteskg = request.form.getlist('porteskg[]')
                beneficiokg = request.form.getlist('beneficiokg[]')

                for i in range(len(nombreproducto)):
                    linea_id = i + 1
                    cursor.execute(
                        """INSERT INTO lineas_producto (albaran_id, linea_id, nombreproducto, intervalopesos, descripcion, 
                        numerocajas, tipocaja, kilos, precio, preciocompra, porteskg, beneficiokg) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (albaran_id, linea_id, nombreproducto[i], intervalopesos[i], descripcion[i],
                         numerocajas[i], tipocaja[i], kilos[i], precio[i], preciocompra[i], porteskg[i], beneficiokg[i])
                    )

                    # Insertar etiquetas asociadas a cada línea de producto
                    etiqueta_kilos = request.form.getlist(f'etiqueta_kilos_{i}[]')
                    qretiqueta = request.form.getlist(f'qretiqueta_{i}[]')
                    qretiquetacompra = request.form.getlist(f'qretiquetacompra_{i}[]')

                    for j in range(len(etiqueta_kilos)):
                        cursor.execute(
                            "INSERT INTO etiqueta (kilos, qretiqueta, qretiquetacompra) VALUES (%s, %s, %s)",
                            (etiqueta_kilos[j], qretiqueta[j], qretiquetacompra[j])
                        )
                        etiqueta_id = cursor.lastrowid
                        cursor.execute(
                            "INSERT INTO linea_producto_etiqueta (albaran_id, linea_id, etiqueta_id) VALUES (%s, %s, %s)",
                            (albaran_id, linea_id, etiqueta_id)
                        )

            connection.commit()
        finally:
            connection.close()
        return redirect(url_for('index'))

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM albaran WHERE albaran_id = %s", (albaran_id,))
        albaran = cursor.fetchone()
        cursor.execute("SELECT * FROM cliente")
        clientes = cursor.fetchall()
        cursor.execute("SELECT * FROM lineas_producto WHERE albaran_id = %s", (albaran_id,))
        lineas_producto = cursor.fetchall()
        cursor.execute(
            "SELECT * FROM linea_producto_etiqueta JOIN etiqueta ON linea_producto_etiqueta.etiqueta_id = etiqueta.etiqueta_id WHERE albaran_id = %s",
            (albaran_id,))
        etiquetas = cursor.fetchall()
        cursor.execute("SELECT * FROM producto")
        productos = cursor.fetchall()
        cursor.execute("SELECT * FROM descripcion")
        descripciones = cursor.fetchall()
        cursor.execute("SELECT * FROM tipocaja")
        tipos_caja = cursor.fetchall()
    connection.close()
    return render_template('edit_albaran.html', albaran=albaran, clientes=clientes, lineas_producto=lineas_producto,
                           etiquetas=etiquetas, productos=productos, descripciones=descripciones, tipos_caja=tipos_caja)


@app.route('/delete/<int:albaran_id>')
def delete_albaran(albaran_id):
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM albaran WHERE albaran_id = %s", (albaran_id,))
    connection.commit()
    connection.close()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
