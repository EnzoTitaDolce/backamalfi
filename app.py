from flask import Flask, redirect, request, url_for, render_template, session, json,jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import and_
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
     cantidad=db.Column(db.Integer, nullable=False)
     
     usuario=db.relationship('Usuarios',backref=db.backref('reservas',lazy=True))
     excursion=db.relationship('Excursiones', backref=db.backref('reservas_excursion', lazy=True))

     def __init__(self, idUsuario,idExcursion,adelanto,pagado,cantidad):
           
           self.idUsuario = idUsuario
           self.idExcursion = idExcursion
           self.adelanto = adelanto
           self.pagado = pagado
           self.cantidad = cantidad

class ReservaSchema(ma.Schema):
      class Meta:
            fields=('idReserva','idUsuario','idExcursion','adelanto','pagado','cantidad')

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
        username=request.form['username']
        password=request.form['password']
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
               if session['role']=='user':
                    consultareserva=Reservas.query.filter_by(idReserva=session['id'])
                    reservasUsuario=reservas_schema.dump(consultareserva)
                    return redirect('/panelusuario')
               else:
                    return redirect('/paneladmin')
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
          usuario = request.form.get('nombre')
          apellido = request.form.get('apellido')
          edad = request.form.get('edad')
          mail = request.form.get('correo')
          documento = request.form.get('documento')
          clave = request.form.get('password')
          role='user'
          #encripta la clave recibida desde el formulario html para que no se registre en la base de datos en una forma legible
          claveencriptada = hashlib.sha256(clave.encode()).hexdigest()

          verificacion=Usuarios.query.filter_by(mail=mail).first()
          if verificacion:
               return jsonify({"message":"El usuario ya existe"})
          else:
               fecha=datetime.utcnow()
               nuevo_usuario=Usuarios(firstname=usuario,lastname=apellido,age=edad,mail=mail,idNumber=documento,clave=claveencriptada,role=role,fechaIngreso=fecha)
               usuario=user_schema.dump(nuevo_usuario)
               db.session.add(nuevo_usuario)
               db.session.commit()
               return "Registro exitoso. Puede iniciar sesión"


# '''*************************************************************************************************************************************************************************************   
# **************************************************************************************************************************************************************************************
# *
# *                                                       FUNCIONES PARA EL ADMINISTRADOR
# *
# **************************************************************************************************************************************************************************************
# **************************************************************************************************************************************************************************************'''        


@app.route('/paneladmin')
def administrador():
        #verifica si existe la session
        if len(session)==0 or session['role']!='admin':
                #si no existe, redirige el navegador a la página principal
                return redirect(baseurl+'index.html')
        else:
            return(render_template('/html/administrador.html',htmladmin=session['name']))
        


        

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
     
#MUESTRA LAS RESERVAS DE UN USUARIO
     
@app.route('/reservasUsuario/<int:id>', methods=['GET'])
def reservasUsuario(id):
     if len(session)!=0 and session['role']=='admin':
          reservasUsuario=Reservas.query.filter_by(idUsuario=id).all()
          resultados=reservas_schema.dump(reservasUsuario)
          if resultados:
               return jsonify(resultados)
          else:
               return jsonify({"message":"El usuario no tiene reservas."})
     else:
          return redirect(baseurl)
     
# #ELIMINA EL USUARIO SELECCIONADO
@app.route('/bajaUsuario/<int:id>', methods=['DELETE'])
def eliminarUsuario(id):
     if len(session)!=0 and session['role']=='admin':
          usuario=Usuarios.query.get(id)
          reservas=Reservas.query.filter_by(idUsuario=id).all()
          if reservas:
               for reserva in reservas:
                    db.session.delete(reserva)
                    db.session.commit()
          
          try:
               if usuario is None:
                    return jsonify({"message":"El usuario no existe."}),404
               db.session.delete(usuario)
               db.session.commit()
               return jsonify({"message":"El usuario ha sido eliminado con éxito."})
          except SQLAlchemyError as e:
               db.session.rollback()
               return jsonify({"message":"No se pudo eliminar"})
     else:
          return redirect(baseurl)
     
#Blanquea la clave del usuario seleccionado
@app.route('/blanquearclave/<int:id>',methods=['PATCH'])
def blanquearClave(id):
     if len(session)!=0 and session['role']=='admin':
          usuario=Usuarios.query.get(id)

          if usuario:
               clave=usuario.idNumber
               claveencriptada=hashlib.sha256(clave.encode()).hexdigest()
               usuario.clave=claveencriptada
          try:
               #fijar los cambios
               db.session.commit()
               return jsonify({"message":f"La nueva clase es: {clave}"})
          except Exception as e:
               db.session.rollback()
               return jsonify({"message":"No se pudo cambiar la clave"})
     else:
          return redirect(baseurl)


# '''*************************************************************************************************************************************************************************************   
# **************************************************************************************************************************************************************************************
# *
# *                                                 FUNCIONES PARA EL ADMINISTRADOR REFERIDAS A LAS EXCURSIONES
# *
# **************************************************************************************************************************************************************************************
# **************************************************************************************************************************************************************************************'''



# #ELIMINA LA EXCURSIÓN SELECCIONADA
@app.route('/bajaExcursion/<int:id>', methods=['DELETE'])
def eliminarExcursion(id):
     if session['role']!='admin' or len(session)==0:
          return 'No tiene autorización para realizar esta operación'
     else:
          reservasExcursion=Reservas.query.filter_by(idExcursion=id).all()
          if reservasExcursion:
               for reserva in reservasExcursion:
                    db.session.delete(reserva)
                    db.session.commit()
          excursion=Excursiones.query.get(id)
          db.session.delete(excursion)
          try:
               db.session.commit()
               return jsonify({"mensaje":"Excursión eliminada con éxito"})
          except Exception as e:
               db.session.rollback()
               return jsonify({"message":"No se pudo eliminar la excursión"})
        


#CREA UNA NUEVA EXCURSIÓN
@app.route('/altaExcursion',methods=['POST'])
def altaExcursion():
      if session['role']!='admin' or len(session)==0:
          return 'No tiene autorización para realizar esta operación'
      else:
        if request.method=='POST':
            datos_excursion = request.get_json()
            salida = datos_excursion['salida']
            destino = datos_excursion['destino']
            fecha_salida = datos_excursion['fechaSalida']
            fecha_llegada = datos_excursion['fechaLlegada']
            precio = datos_excursion['precio']
            cupo = datos_excursion['cupo']
            reservas = datos_excursion['reservas']
            completo = datos_excursion['completo']
            excursion_nueva=Excursiones(salida=salida,destino=destino,fechaSalida=fecha_salida,fechaLlegada=fecha_llegada,precio=precio,cupo=cupo,reservas=reservas,completo=completo)

            try:
                 db.session.add(excursion_nueva)
                 db.session.commit()
                 return jsonify({"message":"Excursión agregada con éxito."})
            except Exception as e:
                 db.session.rollback()
                 return jsonify({"message":"No se pudo agregar la excursión, algo salió mal."})
            

#MODIFICA LA EXCURSIÓN SELECCIONADA
@app.route('/modificarExcursion', methods=['POST'])
def modificarExcursion():
     if session['role']!='admin' or len(session)==0:
          return 'No tiene autorización para realizar esta operación'
     else:

          if request.method=='POST':
               datos_excursion=request.get_json()
               id=datos_excursion['id']
               salida=datos_excursion['salida']
               destino=datos_excursion['destino']
               fecha_salida = datos_excursion['fechaSalida']
               fecha_llegada = datos_excursion['fechaLlegada']
               precio = datos_excursion['precio']
               cupo = datos_excursion['cupo']
               reservas = datos_excursion['reservas']
               completo = datos_excursion['completo']
          excursionEditada=Excursiones.query.get(id)

          if excursionEditada:
               excursionEditada.salida=salida
               excursionEditada.destino=destino
               excursionEditada.fechaSalida=fecha_salida
               excursionEditada.fechaLlegada=fecha_llegada
               excursionEditada.precio=precio
               excursionEditada.cupo=cupo
               excursionEditada.reservas=reservas
               excursionEditada.completo=completo
          try:
               db.session.commit()
               return jsonify({"message":"La excursión ha sido modificada con éxito"})
          except Exception as e:
               db.session.rollback()
               return jsonify({"message":"Algo salió mal."})

# '''*************************************************************************************************************************************************************************************   
# **************************************************************************************************************************************************************************************
# *
# *                                                 FUNCIONES PARA EL ADMINISTRADOR REFERIDAS A LAS RESERVAS
# *
# **************************************************************************************************************************************************************************************
# **************************************************************************************************************************************************************************************'''



@app.route('/adminreservas', methods=['GET'])
def getadminReservas():
     if len(session)==0 or session['role']!='admin':     
          return redirect(baseurl+'frontamalfi/index.html')
     else:
          consulta=Reservas.query.all()
          resultado=reservas_schema.dump(consulta)
          return jsonify(resultado)
@app.route('/deletereserva/<int:id>', methods=['DELETE'])
def deleteReserva(id):
     if len(session)==0 or session['role']!='admin':
          return redirect(baseurl+'frontamalfi/index.html')
     else:
          reserva=Reservas.query.get(id)
          if reserva:
               db.session.delete(reserva)
               try:
                    db.session.commit()
                    return jsonify({"message":"La reserva se eliminó con éxito"})
               except Exception as e:
                    db.session.rollback()
                    return jsonify({"message":"Algo salió mal. No se pudo eliminar la reserva"})
          else:
               return jsonify({"message":"No se encuentra la reserva"})

               
@app.route('/panelusuario')
def usuario():
     #trae los datos del usuario desde la página de login
     usuario=session['name']
     iduser=int(session['id'])

     consulta = db.session.query(Excursiones.salida, Excursiones.destino, Excursiones.fechaSalida, Excursiones.fechaLlegada, Excursiones.precio, Reservas.adelanto, Reservas.cantidad).join(Reservas).filter(and_(Reservas.idUsuario == iduser, Reservas.idExcursion == Excursiones.id))
     resultado=consulta.all()
     user=Usuarios.query.get(iduser)
     resultadoUser=user_schema.dump(user)
     excursiones=Excursiones.query.all()
     resultadosExcursiones=excs_schema.dump(excursiones)
     reservas=Reservas.query.filter_by(idUsuario=iduser)
     return render_template('html/usuario.html',htmlusuario=resultadoUser,htmlreservas=resultado,htmlexcursiones=resultadosExcursiones)


@app.route('/reservas', methods=['GET'])
def getReservas():
     # usuario=session.get('resultado')
     # idUser=usuario[0]
     reservas = Reservas.query.all()
     resultados= reservas_schema.dump(reservas)
     return jsonify(resultados)


@app.route('/reservar',methods=['POST'])
def reservar():
     usuario=session['name']
     idUser=session['id']

     if request.method=='POST':
          excursiondId=request.form.get('index')
          cantidad=request.form.get('cantidad')
          adelanto=request.form.get('adelanto')
          reserva=Reservas(idUsuario=idUser,idExcursion=excursiondId,adelanto=adelanto,pagado=False,cantidad=cantidad)
          db.session.add(reserva)
          try:               
               db.session.commit()
               return redirect('/panelusuario')
          except Exception as e:
               db.session.rollback()
          return jsonify({"message":"Algo salió mal."})
     




@app.route('/logout')
def logout():
     session.clear()
     return redirect(baseurl+'frontamalfi/index.html')


if __name__=='__main__':
    app.run(debug=True)