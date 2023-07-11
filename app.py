from flask import Flask, redirect, request, url_for, render_template, session, json,jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.exc import SQLAlchemyError
import hashlib
from datetime import datetime

#dirección servidor frontend
baseurl='http://127.0.0.1:5500/'

#dirección servidor backend
urlback='http://127.0.0.1:5000/'


app = Flask(__name__,template_folder='template', static_url_path='/static')

app.secret_key="EGTD@do2289"
#configuración para la conexión a la base de datos
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost:3306/amalfi'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

#crear la instancia de la clase SQLAlchemy
db = SQLAlchemy(app)

#crear la instancia de la clase Marshmallow

ma = Marshmallow(app)

#permite cualquier orígen
CORS(app)

#defino los modelos

#modelo de exursiones
class Excursiones(db.Model):
     id = db.Column(db.Integer,nullable=False, primary_key=True)
     salida = db.Column(db.String(30),nullable=False)
     destino = db.Column(db.String(30),nullable=False)
     fechaSalida = db.Column(db.DateTime,nullable=False)
     fechaLlegada = db.Column(db.DateTime,nullable=False)
     precio = db.Column(db.Float,nullable=False)
     cupo = db.Column(db.Integer, nullable=False)
     reservas = db.Column(db.Integer, nullable=False)
     completo = db.Column(db.Boolean, nullable=False)

     def __init__(self, salida,destino,fechaSalida,fechaLlegada,precio,cupo,reservas,completo):

          self.salida=salida
          self.destino=destino
          self.fechaSalida=fechaSalida
          self.fechaLlegada=fechaLlegada
          self.precio=precio
          self.cupo=cupo
          self.reservas=reservas
          self.completo=completo

class ExcSchema(ma.Schema):
     class Meta:
          fields=('id','salida','destino','fechaSalida','fechaLlegada','precio','cupo','reservas','completo')

exc_schema = ExcSchema()
excs_schema = ExcSchema(many=True)


#modelo de ususario
class Usuarios(db.Model):
     id =db.Column(db.Integer, nullable=False, primary_key=True)
     firstname =db.Column(db.String(80), nullable=False)
     lastname =db.Column(db.String(80), nullable=False)
     age =db.Column( db.Integer, nullable=False)
     idNumber =db.Column(db.String(80), nullable=False)
     mail =db.Column(db.String(80),unique=True, nullable=False)
     clave =db.Column(db.String(80), nullable=False)
     fechaIngreso = db.Column(db.DateTime, nullable=False)
     role = db.Column(db.String(10), nullable=False)

     def __init__(self, firstname, lastname,age ,idNumber,mail,clave,fechaIngreso,role):
          self.firstname=firstname
          self.lastname=lastname
          self.age=age
          self.idNumber=idNumber
          self.mail=mail
          self.clave=clave
          self.fechaIngreso=fechaIngreso
          self.role=role

class UserSchema(ma.Schema):
     class Meta:
          fields=('id','firstname','lastname','age','idNumber','mail','clave','fechaIngreso','role')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

#modelo de reserva

class Reservas(db.Model):
      
     idReserva = db.Column(db.Integer, nullable=False, primary_key=True)
     idUsuario = db.Column(db.Integer, db.ForeignKey(Usuarios.id))
     idExcursion = db.Column(db.Integer, db.ForeignKey(Excursiones.id))
     adelanto = db.Column(db.Float, nullable=False)
     pagado = db.Column(db.Boolean, nullable=False)
     
     usuario=db.relationship('Usuarios',backref=db.backref('reservas',lazy=True))
     excursion=db.relationship('Excursiones', backref=db.backref('reservas_excursion', lazy=True))

     def __init__(self, idReserva, idUsuario,idExcursion,adelanto,pagado):
           self.idReserva = idReserva
           self.idUsuario = idUsuario
           self.idExcursion = idExcursion
           self.adelanto = adelanto
           self.pagado = pagado

class ReservaSchema(ma.Schema):
      class Meta:
            fields=('idReserva','idUsuario','idExcursion','adelanto','pagado')

reserva_schema = ReservaSchema()
reservas_schema = ReservaSchema(many=True)


@app.route('/getusuarios', methods=['GET'])
def index():

     usuarios = Usuarios.query.all()
     users=users_schema.dump(usuarios)
     return jsonify(users)


'''*************************************************************************************************************************************************************************************   
**************************************************************************************************************************************************************************************
*
*                                                       FUNCIONES PARA EL LOGIN
*
**************************************************************************************************************************************************************************************
**************************************************************************************************************************************************************************************'''

@app.route('/login', methods=['POST'])
def login():
    #verifica que el método sea POST
    if request.method == 'POST':
        data=request.json
        username=data.get('username')
        password=data.get('password')
        claveencriptada = hashlib.sha256(password.encode()).hexdigest()
        
        claveusuario = Usuarios.query.filter_by(mail=username).with_entities(Usuarios.clave).first()
        resultado=user_schema.dump(claveusuario)
        
        if resultado:
          if resultado['clave']== claveencriptada:
               usuario=Usuarios.query.filter_by(mail=username).first()
               user=user_schema.dump(usuario)

#carga los datos del usuario en la session

               session['id']=user['id']
               session['name']=user['firstname']
               session['lastname']=user['lastname']
               session['age']=user['age']
               session['idNumber']=user['idNumber']
               session['mail']=user['mail']
               session['role']=user['role']
               session['fechaIngreso']=user['fechaIngreso']

               consultareserva=Reservas.query.filter_by(idReserva=session['id'])
               reservasUsuario=reservas_schema.dump(consultareserva)
               return jsonify(reservasUsuario)
          else:
               return jsonify({"message":"Clave Incorrecta"})
        else:
             return jsonify({"message":"No se encontró el usuario."})

# '''*************************************************************************************************************************************************************************************   
# **************************************************************************************************************************************************************************************
# *
# *                                                       FUNCIONES PARA EL USUARIO
# *
# **************************************************************************************************************************************************************************************
# **************************************************************************************************************************************************************************************'''


# #muestra las excursiones disponibles
@app.route('/excursiones', methods=['GET'])
def excursiones():
        
            excursions= Excursiones.query.all()
            resultados=excs_schema.dump(excursions)
            return jsonify(resultados)



# #registra un nuevo usuario
@app.route('/registro', methods=['POST'])
def registro():    
        if request.method == 'POST':
          usuario = request.json['nombre']
          apellido = request.json['apellido']
          edad = request.json['edad']
          mail = request.json['correo']
          documento = request.json['documento']
          clave = request.json['password']
          role='user'
          #encripta la clave recibida desde el formulario html para que no se registre en la base de datos en una forma legible
          claveencriptada = hashlib.sha256(clave.encode()).hexdigest()

          verificacion=Usuarios.query.filter_by(mail=mail).first()
          if verificacion:
               return jsonify({"message":"El usuario ya existe"})
          else:
               fecha=datetime.utcnow()
               nuevo_usuario=Usuarios(firstname=usuario,lastname=apellido,age=edad,mail=mail,idNumber=documento,clave=claveencriptada,role=role,fechaIngreso=fecha)
               db.session.add(nuevo_usuario)
               db.session.commit()
               return user_schema.dump(nuevo_usuario)        


# '''*************************************************************************************************************************************************************************************   
# **************************************************************************************************************************************************************************************
# *
# *                                                       FUNCIONES PARA EL ADMINISTRADOR
# *
# **************************************************************************************************************************************************************************************
# **************************************************************************************************************************************************************************************'''        


# @app.route('/paneladmin')
# def administrador():
#         #verifica si existe la session
#         if len(session)==0:
#                 #si no existe, redirige el navegador a la página principal
#                 return redirect(baseurl)
#         else:
#             return(render_template('/html/administrador.html',htmladmin=session['resultado']))
        


        

# #MUESTRA TODOS LOS USUARIOS EXISTENTES
@app.route('/adminusuarios')
def adminusuarios():
     if len(session)==0 or session['role']!='admin':
          #return redirect(baseurl)
          return jsonify({"message":"No tiene permisos"})
     else:
          usuarios=Usuarios.query.all()
          resultados=users_schema.dump(usuarios)
          return jsonify(resultados)
     
@app.route('/reservasUsuario', methods=['GET'])
def reservasUsuario():
     id=request.args.get('id')
     reservasUsuario=Reservas.query.filter_by(idUsuario=id)
     resultados=reservas_schema.dump(reservasUsuario)
     return jsonify(resultados)
     
# #ELIMINA EL USUARIO SELECCIONADO
@app.route('/bajaUsuario/<int:id>', methods=['DELETE'])
def eliminarUsuario(id):

     idUsuario=request.args.get('id')
     consulta=Reservas.query.filter_by(idUsuario=idUsuario).all()
     resultados=reservas_schema.dump(consulta)
     if resultados is None:
          return None
     else:
          for resultado in resultados:
               db.session.delete(resultado)
          db.session.commit()
          
     try:
          usuario=Usuarios.query.get(id)
          if usuario is None:
               return jsonify({"message":"El usuario no existe."}),404
          db.session.delete(usuario)
          db.session.commit()
          return jsonify({"message":"El usuario ha sido eliminado con éxito."})
     except SQLAlchemyError as e:
          db.session.rollback()
          return jsonify({"message":"No se pudo eliminar"})

     
# #Blanquea la clave del usuario seleccionado
# @app.route('/blanquearclave',methods=['POST'])
# def blanquearClave():
#      if request.method=='POST':
#           idUsuario=int(request.form.get('id'))
#           sentencia='select idNumber from usuarios where id=%s'
#           modificacion='update usuarios set clave=(sha2(%s,256)) where id=%s'
#           conn=mysql.connect()
#           cursor=conn.cursor()
#           cursor.execute(sentencia,idUsuario)
#           conn.commit()
#           clave=cursor.fetchone()
#           cursor.execute(modificacion,(clave,idUsuario))
#           conn.commit()
#           if cursor.rowcount>0:
#                cursor.close()
#                conn.close()
#                return jsonify({'clave':clave})
#           else:
#                cursor.close()
#                conn.close()
#                return jsonify({})


# '''*************************************************************************************************************************************************************************************   
# **************************************************************************************************************************************************************************************
# *
# *                                                 FUNCIONES PARA EL ADMINISTRADOR REFERIDAS A LAS EXCURSIONES
# *
# **************************************************************************************************************************************************************************************
# **************************************************************************************************************************************************************************************'''



# #ELIMINA LA EXCURSIÓN SELECCIONADA
# @app.route('/bajaExcursion', methods=['POST'])
# def eliminarExcursion():
#      if session['role']!='admin':
#           return 'No tiene autorización para realizar esta operación'
#      else:
#         if request.method=='POST':
#             idExcursion=int(request.form.get('id'))
#             sentencia="delete from excursiones where id = %s"
#             conn=mysql.connect()
#             cursor=conn.cursor()

#             #eliminación de las reservas
#             verificacion="select * from reservas where idExcursion = %s"
#             cursor.execute(verificacion,(idExcursion))
#             reservas=cursor.fetchall()
#             try:
#                 #eliminar las reservas
#                 if reservas:
#                         cursor.execute('delete from reservas where idExcursion = %s')
#                         conn.commit()
#                     #eliminar la excursión
#                 cursor.execute(sentencia,idExcursion)
#                 conn.commit()
#                 if cursor.rowcount!=0:
#                         cursor.close()
#                         return 'Excursión Eliminada'
#                 else:
#                         cursor.close()
#                         return 'No se puedo eliminar'
#             except Exception as e:
#                 conn.rollback()
#                 cursor.close()
#                 return 'Ocurrió un error: '+str(e)
#             finally:
#                 conn.close()


# #CREA UNA NUEVA EXCURSIÓN
# @app.route('/altaExcursion',methods=['POST'])
# def altaExcursion():
#       if session['role']!='admin':
#           return 'No tiene autorización para realizar esta operación'
#       else:
#         if request.method=='POST':
#             datos_excursion = request.get_json()
#             salida = datos_excursion['salida']
#             destino = datos_excursion['destino']
#             fecha_salida = datos_excursion['fechaSalida']
#             fecha_llegada = datos_excursion['fechaLlegada']
#             precio = datos_excursion['precio']
#             cupo = datos_excursion['cupo']
#             reservas = datos_excursion['reservas']
#             completo = datos_excursion['completo']
            
#             sentencia="insert into excursiones (salida,destino,fechaSalida,fechaLlegada,precio,cupo,reservas,completo) values (%s,%s,%s,%s,%s,%s,%s,%s);"
#             conn=mysql.connect()
#             cursor=conn.cursor()
#             cursor.execute(sentencia,(salida,destino,fecha_salida,fecha_llegada,precio,cupo,reservas,completo))
#             conn.commit()
#             if cursor.rowcount!=0:
#                  conn.close()
#                  cursor.close()
#                  return 'Excursión añadida con éxito.'
#             else:
#                  conn.close()
#                  cursor.close()
#                  return 'Algo salió mal.'

# #MODIFICA LA EXCURSIÓN SELECCIONADA
# @app.route('/modificarExcursion', methods=['POST'])
# def modificarExcursion():
#      if session['role']!='admin':
#           return 'No tiene autorización para realizar esta operación'
#      else:
#           if request.method=='POST':
#                datos_excursion=request.get_json()
#                id=datos_excursion['id']
#                salida=datos_excursion['salida']
#                destino=datos_excursion['destino']
#                fecha_salida = datos_excursion['fechaSalida']
#                fecha_llegada = datos_excursion['fechaLlegada']
#                precio = datos_excursion['precio']
#                cupo = datos_excursion['cupo']
#                reservas = datos_excursion['reservas']
#                completo = datos_excursion['completo']
#                sentencia="update excursiones set salida = %s, destino=%s, fechaSalida=%s, fechaLlegada=%s, precio=%s, cupo=%s,reservas=%s, completo=%s where id=%s;"
#                conn=mysql.connect()
#                cursor=conn.cursor()
#                cursor.execute(sentencia,(salida,destino,fecha_salida,fecha_llegada,precio,cupo,reservas,completo,id))
#                conn.commit()
#                if cursor.rowcount!=0:
#                     conn.close()
#                     cursor.close()
#                     return 'Modificación realizada.'
#                else:
#                     conn.close()
#                     cursor.close()
#                     return 'Algo salió mal'
               

# @app.route('/adminreservas', methods=['GET'])
# def getadminReservas():
#      conn=mysql.connect()
#      cursor=conn.cursor()
#      sentencia='select idReserva, idUsuario, idExcursion, adelanto, cantidad, pagado,firstname, lastname from reservas join usuarios where reservas.idUsuario=usuarios.id ;'
#      cursor.execute(sentencia)
#      reservas=cursor.fetchall()
#      return jsonify(reservas)
               


               
# @app.route('/panelusuario')
# def usuario():
#      #trae los datos del usuario desde la página de login
#      usuario=session.get('resultado')
#      iduser=usuario[0]
#      conn=mysql.connect()
#      cursor=conn.cursor()
#      #busca en la base de datos la reserva del usuario según su id
#      sentencia='select salida,destino, fechaSalida, fechaLlegada,precio,adelanto,cantidad from reservas join excursiones on reservas.idExcursion=excursiones.id where reservas.idUsuario=%s;'
#      cursor.execute(sentencia,iduser)
#      reservas=cursor.fetchall()
#      #busca todas las escursiones disponibles
#      cursor.execute('select * from excursiones')
#      excursiones=cursor.fetchall()
#      cursor.close()
#      conn.close()

#      return render_template('html/usuario.html',htmlusuario=usuario,htmlreservas=reservas,htmlexcursiones=excursiones)


@app.route('/reservas', methods=['GET'])
def getReservas():
     # usuario=session.get('resultado')
     # idUser=usuario[0]
     reservas = Reservas.query.all()
     resultados= reservas_schema.dump(reservas)
     return jsonify(resultados)


# @app.route('/reservar',methods=['GET','POST'])
# def reservar():
#      usuario=session['resultado']
#      conn=mysql.connect()
#      cursor=conn.cursor()
#      sentencia='insert into reservas (idUsuario,idExcursion,adelanto,pagado,cantidad) values (%s,%s,%s,0,%s);'
#      if request.method=='POST':
#           excursiondId=int(request.form.get('index'))
#           cantidad=int(request.form.get('lugares'))
#           adelanto=float(request.form.get('anticipo'))
#           cursor.execute(sentencia,(usuario[0],excursiondId,adelanto,cantidad))
#           if cursor.rowcount>0:
#             conn.commit()
#             conn.close()
#             cursor.close()
#             response={'mensaje':'El usuario hizo una reserva',
#                         'lugares':cantidad,
#                         'excursion':excursiondId}
#             return jsonify(response)
#           else:
#                conn.rollback()
#                conn.close()
#                cursor.close()
#                return 'Algo salió mal. Intente nuevamente'
#      return render_template('html/reservar.html',htmlresultado=usuario[0])



# @app.route('/logout')
# def logout():
#      session.clear()
#      return redirect(baseurl)


if __name__=='__main__':
    app.run(debug=True)