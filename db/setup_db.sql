-- DROP DATABASE IF EXISTS easy;
-- CREATE DATABASE easy;
-- USE easy;

--
-- Table structure for table 'admins'
--

CREATE TABLE admins (
  uid INTEGER,
  passwd varchar(40) NOT NULL,
  ip varchar(15) NOT NULL,
  name varchar(255) NOT NULL,
  time datetime NOT NULL,
  PRIMARY KEY  (uid)
) ;
-- ALTER TABLE admins AUTO_INCREMENT = 50000;

INSERT INTO admins VALUES (1, MD5('admin'), '0.0.0.0', 'admin', '2014');


--
-- Table structure for table 'messages'
--

CREATE TABLE messages (
  id INTEGER,
  uid char(9) NOT NULL,
  sender char(9) NOT NULL,
  time datetime NOT NULL,
  msg text NOT NULL,
  PRIMARY KEY  (id)
) ;

--
-- Table structure for table 'debits'
--

--pid is deprecated

CREATE TABLE debits (
  id INTEGER,
  uid int unsigned NOT NULL,
  mbytes float NOT NULL,
  debit float NOT NULL,
  time datetime NOT NULL,
  rate int unsigned NOT NULL,
  PRIMARY KEY  (id)
) ;


--
-- Table structure for table 'credits'
-- money should be signed!

CREATE TABLE credits (
  id INTEGER,
  uid int unsigned NOT NULL,
  money int NOT NULL,
  time datetime NOT NULL,
  admin_uid int NOT NULL,
  flag int unsigned NOT NULL,
  PRIMARY KEY  (id)
) ;

--  descr text NOT NULL default '',

--
-- Table structure for table 'sessions'
--

CREATE TABLE sessions (
  sid varchar(32) NOT NULL,
  time datetime NOT NULL,
  ip varchar(15) NOT NULL,
  uid int unsigned,
  PRIMARY KEY  (sid)
) ;

--
-- Table structure for table 'users'
--

--price, daily are deprecated

CREATE TABLE users (
  uid INTEGER,
  name varchar(255) NOT NULL,
  passwd varchar(15) NOT NULL,
  account float NOT NULL,
  acctlimit float NOT NULL,
  traf float NOT NULL,
  traflimit float NOT NULL,
  descr text,
  rate int unsigned NOT NULL,
  time datetime,
  PRIMARY KEY  (uid)
) ;
-- ALTER TABLE users AUTO_INCREMENT = 1;

--
-- Table structure for table 'providers'
--price, monthly are deprecated

CREATE TABLE providers (
  pid INTEGER,
  name varchar(255) NOT NULL,
  ip varchar(15) NOT NULL,
  iface varchar(15) NOT NULL,
  descr text,
  rate int unsigned NOT NULL,
  PRIMARY KEY  (pid)
) ;
-- ALTER TABLE providers AUTO_INCREMENT = 10000;

CREATE TABLE rates (
  id INTEGER,
  price float NOT NULL,
  mode varchar(15) NOT NULL,
  PRIMARY KEY  (id)
) ;
insert into rates values (1, 1, 'traf_based');

CREATE TABLE addresses (
  id INTEGER,
  uid int NOT NULL,
  ip varchar(15) NOT NULL,
  mac varchar(20) NOT NULL,
  PRIMARY KEY  (id)
) ;
