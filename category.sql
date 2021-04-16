------------------------------------------------------------
------------------------STORE-------------------------------
------------------------------------------------------------

CREATE TABLE if NOT EXISTS organization(
	org_id INT(10) AUTO_INCREMENT,
	company VARCHAR(50) NOT NULL,
	manager_name VARCHAR(50) NOT NULL,
	manage_phone_number varchar(20) NULL,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP(),
	PRIMARY KEY (org_id)
) ENGINE=InnoDB DEFAULT CHARSET=UTF8;

INSERT INTO organization(company, manager_name, manage_phone_number) 
VALUES ('ACOMPANY', 'A님', '010-0000-0000')

------------------------------------------------------------
------------------------FESTIVAL----------------------------
------------------------------------------------------------


CREATE TABLE if NOT EXISTS festival(
	festival_id INT(10) AUTO_INCREMENT,
	festival_name VARCHAR(30) NOT NULL,
	org_id INT(10) NOT NULL,
	period VARCHAR(100) NULL,
	location VARCHAR(10) NOT NULL,
	url VARCHAR(100) NULL,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP(),
	PRIMARY KEY (festival_id),
	FOREIGN KEY (org_id) REFERENCES organization(org_id) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=UTF8;


INSERT INTO festival(festival_name, org_id, period, location, url) 
VALUES ('Afestival', 1, '2021-04-15~2021-04-15', '서울', 'https://github.com/jutor')

------------------------------------------------------------
------------------------STORE-------------------------------
------------------------------------------------------------

CREATE TABLE if NOT EXISTS store(
	store_id INT(10) AUTO_INCREMENT,
	festival_id INT(20) NOT NULL,
	store_name VARCHAR(20) NOT NULL,
	store_description VARCHAR(150) NULL,
	contact_number VARCHAR(15) NULL,
	category VARCHAR(20) NOT NULL,
	license_number VARCHAR(20) NOT NULL,
	location_number VARCHAR(20) NOT NULL,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP(),
	PRIMARY KEY (store_id),
	FOREIGN KEY (festival_id) REFERENCES festival(festival_id) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=UTF8;


INSERT INTO store(festival_id, store_name, store_description, contact_number, category, license_number, location_number) 
VALUES ('1', 'A', 'A가게', 'AAA-AAA', '한식', 'AAAA', 'A구역')

INSERT INTO store(festival_id, store_name, store_description, contact_number, category, license_number, location_number) 
VALUES ('1', 'B', 'B가게', 'BBB-BBB', '한식', 'BBBB', 'A구역')

INSERT INTO store(festival_id, store_name, store_description, contact_number, category, license_number, location_number) 
VALUES ('1', 'C', 'C가게', 'CCC-CCC', '치킨', 'CCCC', 'C구역')

INSERT INTO store(festival_id, store_name, store_description, contact_number, category, license_number, location_number) 
VALUES ('1', 'D', 'D가게', 'DDD-DDD', '치킨', 'DDDD', 'C구역')

INSERT INTO store(festival_id, store_name, store_description, contact_number, category, license_number, location_number) 
VALUES ('1', 'E', 'E가게', 'EEE-EEE', '태국음식', 'EEEE', 'E구역')



------------------------------------------------------------
------------------------MENU--------------------------------
------------------------------------------------------------

CREATE TABLE if NOT EXISTS menu(
	menu_id INT(20) AUTO_INCREMENT,
	store_id INT(20) NOT NULL,
	menu_name VARCHAR(20) NOT NULL,
	menu_price int NOT NULL,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP(),
	PRIMARY KEY (menu_id),
	FOREIGN KEY (store_id) REFERENCES store(store_id) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=UTF8;


INSERT INTO menu(store_id, menu_name, menu_price) 
VALUES (1, '김치찌개', 25000)

INSERT INTO menu(store_id, menu_name, menu_price) 
VALUES (3, '후라이드치킨', 10000)
INSERT INTO menu(store_id, menu_name, menu_price) 
VALUES (3, '닭똥집', 8000)

INSERT INTO menu(store_id, menu_name, menu_price) 
VALUES (3, '옛날치킨', 8000)




------------------------------------------------------------
---------------------orders---------------------------------
------------------------------------------------------------

CREATE TABLE if NOT EXISTS orders(
	order_id INT(20) AUTO_INCREMENT,
	user_id INT(10) NOT NULL,
	store_id INT(10) NOT NULL,
	menu_name VARCHAR(40) NOT NULL,
	total_qty INT(10) DEFAULT 1,
	total_price INT(30) NOT NULL,
	payment VARCHAR(20) DEFAULT 'Card',
	requests VARCHAR(100) NULL,
	order_time DATETIME DEFAULT CURRENT_TIMESTAMP(),
	PRIMARY KEY (order_id)
	
) ENGINE=InnoDB DEFAULT CHARSET=UTF8;

------------------------------------------------------------
---------------------order_detail---------------------------
------------------------------------------------------------



CREATE TABLE if NOT EXISTS order_detail(
	order_detail_id INT(10) AUTO_INCREMENT,
	order_id INT(20) NOT NULL,
	menu_id INT(20) NOT NULL,
	food_price INT(30) NOT NULL,
	order_state VARCHAR(20) DEFAULT '주문중',
	food_qty INT(10) DEFAULT 1,
	PRIMARY KEY (order_detail_id),
	FOREIGN KEY (order_id) REFERENCES orders(order_id) ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY (menu_id) REFERENCES menu(menu_id) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=UTF8;