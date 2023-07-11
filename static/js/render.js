/*************************************************************************************************************************************************************************************   
**************************************************************************************************************************************************************************************
*
*                                                       FUNCIONES PARA LOS USUARIOS
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
                item.id=dato[0]
                item.innerHTML+=`<article class="datosPersonales">
                                    <p><h3> ${dato[1]} ${dato[2]}</h3></p>
                                    <p>${dato[3]} años</p>
                                    <p>DNI: ${dato[4]}</p>
                                 </article>
                                 <article class="datosNegocio">
                                    <p>ID: ${dato[0]}</p>
                                    <p>Rol: ${dato[7]}</p>
                                    <p>Correo Registrado:${dato[5]}</p>
                                    <p>Fecha de registro: ${dato[8]}</p>
                                 </article>
                                 <article id='${dato[0]}'>
                                 </article> 
                                 <article class="funciones">
                                    <button onclick="eliminarUsuario(${dato[0]})" id="${dato[0]}" class="botonadmin">Dar de Baja</button>
                                    <button onclick="getReservasUsuario(${dato[0]})" class="botonadmin">Ver reservas</button>
                                    <button onclick="blanquearClave(${dato[0]})" class="botonadmin">Recuperar Clave</button>
                                 </article>`
            plantilla.appendChild(item)
            }
        })
    }
    function eliminarUsuario(index){
        let confirmar=confirm('¿Desea dar de baja al usuario? También se eleminirán las reservas que el usuario haya hecho.')
        if (confirmar){
            
            fetch('/bajaUsuario',{
                method:'POST',
                body:new URLSearchParams({id:index}),
                headers:{
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            }).then(response=>{
                if (response.ok){
                    console.log('Usuario Eliminado');
                    renderUsuarios();
                }
                else{
                    console.log('Error al eliminar el usuario');
                }
            });
        }
    }

   async function getReservasUsuario(index){
        let resultado=document.getElementById(index)

            await fetch(`/reservasUsuario?id=${index}`).then(response=>response.json())
            .then(datos=>{
     
             for(let reserva of datos){
                 //idReserva, idUsuario, idExcursion, adelanto, cantidad, pagado, salida, destino, fechaSalida, fechaLlegada, precio
                 resultado.innerHTML+=`<div class="reservaUsuario" name='reservasdelusuario' >
                                     <p>Código Reserva: ${reserva[0]}</p>
                                     <p>Código Excursión: ${reserva[2]}</p>
                                     <p>Cantidad de lugares: ${reserva[4]} Adelanto: ${reserva[3]} Pagado: ${reserva[5]} Total: ${reserva[10]}</p>
                                     <p>Origen: ${reserva[6]}  Destino:${reserva[7]}</p>
                                     <p>Salida: ${reserva[8]}  Llegada: ${reserva[9]}</p>
                                     <button onclick="ocultar(this)" class='botonadmin'>Ocultar</button>
                                     </div>`
                                 }
             console.log(datos)
     
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
        fetch('/blanquearclave',{
            method:'POST',
            body:new URLSearchParams({id:index}),
            headers:{
                'Content-Type': 'application/x-www-form-urlencoded'
            }
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
        plantilla.innerHTML='<button onclick="agregarExcursion()" class="botonadmin">Agregar</button>';
        await fetch('/excursiones').then(response=>response.json())
        .then(datos=>{
            console.log(datos)
            for(let dato of datos){
                let item=document.createElement('section')
                item.className="resultado"
                item.id=dato[0]
                item.innerHTML+=`<article class="articleExcursiones">
                                    <div id="infoExcursion">
                                    <p>Código ${dato[0]}</p>
                                    <p>Origen: ${dato[1]} Destino: ${dato[2]}</p>
                                    <p>Salida: ${dato[3]} Llegada: ${dato[4]}</p>
                                    <p>Precio: ${dato[5]}</p>
                                    <p>Cupo: ${dato[6]}  Reservas: ${dato[7]}</p>
                                    <p>Completo: ${dato[8]}</p>
                                    </div>
                                    <div id="funciones">
                                    <button onclick="eliminarExcursión(${dato[0]})" id="${dato[0]}" class="botonadmin">Eliminar Excursión</button>
                                    <button onclick="modificarExcursión(${dato[0]})" class="botonadmin">Editar</button>                                    
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
            fetch('/bajaExcursion',{
                method:'POST',
                body:new URLSearchParams({id:index}),
                headers:{
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            }).then(response=>{
                if(response.ok){
                    console.log('Excursión Eliminada')
                    renderExcursiones();
                }
            })
        }

    }

    function agregarExcursion(){
        let excursion={
            'salida':prompt('Ingrese el origen:'),
            'destino':prompt('Ingrese el origen:'),
            'fechaSalida':prompt('Ingreser la fecha de salida y la hora: (Formato YYYY-MM-DD HH:MM:SS'),
            'fechaLlegada':prompt('Ingreser la fecha de llegada y la hora: (Formato YYYY-MM-DD HH:MM:SS'),
            'precio':Number(prompt('Ingrese el precio: (Punto para símbolo decimal')),
            'cupo':Number(prompt('Ingrese el cupo:')),
            'reservas':0,
            'completo':0
        }
        fetch('/altaExcursion',{
            method:'POST',
            body:JSON.stringify(excursion),
            headers:{'Content-Type': 'application/json'}
        }).then(response=>{
            if (response.ok){
                renderExcursiones()
            }
        })
        .catch(error=>{
            console.error('Error: ',error)
        })

        console.log(excursion)
    }

    function modificarExcursión(index){
       
        let excursion={
            'id':Number(index),
            'salida':prompt('Ingrese el origen:'),
            'destino':prompt('Ingrese el origen:'),
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
                                <p>Código Reserva: ${dato[0]}</p>
                                <p>Código Usuario: ${dato[1]} Nombre:${dato[6]} Apellido:${dato[7]}</p>
                                <p>Código Excursión: ${dato[2]}</p>
                                <p>Adelanto: ${dato[3]} Pagado: ${dato[4]}</p>
                                <p>Cantidad: ${dato[5]}</p>
                                </div>                                
                             </article>
                             `
        plantilla.appendChild(item)
        }
    })
}