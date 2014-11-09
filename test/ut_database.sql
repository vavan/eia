
CREATE TABLE admins (
  uid INTEGER PRIMARY KEY,
  passwd text,
  ip text,
  name text
);

INSERT INTO admins VALUES (7, MD5('1'), '127.0.0.1', '1');

CREATE TABLE messages (
  id INTEGER PRIMARY KEY,
  uid text,
  time datetime,
  msg text
);

CREATE TABLE debits (
  id INTEGER PRIMARY KEY,
  uid int,
  mbytes float,
  debit float,
  rate int,
  time datetime
);


CREATE TABLE credits (
  id INTEGER PRIMARY KEY,
  uid int,
  maney int,
  time datetime ,
  admin_uid int,
  flag int
);


CREATE TABLE sessions (
  sid varchar PRIMARY KEY,
  time datetime,
  ip varchar,
  uid int
);

CREATE TABLE users (
  uid INTEGER PRIMARY KEY,
  name varchar,
  passwd varchar,
  account float,
  acctlimit float,
  rate int,
  traf float,
  traflimit float,
  descr text
);

CREATE TABLE addresses (
  id INTEGER PRIMARY KEY,
  uid int,
  ip varchar,
  mac varchar
);

INSERT INTO users VALUES (2, '1st', '1', 10, 0, 0, 0, 0, '');
INSERT INTO users VALUES (3, '2nd', '1', 20, 0, 0, 0, 0, '');

INSERT INTO addresses VALUES (1, 2, '192.168.0.2', '00:04:61:A7:71:BE');
INSERT INTO addresses VALUES (2, 3, '192.168.0.3', '00:0E:2E:BE:46:27');

CREATE TABLE providers (
  pid INTEGER PRIMARY KEY,
  name varchar,
  ip varchar,
  iface varchar,
  rate int
);
INSERT INTO providers VALUES (101, 'prov1', '*', 'eth3', 0);

CREATE TABLE rates (
  id INTEGER PRIMARY KEY,
  price float,
  mode text,
  channel int
);

INSERT INTO rates VALUES (0,  2, 'traf_based', 0);
INSERT INTO rates VALUES (1,  0.08, 'traf_based', 0);
INSERT INTO rates VALUES (3,  500, 'daily', 1);
INSERT INTO rates VALUES (10, 250, 'monthly', 2);
