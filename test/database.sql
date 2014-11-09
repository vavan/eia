
CREATE TABLE admins (
  uid INTEGER PRIMARY KEY,
  passwd text,
  ip text,
  name text,
  time datetime
);

INSERT INTO admins VALUES (7, MD5('1'), '127.0.0.1', '1', 0);

CREATE TABLE messages (
  id INTEGER PRIMARY KEY,
  uid text,
  sender text,
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
  traf float,
  traflimit float,
  descr text,
  rate int,
  time datetime
);

CREATE TABLE addresses (
  id INTEGER PRIMARY KEY,
  uid int,
  ip varchar,
  mac varchar
);

insert into addresses VALUES (1, 2, '192.168.0.2', '00:04:61:A7:71:BE');
insert into addresses VALUES (2, 3, '192.168.0.3', '01:04:61:A7:71:BE');
insert into addresses VALUES (3, 4, '192.168.0.4', '02:04:61:A7:71:BE');
insert into addresses VALUES (4, 5, '192.168.0.5', '03:04:61:A7:71:BE');
insert into addresses VALUES (5, 6, '192.168.0.6', '04:04:61:A7:71:BE');
insert into addresses VALUES (6, 7, '192.168.0.7', '05:04:61:A7:71:BE');

INSERT INTO users VALUES (2, '2st', '1', 10, 0, 0, 0, '', 3, '');
INSERT INTO users VALUES (3, '3nd', '1', 20, 0, 0, 0, '', 2, '');
INSERT INTO users VALUES (4, '4nd', '1', 20, 0, 0, 0, '', 2, '');
INSERT INTO users VALUES (5, '5nd', '1', 20, 0, 0, 0, '', 2, '');
INSERT INTO users VALUES (6, '6nd', '1', 20, 0, 0, 0, '', 2, '');
INSERT INTO users VALUES (7, '7nd', '1', 20, 0, 0, 0, '', 2, '');

CREATE TABLE providers (
  pid INTEGER PRIMARY KEY,
  name varchar,
  ip varchar,
  iface varchar,
  rate int
);
INSERT INTO providers VALUES (101, 'prov1', '*', 'eth3', 10);

CREATE TABLE rates (
  id INTEGER PRIMARY KEY,
  price float,
  mode text,
  channel int
);

INSERT INTO rates VALUES (0,  0.1, 'traf_based', 0);
INSERT INTO rates VALUES (2,  0.08, 'traf_based', 0);
INSERT INTO rates VALUES (3,  3, 'daily', 1);
INSERT INTO rates VALUES (10, 250, 'monthly', 2);

