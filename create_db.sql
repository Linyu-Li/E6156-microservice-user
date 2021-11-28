create table users.user
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

alter table users.user
	add primary key (userID);


create table users.addresses
(
	id int auto_increment
		primary key,
	address varchar(768) not null,
	constraint addresses_address_uindex
		unique (address)
);
