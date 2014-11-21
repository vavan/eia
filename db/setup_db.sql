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
-- Table structure for table 'debits'
--

--pid is deprecated

CREATE TABLE debits (
  id INTEGER,
  uid INTEGER NOT NULL,
  mbytes float NOT NULL,
  debit float NOT NULL,
  time datetime NOT NULL,
  rate INTEGER NOT NULL,
  PRIMARY KEY  (id)
) ;


--
-- Table structure for table 'credits'
-- money should be signed!

CREATE TABLE credits (
  id INTEGER,
  uid INTEGER NOT NULL,
  money INTEGER NOT NULL,
  time datetime NOT NULL,
  admin_uid INTEGER NOT NULL,
  flag INTEGER NOT NULL,
  PRIMARY KEY  (id)
) ;


--
-- Table structure for table 'sessions'
--

CREATE TABLE sessions (
  sid varchar(32) NOT NULL,
  time datetime NOT NULL,
  ip varchar(15) NOT NULL,
  uid INTEGER,
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
  descr text,
  time datetime,
  PRIMARY KEY  (uid)
) ;

--
-- Table structure for table 'devices'
--

CREATE TABLE devices (
  id INTEGER,
  name varchar(255) NOT NULL,
  mac varchar(20) NOT NULL,
  PRIMARY KEY  (id)
) ;

--
-- Table structure for table 'alive'
--

CREATE TABLE alive (
  id INTEGER,
  user INTEGER NOT NULL,
  device INTEGER NOT NULL,
  time datetime NOT NULL,
  duration INTEGER NOT NULL,
  PRIMARY KEY  (id)
) ;

CREATE TABLE cache (
  id INTEGER,
  mac varchar(20) NOT NULL,
  PRIMARY KEY  (id)
) ;
