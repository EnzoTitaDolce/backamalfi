create database amalfi;

use amalfi;
drop table usuarios;

create table usuarios(

id int auto_increment primary key,
firstname varchar(80) not null,
lastname varchar (80) not null,
age int not null,
idNumber varchar(80) not null,
mail varchar(50) not null,
clave varchar(100) not null
);

drop table excursiones;
create table excursiones(
id int auto_increment  primary key,
salida varchar(30) not null,
destino varchar(30) not null,
fechaSalida datetime not null,
fechaLlegada datetime not null,
precio decimal(13,2) not null,
cupo int not null,
reservas int not null,
completo bool
);


drop table reservas;

create table reservas(

idReserva int auto_increment primary key,
idUsuario int,
idExcursion int,
adelanto decimal(13,2),
pagado bool,
foreign key (idExcursion) references excursiones(id),
foreign key (idUsuario) references usuarios(id)
);

insert into usuarios (firstname,lastname,age,idNumber,mail,clave) values('Enzo','Tita Dolce','34','33753997','etitadolce@gmail.com',(sha2('EGTD@do2289',256)));
insert into usuarios (firstname,lastname,age,idNumber,mail,clave,role) values('Jhon','Doe','24','88888888','jhon@doe.com',(sha2('jhondoe',256)),'user');
insert into usuarios (firstname,lastname,age,idNumber,mail,clave,role,fechaIngreso) values ('Homero','Simpson','47','33333333','homero@simpson.com',(sha2('homerosimpson',256)),'user',curdate());
insert into excursiones (salida,destino,fechaSalida,fechaLlegada,precio,cupo,reservas,completo) values ('Salta','Tucuman','2023-02-02 08:00:00','2023-02-02 12:00:00','563.17',100,0,false);
insert into excursiones (salida,destino,fechaSalida,fechaLlegada,precio,cupo,reservas,completo) values ('Jujuy','La Quiaca','2023-04-10 08:00:00','2023-04-11 12:00:00','3563.17',100,0,false);
insert into reservas (idUsuario,idExcursion,adelanto,pagado,cantidad) values (1,4,'456.3',false,5);
insert into reservas (idUsuario,idExcursion,adelanto,pagado,cantidad) values (30,2,'456.3',false,3);
insert into reservas (idUsuario,idExcursion,adelanto,pagado,cantidad) values (31,2,'456.21',false,21);

truncate table usuarios;
truncate table excursiones;
truncate table reservas;
truncate table usuarios;

select * from usuarios;
select * from reservas;
select * from excursiones;
select *, salida,destino, fechaSalida, fechaLlegada, precio from reservas join excursiones on reservas.idExcursion=excursiones.id where reservas.idUsuario=28;
select *, salida,destino, fechaSalida, fechaLlegada, precio, adelanto,cantidad from reservas join excursiones on reservas.idExcursion=excursiones.id where reservas.idUsuario=32;
select salida,destino, fechaSalida, fechaLlegada,precio,adelanto,cantidad from reservas join excursiones on reservas.idExcursion=excursiones.id where reservas.idUsuario=32;
select idReserva, idUsuario, idExcursion, adelanto, cantidad, pagado, salida, destino, fechaSalida, fechaLlegada, precio from reservas join excursiones where reservas.idUsuario=40;
select idNumber from usuarios where id=41;

delete from usuarios where id = 41;
delete from reservas where idUsuario=28;
delete from reservas where idReserva=2;

alter table reservas add column cantidad int;

alter table usuarios add column role enum('admin','user') not null;
alter table usuarios add column fechaIngreso date;
update usuarios set clave=(sha2('homerosimpson',256)) where id=42;
update usuarios set firstname="Mario", lastname="Baracu", mail="fake@mail.com" where id=28;
update usuarios set idNumber='898989' where id=28;
update usuarios set firstname = 'José' where id=32;
update usuarios set lastname = 'Simpson' where id=37;
update usuarios set fechaingreso = curdate();
update excursiones set reservas=0,cupo=100;
update reservas set cantidad = 0 where idReserva=1;
update reservas set cantidad = 2 where idReserva=2;



delimiter //
-- Trigger para operación de inserción
CREATE TRIGGER actualizar_cupo_insert
AFTER INSERT ON reservas
FOR EACH ROW
BEGIN
  UPDATE excursiones
  SET cupo = cupo - NEW.cantidad
  WHERE id = NEW.idExcursion;
END//
delimiter;

delimiter //
-- Trigger para operación de eliminación
CREATE TRIGGER actualizar_cupo_delete
AFTER DELETE ON reservas
FOR EACH ROW
BEGIN
  UPDATE excursiones
  SET cupo = cupo + OLD.cantidad
  WHERE id = OLD.idExcursion;
END//
delimiter ;


delimiter //
create trigger actualizar_reservas
after insert on reservas
for each row
begin
update excursiones
set reservas=reservas+1
where id=new.idExcursion;
end//
delimiter ;

delimiter //
create trigger actualizar_reservas_delete
after delete on reservas
for each row
begin
update excursiones
set reservas=reservas-1
where id=OLD.idExcursion;
end//
delimiter ;



