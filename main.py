#se agrego flask
from flask import Flask, render_template, send_file, request,redirect, url_for, session, send_from_directory, Markup
import sqlite3
import datetime as dt
#se importa extensión Flask Mail
from flask_mail import Mail, Message
#se importa libreria para trabajar con codigo QR
import qrcode
#Se importa con lo que se trabajara la conversion de pdf a html
from flask_weasyprint import HTML, render_pdf
from flask import flash

#Se usa la libreria para reCAPTCHA. La idea es utilizar la Api de Google para impedir  el tráfico procedente de programas automatizados o bots, implementando asi mayor seguridad al sitio web.
from flask_recaptcha import ReCaptcha


app = Flask('app')

#se define variable a trabar en las funciones posteriores para captcha
recaptcha = ReCaptcha(app=app)
#Se habilita con las credenciales que se obtienen de la API en el cloudDeveloper de GOOGLE, se almacenan estos datos con un diccionario 
app.config.update(dict(
    RECAPTCHA_ENABLED = True,
    RECAPTCHA_SITE_KEY = "6LcqoAobAAAAACK7zdA1d34xcp5JofU03rwkwkxc",
    RECAPTCHA_SECRET_KEY = "6LcqoAobAAAAAJk5Sps8ljZpZIPdr3soDcNQZyG0",
))
#se inicializa el objeto una vez creado
recaptcha = ReCaptcha()
recaptcha.init_app(app)


app.secret_key = "hola123"
#SMTP permite enviar correos, en este caso se usan los ajustes de GMAIL
app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config['MAIL_PORT'] = 587
#protocolo TLS es de encriptado de datos servidor-usuario, de acuerdo al protocolo es asignado el numero de puerto
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
#Nombre de usuario del servidor smtp
app.config['MAIL_USERNAME'] = mail_username="elproyectowhy@gmail.com"
#Contraseña del usuario del servidor smtp
app.config['MAIL_PASSWORD'] = mail_password="hola123@"
#Se crea un default sender, para que todos los correos salgan del mismo correo
app.config['MAIL_DEFAULT_SENDER'] = "elproyectowhy@gmail.com"
#se define la variable mail, la cual se usa una vez definida la ruta 
mail=Mail(app)

app.secret_key = "hola123"

try:
  #conexión de la base de datos
  con = sqlite3.connect('database.db')
  #Creacion del cursor de la base de datos
  c= con.cursor() 
  #Se crea la tabla de usuarios   
  c.execute('CREATE TABLE IF NOT EXISTS users(nombre TEXT NOT NULL, apellido TEXT, email TEXT NOT NULL, password TEXT NOT NULL)')
  #Tabla de historia medica
  c.execute('CREATE TABLE IF NOT EXISTS medical(email TEXT, nombre TEXT NOT NULL, apellidos TEXT NOT NULL , documento INTEGER, edad TEXT, nacimiento TEXT, eps INTEGER,sangre TEXT, sexo TEXT , contacto TEXT NOT NULL, enfermedad TEXT, medicamento TEXT, alergia TEXT, habitos TEXT, adicional TEXT )')
  #Tabla de foro
  c.execute('CREATE TABLE IF NOT EXISTS foro(titulo TEXT NOT NULL, texto TEXT, nombre TEXT, fecha timestamp )')
  #Tabla del calendario
  c.execute('CREATE TABLE IF NOT EXISTS eventos(titulo TEXT, fecha TEXT, email TEXT, comentario TEXT)')
  con.commit()
  c.close()


  
except sqlite3.Error as error:

    print(error)
finally:

    con.close()
    

#creación de rutas
@app.route('/')
def index():
  if  "email" not in session:
    #se crea un markup, para agregar un link en el mensaje que se flashea
    flash(Markup('No ha iniciado sesión <a href="/login" class="alert-link">INICIE SESION</a>'))
  return render_template ("index.html")


@app.route('/about')
def about():
  if  "email" not in session:
    #se crea un markup, para agregar un link en el mensaje que se flashea
    flash(Markup('No ha iniciado sesión <a href="/login" class="alert-link">INICIE SESION</a>'))
  return render_template("about.html")

@app.route('/login', methods = ('GET', 'POST'))
def login():
  if request.method == 'POST':
    #conexión con la base de datos
    con = sqlite3.connect('database.db')
    #Creacion del cursor
    c = con.cursor()
    email = request.form.get('email')
    session["email"] = email #Se guarda el email en la sesion
    password = request.form.get('password')
    c.execute('SELECT * FROM users WHERE email = ?', (email,))
    data = c.fetchone()
    c.close()
    
    if data:
      passw = data[-1]
      fail_message='contraseña incorrecta o no llenó el reCaptcha, intentelo de nuevo'
      if passw == password and recaptcha.verify():      
        flash(Markup('Sesión iniciada' ))
      else:
        flash(fail_message)
    else:
       flash(Markup('No existe una cuenta con este correo, por favor  <a href="/sign_up" class="alert-link">cree una cuenta</a>'))    
    #if recaptcha.verify() and passw == password :
        #flash('correcto')
        #return redirect(url_for('servicios'))
   
    #else:
        #flash('Error ReCaptcha')
        #return redirect(url_for('login'))
    
    
  return render_template("login.html")

#Ruta para cerrar sesión
@app.route('/log_out')
def log_out():
  if  "email" in session:
    #Cuando se entre a esta página, con el session.pop se borrará el elemento email de la sesión, que fue la unica informacion guardada en el servidor al iniciar sesion.
    session.pop("email")
    return render_template("log_out.html")
  else:
    flash('Para cerrar sesión primero debes de tener sesión iniciada')
    return redirect(url_for('login'))

  

@app.route('/sign_up', methods = ('GET', 'POST'))
def sign_up():
  if request.method == 'POST':
    #conexión con la base de datos
    con = sqlite3.connect('database.db')
    #Creacion del cursor
    c = con.cursor()
    nombre= request.form.get('nombre')
    apellido = request.form.get('apellido')
    email= request.form.get('correo')
    password = request.form.get('password')
    c.execute('SELECT * FROM users WHERE email = ?', (email,))
    data = c.fetchone()
    c.close()
    if data:
      flash ("Ya existe una cuenta con este correo, vuelva a intentarlo")
      return redirect(url_for('sign_up'))
    else:
      c = con.cursor()
      c.execute('INSERT INTO users(nombre, apellido, email, password) VALUES (?,?,?,?)', (nombre, apellido,email, password))
      con.commit()
      c.close()
      flash ("Cuenta creada correctamente, inice sesión")
      return redirect(url_for('login'))
  
  return render_template("sign_up.html")     
''''
@app.route('/password_recovery')
def 
'''
@app.route('/historia_medica', methods = ('GET', 'POST'))
def historia_medica():
  if  "email" in session: #Se verifica que se haya iniciado sesion, para poder acceder a la historia medica
    if request.method == 'POST':
        con = sqlite3.connect('database.db')#base de datos para el alojamiento de archivos de usuario 
        c = con.cursor() #Se crea el cursor
        #Se obtienen los datos recuperados del formulario de sign up
        Nombre=request.form.get('name')
        Apellido=request.form.get('last-name')
        DocumentoIdentidad=request.form.get('ID')
        Edad= request.form.get('edad')
        Fecha = request.form.get('datebirth')
        EPS= request.form.get('EPS')  
        Sexo = request.form.get('sex')
        TipoSangre = request.form.get('sangre')
        ContactoEmergencia= request.form.get('contacto')
        Enfermedad = request.form.get('enfermedad')
        Medicamentos = request.form.get('medicamento')
        Alergias = request.form.get('allergy')
        Habitos = request.form.get('habit')
        Adicional=request.form.get('adicional')
        Email = session['email']
        #Se agregan los datos a la base de datos
        c.execute('INSERT INTO medical(email,nombre, apellidos, documento, edad, nacimiento, eps, sangre, sexo, contacto,enfermedad, medicamento, alergia, habitos, adicional) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', (Email, Nombre, Apellido, DocumentoIdentidad, Edad, Fecha, EPS, TipoSangre, Sexo, ContactoEmergencia, Enfermedad, Medicamentos, Alergias, Habitos,Adicional))
        con.commit()
        c.close()
        
        return redirect(url_for('servicios'))
  else:
    flash('No has iniciado sesion, intentalo de nuevo')
    return redirect(url_for('login'))
      
  return render_template("historia_medica.html")  

@app.route('/servicios')
def servicios():
  if  "email" in session:
    return render_template("servicios.html")
  else:  
    flash('No has iniciado sesion, intentalo de nuevo')
    return redirect(url_for('login'))

#Ruta base del foro
@app.route('/foro')
def foro():
  #conexión base de datos
  con = sqlite3.connect('database.db')
  #Cursor
  c = con.cursor()
  
  #Se seleccionan los elementos de la base de datos
  c.execute('SELECT * FROM  foro')
  posts = c.fetchall()
  c.close()
  
  #posts=posts es para pasar todos los posts
  return render_template("foro.html", posts=posts) 

#Ruta donde se agregan los posts
@app.route('/agregar_entrada')
def agregar_entrada():
  if  "email" in session: #Se verifica que se haya iniciado sesion, para poder acceder a la historia medica
    return render_template("agregar_entrada.html")
  else:
    flash('No has iniciado sesion, intentalo de nuevo')
    return redirect(url_for('login')) 

@app.route('/crear', methods = ('GET', 'POST'))
def crear_post():  
  #conexión base de datos
  con = sqlite3.connect('database.db')
  #Cursor
  c = con.cursor()
  titulo = request.form.get("titulo")
  texto = request.form.get("texto")
  fecha = dt.datetime.now()
  

  c.execute('INSERT INTO foro(titulo, texto, fecha) VALUES(?,?,?)', (titulo, texto, fecha))
  con.commit()
  c.close()
  return  redirect(url_for('foro'))


@app.route('/agenda')
def agenda():
  if  "email" in session: #Se verifica que se haya iniciado sesion, para poder acceder a la agenda
  #conexión base de datos
    con = sqlite3.connect('database.db')
    #Cursor
    c = con.cursor()
    #Se guarda el email de la sesion
    email = session["email"]
    #con el email se filtran los eventos creados desde este mismo correo
    c.execute('SELECT * FROM eventos WHERE  email = ?', (email,))
    #se guardan los eventos de la tabla en una tupla
    events = c.fetchall()
    #Se cierra la base de datos
    c.close()
    return render_template("agenda.html", events=events)  
  else:  
    flash('No has iniciado sesion, intentalo de nuevo')
    return redirect(url_for('login')) 


#ruta para agregar evento
@app.route('/agregar_evento')
def agregar_evento():
  return render_template("agregar_evento.html")

#ruta donde se crean los eventos
@app.route('/crear_evento',  methods = ('GET', 'POST'))
def crear_evento():
  #se verifica que se haya iniciado sesion
  if  "email" in session:
    #conexión base de datos
    con = sqlite3.connect('database.db')
    #Cursor
    c = con.cursor()
    #Se toma el titulo del evento, ingresado en el formulario
    titulo = request.form.get("titulo")
    #se toma la fecha ingresada
    fecha = request.form.get("fecha")
    #se toma el email de la sesion iniciada
    email = session["email"]

    comment = request.form.get("comentario")

    #se guardan los elementos en la tabla de eventos
    c.execute('INSERT INTO eventos(titulo, fecha, email, comentario) VALUES (?,?,?,?)', (titulo, fecha, email, comment))
    con.commit()
    c.close()
    return redirect ('agenda')
  else:  
    flash('No has iniciado sesion, intentalo de nuevo')
    return redirect(url_for('login')) 



  
@app.route('/contact', methods = ('GET', 'POST'))
def contact():
  #se obtienen los datos ingresados con el metodo get
  if request.method == 'POST':
     name1 = request.form.get("name1")
     lastname1 = request.form.get("lastname1")
     email1 = request.form.get("email1")
     message1 = request.form.get("message1")
    #se crea instancia Message se definen nomnre de destinatario correo y cuerpo de mensaje
     msg = Message(
            subject=f"Mail from {name1}", body=f"Name: {name1}\nE-Mail: {email1}\n\n\n\n{message1}", sender=mail_username, recipients=['elproyectowhy@gmail.com'])
    #se llama la variable main y se envia con los ajustes aplicados en msg 
     mail.send(msg)
     return render_template("contact.html", success=True)
  return render_template("contact.html")

#Creacion de la ruta donde se crea el html con la historia medica del usuario
@app.route('/historia_medica.pdf' )
def historia_pdf():
  con = sqlite3.connect('database.db')
  #Cursor
  c = con.cursor()
  #Se guarda el email de la sesion 
  ID = session['ID']
  c.execute('SELECT * FROM medical WHERE  documento = ?', (ID,))
  #se guardan los eventos de la tabla en una tupla
  datos = c.fetchall()
  #Se cierra la base de datos
  c.close()
  #return render_template("pdf_historia.html", data = datos)
  #Se crea el render del html
  html = render_template("pdf_historia.html", data = datos)
  #Se devuelve el 
  return render_pdf(HTML(string=html))
  
@app.route('/Guia')
def Guia():
  return render_template('Instructions.html')  

@app.route('/QR')
def Qrcode():
  if "email " in session:
    #se crean las propiedades del codigo QR, con la clase QRCode
    qr = qrcode.QRCode(
    version = None, #Tamano del codigo qr, en este caso sera automatico
    error_correction = qrcode.constants.ERROR_CORRECT_M, #Se crea el parametro para controlar el error, en este caso se controlaran los errores inferiores al 15%
    box_size = 10, #Este parametro es para controlar cuantos pixeles tiene cada "caja" del qr
    border =4,  #Este parametro controla la cantidad de pixeles que debe de tener el borde del QR
    )
    data = "https://TA04-1.ta04.repl.co/Guia"
    #Se agrega la informacion 
    qr.add_data(data)
    #se crea el qr, se dedebidobe de usar el fit=True, debido en un inicio se dijo que el tamano seria automatico 
    qr.make(fit=True)

    img = qr.make_image()
    f = open("static/output.png", "wb")
    img.save(f)
    f.close()
        
    return render_template("QR.html")
  else:    
    flash( "Para acceder al codigo Qr, debes iniciar sesion")

    return redirect(url_for('login'))
  
  
@app.route('/Ingreso_emergencias', methods = ('GET', 'POST'))
def Ingreso_emergencias():
  if request.method == 'POST':
    #conexión con la base de datos
    con = sqlite3.connect('database.db')
    #Creacion del cursor
    c = con.cursor()
    documento = request.form.get("ID")
    #Se busca el Documento de identidad en la base de datos
    c.execute('SELECT * FROM medical WHERE documento = ?', (documento,))
    data = c.fetchone()
    c.close()
    if data:
      session['ID']= data[3]     
      return redirect(url_for('historia_pdf'))
    else:
      flash("Numero de identificación incorrecto, vuelvalo a intentar")

  return render_template ('Ingreso_emergencia.html')

@app.route('/mapa')
def mapa2():
  return render_template('map2.html')

@app.errorhandler(404)
def error404(error):
    
    return render_template('404.html'), 404



app.run(host='0.0.0.0', port=8080, debug=True)