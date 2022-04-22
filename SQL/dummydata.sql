-- populate locations
insert into `locationsLkUp` (`id`,`name`,`street`,`city`,`state`,`country`)
	values
		(1, "GCC", "123 Acme Dr", "Cleveland", "Ohio", "USA"),
		(2, "SCC", "456 Sesame St", "New York", "New York", "USA"),
		(3, "TCC", "789 Ottawa Dr", "Toronto", "Ontario", "Canada");

-- populate rooms
insert into `roomLkUp` (`id`,`name`,`locationId`) 
	values
		(1,"gcc-01",1), (2,"gcc-02",1), (3,"gcc-03",1),
		(4,"scc-01",2), (5,"scc-02",2), (6,"scc-03",2),
		(7,"tcc-01",3), (8,"tcc-02",3), (9,"tcc-03",3);

-- populate shelves
insert into `shelfLkUp` (`id`,`name`,`roomId`) 
	values 
	(1, "shelf-01",1), (2, "shelf-02",1), (3, "shelf-03",1),
	(4, "shelf-01",2), (5, "shelf-02",2), (6, "shelf-03",2),
	(7, "shelf-01",3), (8, "shelf-02",3), (9, "shelf-03",3),
	(10, "shelf-01",4), (11, "shelf-02",4), (12, "shelf-03",4),
	(13, "shelf-01",5), (14, "shelf-02",5), (15, "shelf-03",5),
	(16, "shelf-01",6), (17, "shelf-02",6), (18, "shelf-03",6),
	(19, "shelf-01",7), (20, "shelf-02",7), (21, "shelf-03",7),
	(22, "shelf-01",8), (23, "shelf-02",8), (24, "shelf-03",8),
	(25, "shelf-01",9), (26, "shelf-02",9), (27, "shelf-03",9);

-- -- populate vendors
insert into `vendorLkUp` (`id`,`name`) 
	values 
		(1, "Lenovo"), (2, "Cisco"), (3, "HP");

-- populate categories
insert into `categoryLkUp` (`id`,`name`,`description`) 
	values 
		(1, "server", "server hardware"),
		(2, "network", "network gear"),
		(3, "part", "replacment parts");

-- populate model #s
insert into `modelNumLkUp` (`id`,`name`,`description`,`categoryId`,`vendorId`)
	values
		(1,"x3650","3650 X Series server",1,1),
		(2,"x3850","3850 X Series server",1,1),
		(3,"x3550","3550 X Series server",1,1),
		(4,"N1000","N 1000 switch",2,1),
		(5,"6500-E","Catalyst 6500 Chassis",2,2),
		(6,"8500-E","Catalyst 8500 Chassis",2,2),
		(7,"9500-E","Catalyst 9500 Chassis",2,2),
		(8,"UCS-2200","UCS 2200 server",1,2),
		(9,"TX-400","TX 400 server",1,3),
		(10,"TX-800","TX 800 server",1,3),
		(11,"NX-100","NX 100 switch",2,3),
		(12,"L-FRU-100","16GB DDR4 RAM",3,1),
		(13,"L-FRU-200","Intel Xeon 3.5GHz",3,1),
		(14,"C-FRU-100","switch fan",3,2),
		(15,"C-FRU-200","switch power supply",3,2),
		(16,"H-FRU-200","TX 400 motherboard",3,3),
		(17,"H-FRU-200","NX 100 power supply",3,3);

-- populate users
insert into `user` (`id`,`email`,`password`)
	values
		(1,"jim@acme.com","1234"),
		(2,"lisa@acme.com","1234"),
		(3,"peter@acme.com","1234");

-- populate items
insert into `items` (`id`,`poNumber`,`serialNumber`,`isPart`, `shelfId`, `categoryId`, `modelId`, `rcvdBy`, `vendorId`, `roomId`, `locationId`)
	values
		(1,"PO-2022-101","L-YX567",0, 1,1,1,1,1,1,1),
		(2,"PO-2022-102","L-HJ390",0, 2,1,2,2,1,1,1),
		(3,"PO-2022-103","L-KE203",0, 3,1,3,3,1,1,1),
		(4,"PO-2022-104","C-NB349",0, 1,2,4,1,2,2,1),
		(5,"PO-2022-105","C-ER342",0, 2,2,5,2,2,2,1),
		(6,"PO-2022-106","C-MD652",0, 3,2,6,3,2,2,1),
		(7,"PO-2022-107","H-NB349",0, 1,2,9,1,3,3,1),
		(8,"PO-2022-108","H-ER342",0, 2,2,10,2,3,3,1),
		(9,"PO-2022-109","H-MD652",0, 3,2,11,3,3,3,1);
		(10,"PO-2022-107","H-NB349",0, 1,2,9,1,3,3,1),
		(11,"PO-2022-108","H-ER342",0, 2,2,10,2,3,3,1),
		(12,"PO-2022-109","H-MD652",0, 3,2,11,3,3,3,1);