/*************************************************************************************************************************************************************************************   
**************************************************************************************************************************************************************************************
*
*                                             FUNCIONES PARA EL ADMIN REFERIDAS A LOS USUARIOS
*
**************************************************************************************************************************************************************************************
**************************************************************************************************************************************************************************************/
    
    async function renderUsuarios(){
        let plantilla=document.getElementById('contenido')
        plantilla.innerHTML='';
        await fetch('/adminusuarios').then(response=>response.json())
        .then(datos=>{
            console.log(datos)
            for(let dato of datos){
                let item=document.createElement('section')
                item.className="resultado"
                item.id=dato['id']
                item.innerHTML+=`<article class="datosPersonales">
                                    <p><h3> ${dato['firstname']} ${dato['lastname']}</h3></p>
                                    <p>${dato['age']} años</p>
                                    <p>DNI: ${dato['idNumber']}</p>
                                 </article>
                                 <article class="datosNegocio">
                                    <p>ID: ${dato['id']}</p>
                                    <p>Rol: ${dato['role']}</p>
                                    <p>Correo Registrado:${dato['mail']}</p>
                                    <p>Fecha de registro: ${dato['fechaIngreso']}</p>
                                 </article>
                                <article id='${dato['id']}'>
                                </article> 
                                 <article class="funciones">
                                    <button onclick="eliminarUsuario(${dato['id']})" id="${dato['id']}" class="botonadmin">Dar de Baja</button>
                                    <button onclick="getReservasUsuario(${dato['id']})" class="botonadmin">Ver reservas</button>
                                    <button onclick="blanquearClave(${dato['id']})" class="botonadmin">Recuperar Clave</button>
                                 </article>`
            plantilla.appendChild(item)
            }
        })
    }
    function eliminarUsuario(index){
        let confirmar=confirm('¿Desea dar de baja al usuario? También se eleminirán las reservas que el usuario haya hecho.')
        if (confirmar){
            fetch(`/bajaUsuario/${index}`,{method:'DELETE'}).then(response=>{
                if(response.ok){
                    console.log("usuario eliminado")
                }
                else{
                    console.log('error al eliminar el usuario')
                }
                renderUsuarios()
            })            
        }
    }













   async function getReservasUsuario(index){
        let resultado=document.getElementById(index)

            await fetch(`/reservasUsuario/${index}`).then(response=>response.json())
            .then(datos=>{
                
                if(datos && datos.length >0){

                    for(let reserva of datos){
                        //idReserva, idUsuario, idExcursion, adelanto, cantidad, pagado, salida, destino, fechaSalida, fechaLlegada, precio
                        resultado.innerHTML+=`<div class="reservaUsuario" name='reservasdelusuario'>
                                            <p>Código Reserva: ${reserva['idReserva']}</p>
                                            <p>Código Excursión: ${reserva['idExcursion']}</p>
                                            <p>Cantidad de lugares: ${reserva['cantidad']} Adelanto: ${reserva['adelanto']} Pagado: ${reserva['pagado']}</p>
                                          
                                            <button onclick="ocultar(this)" class='botonadmin'>Ocultar</button>
                                            </div>`
                                        }
                }
                else{
                    resultado.innerHTML+=`<div class="reservaUsuario" name='reservasdelusuario'>
                                            No hay reservas para este usuario.
                                        <button onclick="ocultar(this)" class='botonadmin'>Ocultar</button>
                                        </div>`
                }
            })
        }
    
    function ocultar(){
        var contenedor=document.getElementsByName('reservasdelusuario');
        if(contenedor){
            for(let elemento of contenedor){
                elemento.style.display='none';
            }
        }
    }

    function blanquearClave(index){
        fetch(`/blanquearclave/${index}`,{
            method:'PATCH'
        }).then(response=>{
            if (response.ok){
                return response.json();
            }
        }).then(datos=>{
            console.log(datos)
            alert('La nueva contraseña es:'+datos['clave'])
        })
    }

/*************************************************************************************************************************************************************************************   
**************************************************************************************************************************************************************************************
*
*                                                       FUNCIONES PARA LAS EXCURSIONES
*
**************************************************************************************************************************************************************************************
**************************************************************************************************************************************************************************************/





    async function renderExcursiones(){
       
        let plantilla=document.getElementById('contenido')
        plantilla.innerHTML='<button onclick="openModal()" class="botonadmin">Agregar</button>';
        await fetch('/excursiones').then(response=>response.json())
        .then(datos=>{
            console.log(datos)
            for(let dato of datos){
                let item=document.createElement('section')
                item.className="resultado"
                item.id=dato[0]
                item.innerHTML+=`<article class="articleExcursiones">
                                    <div id="infoExcursion">
                                    <p>Código ${dato['id']}</p>
                                    <p>Origen: ${dato['salida']} Destino: ${dato['destino']}</p>
                                    <p>Salida: ${dato['fechaSalida']} Llegada: ${dato['fechaLlegada']}</p>
                                    <p>Precio: ${dato['precio']}</p>
                                    <p>Cupo: ${dato['cupo']}  Reservas: ${dato['reservas']}</p>
                                    <p>Completo: ${dato['completo']}</p>
                                    </div>
                                    <div id="funciones">
                                    <button onclick="eliminarExcursión(${dato['id']})" id="${dato['id']}" class="botonadmin">Eliminar Excursión</button>
                                    <button onclick="modificarExcursión(${dato['id']})" class="botonadmin">Editar</button>                                    
                                    </div>
                                 </article>
                                 `
            plantilla.appendChild(item)
            }
        })
    }






    function eliminarExcursión(index){
        let confirmar=confirm('Si elimina la excursión también eliminará las reservas de la misma.')
        if (confirmar){
            fetch(`/bajaExcursion/${index}`,{
                method:'DELETE'
            }).then(response=>{
                if(response.ok){
                    console.log('Excursión Eliminada')
                    renderExcursiones();
                }
            })
        }

    }








    function openModal() {
        var modal = document.getElementById("myModal");
        modal.style.display = "block";
    }
    function closeModal() {
        var modal = document.getElementById("myModal");
        modal.style.display = "none";
    }

    function agregarExcursion(){
        
        
        // Obtener los valores de los campos
        var salida = document.getElementById("salida").value;
        var destino = document.getElementById("destino").value;
        var fechaSalida = document.getElementById("fechaSalida").value;
        var fechaLlegada = document.getElementById("fechaLlegada").value;
        var precio = document.getElementById("precio").value;
        var cupo = document.getElementById("cupo").value;
        var reservas = document.getElementById("reservas").value;
        var completo = document.getElementById("completo").checked;
        
        let excursion_nueva={
            "salida":salida,
            "destino":destino,
            "fechaSalida":fechaSalida,
            "fechaLlegada":fechaLlegada,
            "precio":precio,
            "cupo":cupo,
            "reservas":reservas,
            "completo":completo
        }
        alert(excursion_nueva.precio)

        fetch('/altaExcursion',{
            method:'POST',
            body:JSON.stringify(excursion_nueva),
            headers:{'Content-Type': 'application/json'}
        }).then(response=>{
            if (response.ok){
                renderExcursiones()
            }
        })
        .catch(error=>{
            console.error('Error: ',error)
        })
        console.log(excursion_nueva)
        renderExcursiones()
    }







    function modificarExcursión(index){
       
        let excursion={
            'id':Number(index),
            'salida':prompt('Ingrese el origen:'),
            'destino':prompt('Ingrese el destino:'),
            'fechaSalida':prompt('Ingreser la fecha de salida y la hora: (Formato YYYY-MM-DD HH:MM:SS'),
            'fechaLlegada':prompt('Ingreser la fecha de llegada y la hora: (Formato YYYY-MM-DD HH:MM:SS'),
            'precio':Number(prompt('Ingrese el precio: (Punto para símbolo decimal')),
            'cupo':Number(prompt('Ingrese el cupo:')),
            'reservas':0,
            'completo':0
        }

        fetch('/modificarExcursion',{
            method:'POST',
            body:JSON.stringify(excursion),
            headers:{
                'Content-Type': 'application/json'
            }
        }).then(response=>{
            if (response.ok){
                renderExcursiones()
            }
        })
        .catch(error=>{
            console.error('Error: ',error)
        })
       
    }

/*************************************************************************************************************************************************************************************   
**************************************************************************************************************************************************************************************
*
*                                                       FUNCIONES PARA LAS RESERVAS
*
**************************************************************************************************************************************************************************************
**************************************************************************************************************************************************************************************/

async function renderReservas(){
        
    let plantilla=document.getElementById('contenido')
    plantilla.innerHTML="";
    
    await fetch('/adminreservas').then(response=>response.json())
    .then(datos=>{
        console.log(datos)
        for(let dato of datos){
            let item=document.createElement('section')
            item.className="resultado"
            item.id=dato[0]
            item.innerHTML+=`<article class="articleExcursiones">
                                <div id="infoExcursion">
                                <p>Código Reserva: ${dato['idReserva']}</p>
                                <p>Código Usuario: ${dato['idUsuario']}</p>
                                <p>Código Excursión: ${dato['idExcursion']}</p>
                                <p>Adelanto: ${dato['adelanto']} Pagado: ${dato['pagado']}</p>
                                <p>Cantidad: ${dato['cantidad']}</p>
                                </div>
                                <button onclick="eliminarReserva(${dato['idReserva']})">Eliminar</button>
                             </article>
                             `
        plantilla.appendChild(item)
        }
    })
}

async function eliminarReserva(index){

    await fetch(`/deletereserva/${index}`, {
        method:'DELETE'
    }).then(response=>{
        if (response.ok){
            console.log("Reserva Eliminada")
        }
        renderReservas()
    })
    }