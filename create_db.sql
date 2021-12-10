create schema if not exists users;
use users;

drop table if exists user;
CREATE TABLE `user` (
  `userID` int NOT NULL AUTO_INCREMENT,
  `nameLast` varchar(256) DEFAULT NULL,
  `nameFirst` varchar(256) DEFAULT NULL,
  `email` varchar(256) NOT NULL,
  `addressID` int DEFAULT NULL,
  `password` varchar(256) NOT NULL,
  `gender` varchar(16) DEFAULT NULL,
  PRIMARY KEY (`userID`),
  UNIQUE KEY `User_email_uindex` (`email`),
  UNIQUE KEY `User_userID_uindex` (`userID`)
);

drop table if exists address;
CREATE TABLE `address` (
  `addressID` int NOT NULL AUTO_INCREMENT,
  `address` varchar(768) NOT NULL,
  `postalCode` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`addressID`),
  UNIQUE KEY `addresses_address_uindex` (`address`)
);

insert into user (nameLast, nameFirst, email, addressID, password, gender)
values ('Deep', 'Breath', 'dontbeangry@gmail.com', NULL, 'Pop', 'male'),
       ('ahhhhhh', 'Breath', 'dontbesilly@gmail.com', NULL, 'Pop', 'male'),
       ('Last', 'First', 'helloworld@gmail.com', NULL, 'Pop', 'female');

insert into address (address, postalCode) values ('1080 Amsterdam Ave', 10041), ('2960 Broadway', 10001), ('3000 Broadway', 10027);
