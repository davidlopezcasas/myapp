from flask import Flask, render_template, request, redirect, url_for, flash, make_response, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
import pymysql
from weasyprint import HTML, CSS
import io
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'tu_secreto_aqui'
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=1)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

users = {
    1: User(1, 'SOCO', generate_password_hash('1983S')),
    2: User(2, 'FRAN', generate_password_hash('1983F'))
}

@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        for user in users.values():
            if user.username == username and check_password_hash(user.password, password):
                login_user(user, remember=True)
                return redirect(url_for('index'))
        flash('Nombre de usuario o contraseña incorrectos')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


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
@login_required
def index():
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM albaran a JOIN cliente c ON a.cliente_id = c.cliente_id ORDER BY a.albaran_id DESC")
        albaranes = cursor.fetchall()
    connection.close()
    return render_template('index.html', albaranes=albaranes)

@app.route('/gastos')
@login_required
def ver_gastos():
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM gasto g ORDER BY g.fecha DESC")
        gastos = cursor.fetchall()
    connection.close()
    return render_template('ver_gastos.html', gastos=gastos)

@app.route('/get_costes/<int:albaran_id>', methods=['GET'])
@login_required
def get_costes(albaran_id):
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT preciotransporte, kilostransporte FROM albaran WHERE albaran_id = %s", (albaran_id,))
        costes = cursor.fetchone()
    connection.close()
    return jsonify(costes)


@app.route('/costes/<int:albaran_id>', methods=['POST'])
@login_required
def guardar_costes(albaran_id):
    data = request.get_json()
    connection = get_db_connection()
    precio_transporte = data['precio_transporte']
    kilos_transporte = data['kilos_transporte']

    with connection.cursor() as cursor:
        cursor.execute("UPDATE albaran SET preciotransporte = %s, kilostransporte = %s WHERE albaran_id = %s",
                       (precio_transporte, kilos_transporte, albaran_id))
        connection.commit()

    connection.close()
    return jsonify(success=True)


@app.route('/albaran/<int:albaran_id>')
@login_required
def view_albaran(albaran_id):
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM albaran WHERE albaran_id = %s", (albaran_id,))
        albaran = cursor.fetchone()

        # Obtener el siguiente albarán
        cursor.execute("SELECT albaran_id FROM albaran WHERE albaran_id > %s ORDER BY albaran_id ASC LIMIT 1",
                       (albaran_id,))
        next_albaran = cursor.fetchone()
        albaran_next_id = next_albaran['albaran_id'] if next_albaran else None

        cursor.execute("SELECT albaran_id FROM albaran WHERE albaran_id < %s ORDER BY albaran_id DESC LIMIT 1",
                       (albaran_id,))
        previous_albaran = cursor.fetchone()
        albaran_previous_id = previous_albaran['albaran_id'] if previous_albaran else None

        cursor.execute("SELECT * FROM cliente WHERE cliente_id = %s", (albaran['cliente_id'],))
        cliente = cursor.fetchone()

        cursor.execute("SELECT * FROM lineas_producto WHERE albaran_id = %s", (albaran_id,))
        lineas_producto = cursor.fetchall()

        for linea in lineas_producto:
            cursor.execute(
                "SELECT * FROM etiqueta WHERE etiqueta_id IN (SELECT etiqueta_id FROM linea_producto_etiqueta WHERE albaran_id = %s AND linea_id = %s)",
                (albaran_id, linea['linea_id']))
            etiquetas = cursor.fetchall()

            for etiqueta in etiquetas:
                if 'kilos' in etiqueta:
                    etiqueta['kilos'] = etiqueta['kilos'].split()

            linea['etiquetas'] = etiquetas

    connection.close()
    return render_template('view_albaran.html', albaran=albaran, cliente=cliente, lineas_producto=lineas_producto,
                           albaran_next_id=albaran_next_id, albaran_previous_id=albaran_previous_id)


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_albaran():
    connection = get_db_connection()
    if request.method == 'POST':
        albaran_id = request.form['albaran_id']
        cliente_id = request.form['cliente_id']
        portestotales = request.form['portestotales']
        fecha = request.form['fecha']

        try:
            with connection.cursor() as cursor:
                # Insertar albarán
                cursor.execute(
                    "INSERT INTO albaran (albaran_id, cliente_id, portestotales, fecha) VALUES (%s, %s, %s, %s)",
                    (albaran_id, cliente_id, portestotales, fecha)
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
                arte = request.form.getlist('tipoarte[]')
                zona = request.form.getlist('tipozona[]')
                lote = request.form.getlist('lote[]')
                barco = request.form.getlist('barco[]')
                obs = request.form.getlist('obs[]')

                for i in range(len(nombreproducto)):
                    linea_id = i + 1  # Suponiendo que cada nueva línea se asigna de manera secuencial
                    cursor.execute(
                        """INSERT INTO lineas_producto (albaran_id, linea_id, nombreproducto, intervalopesos, descripcion, 
                        numerocajas, tipocaja, kilos, precio, preciocompra, porteskg, beneficiokg, lote, zona, arte, barco, obs) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (albaran_id, linea_id, nombreproducto[i], intervalopesos[i], descripcion[i],
                         numerocajas[i], tipocaja[i], kilos[i], precio[i], preciocompra[i], porteskg[i], beneficiokg[i], lote[i], zona[i], arte[i], barco[i], obs[i])
                    )

                    # Insertar etiquetas asociadas a cada línea de producto
                    etiqueta_kilos = str(request.form.get(f'etiqueta_kilos_{i}'))
                    print(f"Valor de etiqueta_kilos: {etiqueta_kilos}")
                    qretiqueta = request.form.getlist(f'qretiqueta_{i}[]')
                    qretiquetacompra = request.form.getlist(f'qretiquetacompra_{i}[]')

                    for j in range(len(qretiqueta)):
                        cursor.execute(
                            "INSERT INTO etiqueta (kilos, qretiqueta, qretiquetacompra) VALUES (%s, %s, %s)",
                            (etiqueta_kilos, qretiqueta[j], qretiquetacompra[j])
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
        cursor.execute("SELECT * FROM zona")
        tipos_zona = cursor.fetchall()
        cursor.execute("SELECT * FROM arte")
        tipos_arte = cursor.fetchall()
        cursor.execute("SELECT * FROM tipocaja")
        tipos_caja = cursor.fetchall()
    connection.close()
    return render_template('create_albaran.html', clientes=clientes, productos=productos, descripciones=descripciones,
                           tipos_caja=tipos_caja, tipos_zona=tipos_zona, tipos_arte=tipos_arte)


@app.route('/creategasto', methods=['GET', 'POST'])
@login_required
def create_gasto():
    connection = get_db_connection()
    if request.method == 'POST':
        nombreempresa = request.form['nombreempresa']
        importe_aux = (request.form['importe']).replace(",", ".")
        importe = float(importe_aux)
        fecha = request.form['fecha']

        try:
            with connection.cursor() as cursor:
                # Insertar albarán
                cursor.execute(
                    "INSERT INTO gasto (nombreempresa, importe, fecha, pagado) VALUES (%s, %s, %s, 0)",
                    (nombreempresa, importe, fecha)
                )
            connection.commit()
        finally:
            connection.close()
        return redirect(url_for('ver_gastos'))

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM empresasgastos")
        gastos = cursor.fetchall()
    connection.close()
    return render_template('create_gasto.html', gastos=gastos)


@app.route('/edit/<int:albaran_id>', methods=['GET', 'POST'])
@login_required
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
                arte = request.form.getlist('tipoarte[]')
                zona = request.form.getlist('tipozona[]')
                lote = request.form.getlist('lote[]')
                barco = request.form.getlist('barco[]')
                obs = request.form.getlist('obs[]')


                for i in range(len(nombreproducto)):
                    linea_id = i + 1
                    cursor.execute(
                        """INSERT INTO lineas_producto (albaran_id, linea_id, nombreproducto, intervalopesos, descripcion, 
                        numerocajas, tipocaja, kilos, precio, preciocompra, porteskg, beneficiokg, lote, zona, arte, barco, obs) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (albaran_id, linea_id, nombreproducto[i], intervalopesos[i], descripcion[i],
                         numerocajas[i], tipocaja[i], kilos[i], precio[i], preciocompra[i], porteskg[i], beneficiokg[i], lote[i], zona[i], arte[i], barco[i], obs[i])
                    )

                    # Insertar etiquetas asociadas a cada línea de producto
                    etiqueta_kilos = request.form.getlist(f'etiqueta_kilos_{i}[]')
                    print(etiqueta_kilos)
                    qretiqueta = request.form.getlist(f'qretiqueta_{i}[]')
                    print(qretiqueta)
                    qretiquetacompra = request.form.getlist(f'qretiquetacompra_{i}[]')
                    print(qretiqueta)

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
        cursor.execute("SELECT * FROM zona")
        tipos_zona = cursor.fetchall()
        cursor.execute("SELECT * FROM arte")
        tipos_arte = cursor.fetchall()
        cursor.execute("SELECT * FROM descripcion")
        descripciones = cursor.fetchall()
        cursor.execute("SELECT * FROM tipocaja")
        tipos_caja = cursor.fetchall()
    connection.close()
    return render_template('edit_albaran.html', albaran=albaran, clientes=clientes, lineas_producto=lineas_producto,
                           etiquetas=etiquetas, productos=productos, descripciones=descripciones, tipos_caja=tipos_caja, tipos_zona=tipos_zona, tipos_arte=tipos_arte)


@app.route('/delete/<int:albaran_id>')
@login_required
def delete_albaran(albaran_id):
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM albaran WHERE albaran_id = %s", (albaran_id,))
    connection.commit()
    connection.close()
    return redirect(url_for('index'))

@app.route('/albaran/pdf/<int:albaran_id>', methods=['GET'])
@login_required
def pdf_albaran_view(albaran_id):
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM albaran WHERE albaran_id = %s", (albaran_id,))
        albaran = cursor.fetchone()

        cursor.execute("SELECT * FROM cliente WHERE cliente_id = %s", (albaran['cliente_id'],))
        cliente = cursor.fetchone()

        cursor.execute("SELECT * FROM lineas_producto lp JOIN producto p ON p.nombreproducto = lp.nombreproducto WHERE albaran_id = %s", (albaran_id,))
        lineas_producto = cursor.fetchall()

        for linea in lineas_producto:
            cursor.execute(
                "SELECT * FROM etiqueta WHERE etiqueta_id IN (SELECT etiqueta_id FROM linea_producto_etiqueta WHERE albaran_id = %s AND linea_id = %s)",
                (albaran_id, linea['linea_id']))
            etiquetas = cursor.fetchall()
            linea['etiquetas'] = etiquetas

            linea['numerocajas'] = int(linea['numerocajas'])
            linea['kilos'] = float(linea['kilos'])

    connection.close()
    html = render_template('pdf_albaran.html', albaran=albaran, cliente=cliente, lineas_producto=lineas_producto)

    # Generar PDF en memoria
    pdf_file = io.BytesIO()
    HTML(string=html).write_pdf(pdf_file, stylesheets=[CSS(string='body { font-family: Arial, sans-serif; } table { width: 100%; border-collapse: collapse; margin-bottom: 20px; } th, td { border: 1px solid #000; padding: 8px; text-align: left; } th { background-color: #f2f2f2; }')])
    pdf_file.seek(0)

    # Devolver el PDF como una respuesta para ser visualizado en una nueva pestaña
    response = make_response(pdf_file.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=albaran_{albaran_id}.pdf'

    return response


@app.route('/upload_pdf/<int:albaran_id>', methods=['POST'])
@login_required
def upload_pdf(albaran_id):
    if 'pdf_file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['pdf_file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file and file.filename.endswith('.pdf'):
        pdf_data = file.read()
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE albaran SET pdfventa = %s WHERE albaran_id = %s", (pdf_data, albaran_id))
                connection.commit()
        finally:
            connection.close()
        flash('PDF uploaded successfully')
        return redirect(url_for('index'))
    else:
        flash('Invalid file format')
        return redirect(request.url)


@app.route('/view_pdf/<int:albaran_id>', methods=['GET'])
@login_required
def view_pdf(albaran_id):
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT pdfventa FROM albaran WHERE albaran_id = %s", (albaran_id,))
        result = cursor.fetchone()
    connection.close()

    if result and result['pdfventa']:
        response = make_response(result['pdfventa'])
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=albaran_{}.pdf'.format(albaran_id)
        return response
    else:
        flash('No PDF file found')
        return redirect(url_for('index'))


@app.route('/fk_factura/<int:albaran_id>/cliente/<int:cliente_id>', methods=['POST'])
@login_required
def update_factura_and_cliente(albaran_id, cliente_id):
    data = request.get_json()
    connection = get_db_connection()
    factura_id = data['factura_id']

    try:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE albaran SET factura_id = %s WHERE albaran_id = %s",
                           (factura_id, albaran_id))
            cursor.execute("UPDATE factura SET cliente_id = %s WHERE factura_id = %s",
                           (cliente_id, factura_id))
            connection.commit()
    except Exception as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

    return jsonify(success=True)


@app.route('/view_factura/<int:albaran_id>', methods=['GET'])
@login_required
def view_factura(albaran_id):
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT pdffactura FROM albaran a JOIN factura f ON a.factura_id = f.factura_id WHERE albaran_id = %s", (albaran_id,))
        result = cursor.fetchone()
    connection.close()

    if result and result['pdffactura']:
        response = make_response(result['pdffactura'])
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=albaran_{}.pdf'.format(albaran_id)
        return response
    else:
        flash('No PDF file found')
        return redirect(url_for('index'))

@app.route('/view_factura_factura/<int:factura_id>', methods=['GET'])
@login_required
def view_factura_factura(factura_id):
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT pdffactura FROM factura f WHERE factura_id = %s", (factura_id,))
        result = cursor.fetchone()
    connection.close()

    if result and result['pdffactura']:
        response = make_response(result['pdffactura'])
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=factura_{}.pdf'.format(factura_id)
        return response
    else:
        flash('No PDF file found')
        return redirect(url_for('index'))


@app.route('/facturas')
@login_required
def ver_facturas():
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM factura f JOIN cliente c ON f.cliente_id = c.cliente_id ORDER BY f.factura_id DESC")
        facturas = cursor.fetchall()
    connection.close()
    return render_template('ver_facturas.html', facturas=facturas)


@app.route('/toggle_pagada/<int:factura_id>', methods=['POST'])
@login_required
def toggle_pagada(factura_id):
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT pagada FROM factura WHERE factura_id = %s", (factura_id,))
        result = cursor.fetchone()

        if result:
            new_status = not result['pagada']
            cursor.execute("UPDATE factura SET pagada = %s WHERE factura_id = %s", (new_status, factura_id))
            connection.commit()
            flash('Estado de pago actualizado correctamente.')
        else:
            flash('Factura no encontrada.')

    connection.close()
    return redirect(url_for('ver_facturas'))

@app.route('/toggle_pagado/<int:gasto_id>', methods=['POST'])
@login_required
def toggle_pagado(gasto_id):
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT pagado FROM gasto WHERE gasto_id = %s", (gasto_id,))
        result = cursor.fetchone()

        if result:
            new_status = not result['pagado']
            cursor.execute("UPDATE gasto SET pagado = %s WHERE gasto_id = %s", (new_status, gasto_id))
            connection.commit()
            flash('Estado de pago actualizado correctamente.')
        else:
            flash('Gasto no encontrado.')

    connection.close()
    return redirect(url_for('ver_gastos'))





if __name__ == '__main__':
    app.run(debug=True)
