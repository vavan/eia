DROP DATABASE IF EXISTS easy;
CREATE DATABASE easy;
USE easy;

#
# Table structure for table 'admins'
#

CREATE TABLE admins (
  uid int unsigned NOT NULL,
  passwd varchar(40) NOT NULL,
  ip varchar(15) NOT NULL,
  name varchar(255) NOT NULL,
  time datetime NOT NULL,
  PRIMARY KEY  (uid)
) TYPE=MyISAM;
ALTER TABLE admins AUTO_INCREMENT = 50000;



#
# Table structure for table 'messages'
#

CREATE TABLE messages (
  id int unsigned NOT NULL auto_increment,
  uid char(9) NOT NULL,
  sender char(9) NOT NULL,
  time datetime NOT NULL,
  msg text NOT NULL,
  PRIMARY KEY  (id)
) TYPE=MyISAM;

#
# Table structure for table 'debits'
#

#pid is deprecated

CREATE TABLE debits (
  id int unsigned NOT NULL auto_increment,
  uid int unsigned NOT NULL,
  mbytes float NOT NULL,
  debit float NOT NULL,
  time datetime NOT NULL,
  rate int unsigned NOT NULL,
  PRIMARY KEY  (id)
) TYPE=MyISAM;


#
# Table structure for table 'credits'
# maney shoud be signed!

CREATE TABLE credits (
  id int unsigned NOT NULL auto_increment,
  uid int unsigned NOT NULL,
  money int NOT NULL,
  time datetime NOT NULL,
  admin_uid int NOT NULL,
  flag int unsigned NOT NULL,
  PRIMARY KEY  (id)
) TYPE=MyISAM;

#  descr text NOT NULL default '',

#
# Table structure for table 'sessions'
#

CREATE TABLE sessions (
  sid varchar(32) NOT NULL,
  time datetime NOT NULL,
  ip varchar(15) NOT NULL,
  uid int unsigned,
  PRIMARY KEY  (sid)
) TYPE=MyISAM;

#
# Table structure for table 'users'
#

#price, daily are deprecated

CREATE TABLE users (
  uid int unsigned NOT NULL auto_increment,
  name varchar(255) NOT NULL,
  passwd varchar(15) NOT NULL,
  account float NOT NULL,
  acctlimit float NOT NULL,
  traf float NOT NULL,
  traflimit float NOT NULL,
  descr text NOT NULL,
  rate int unsigned NOT NULL,
  time datetime NOT NULL,
  PRIMARY KEY  (uid)
) TYPE=MyISAM;
ALTER TABLE users AUTO_INCREMENT = 1;

#
# Table structure for table 'providers'
#price, monthly are deprecated

CREATE TABLE providers (
  pid int unsigned NOT NULL auto_increment,
  name varchar(255) NOT NULL,
  ip varchar(15) NOT NULL,
  iface varchar(15) NOT NULL,
  descr text NOT NULL,
  rate int unsigned NOT NULL,
  PRIMARY KEY  (pid)
) TYPE=MyISAM;
ALTER TABLE providers AUTO_INCREMENT = 10000;

CREATE TABLE rates (
  id int unsigned NOT NULL auto_increment,
  price float NOT NULL,
  mode varchar(15) NOT NULL,
  channel int NOT NULL,
  PRIMARY KEY  (id)
) TYPE=MyISAM;
insert into rates values (1, 1, 'traf_based', 0);

CREATE TABLE addresses (
  id int NOT NULL auto_increment,
  uid int NOT NULL,
  ip varchar(15) NOT NULL,
  mac varchar(20) NOT NULL,
  PRIMARY KEY  (id)
) TYPE=MyISAM;
