create schema if not exists users;
use users;

drop table if exists user;
create table user
(
	userID int auto_increment,
	nameLast varchar(256) null,
	nameFirst varchar(256) null,
	email varchar(256) not null,
	addressID int null,
	password varchar(256) not null,
	gender varchar(16) null,
	constraint User_email_uindex
		unique (email),
	constraint User_userID_uindex
		unique (userID)
);

alter table user
	add primary key (userID);

drop table if exists addresses;
create table addresses
(
	id int auto_increment
		primary key,
	address varchar(768) not null,
	constraint addresses_address_uindex
		unique (address)
);

insert into user (nameLast, nameFirst, email, addressID, password, gender)
values ('Deep', 'Breath', 'dontbeangry@gmail.com', NULL, 'Pop', 'male'),
       ('ahhhhhh', 'Breath', 'dontbesilly@gmail.com', NULL, 'Pop', 'male');