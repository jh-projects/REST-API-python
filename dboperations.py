from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection
from dbmodel import tblUser, tblItem, tblCategory, tblManufacturer, tblModelNumber, tblBuilding, tblRoom, tblShelf, tblPartQuantity

@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()
    
def populateDB(db):
    db.create_all()

    testData = {    
                    'user1' : tblUser(username="admin",email="a@b.com",password="password", isAdmin=True),
                    'user2': tblUser(username="user1",email="a@bb.com",password="password"),
                    'b1' : tblBuilding(name="Unit1", street="123 Street", city="Chicago", region="Illinois", country="USA"),
                    'b2' : tblBuilding(name="Unit2", street="456 Drive", city="Toronto", region="Ontario", country="Canada"),
                    'r1' : tblRoom(name="US-ST-1",buildingId=1),
                    'r2' : tblRoom(name="US-ST-2",buildingId=1),
                    'r3' : tblRoom(name="CA-ST-1",buildingId=2),
                    'r4' : tblRoom(name="CA-ST-2",buildingId=2),
                    's1' : tblShelf(name="A-01", roomId=1),
                    's2' : tblShelf(name="A-02", roomId=1),
                    's3' : tblShelf(name="B-01", roomId=2),
                    's4' : tblShelf(name="B-02", roomId=2),
                    's5' : tblShelf(name="C-01", roomId=3),
                    's6' : tblShelf(name="C-02", roomId=3),
                    's7' : tblShelf(name="D-01", roomId=4),
                    's8' : tblShelf(name="D-02", roomId=4),
                    'v1' : tblManufacturer(name="IBM"),
                    'v2' : tblManufacturer(name="Cisco"),
                    'c1' : tblCategory(name="Server", description="server hardware"),
                    'c2' : tblCategory(name="Network", description="network hardware"),
                    'm1' : tblModelNumber(name="S100",description="100 class server", manufacturerId=1),
                    'm2' : tblModelNumber(name="S200",description="200 class server", manufacturerId=1),
                    'm3' : tblModelNumber(name="N100",description="100 class network switch", manufacturerId=2),
                    'm4' : tblModelNumber(name="N200",description="200 class network switch", manufacturerId=2),
                    'i1' : tblItem(poNumber="5", serialNumber="SN8", isPart=False, userId=1, categoryId=1, modelNumberId=1, manufacturerId=1, roomId=1, buildingId=1, shelfId=1),
                    'i2' : tblItem(poNumber="4", serialNumber="SN7", isPart=False, userId=1, categoryId=1, modelNumberId=2, manufacturerId=1, roomId=1, buildingId=1, shelfId=2),
                    'i3' : tblItem(poNumber="3", serialNumber="SN6", isPart=False, userId=1, categoryId=2, modelNumberId=3, manufacturerId=2, roomId=2, buildingId=1, shelfId=3),
                    'i4' : tblItem(poNumber="2", serialNumber="SN5", isPart=False, userId=1, categoryId=2, modelNumberId=4, manufacturerId=2, roomId=2, buildingId=1, shelfId=4),
                    'i5' : tblItem(poNumber="9", serialNumber="SN4", isPart=False, userId=1, categoryId=1, modelNumberId=1, manufacturerId=1, roomId=3, buildingId=2, shelfId=5),
                    'i6' : tblItem(poNumber="8", serialNumber="SN3", isPart=False, userId=1, categoryId=1, modelNumberId=2, manufacturerId=1, roomId=3, buildingId=2, shelfId=6),
                    'i7' : tblItem(poNumber="7", serialNumber="SN2", isPart=False, userId=1, categoryId=2, modelNumberId=3, manufacturerId=2, roomId=4, buildingId=2, shelfId=7),
                    'i8' : tblItem(poNumber="6", serialNumber="SN1", isPart=False, userId=2, categoryId=2, modelNumberId=4, manufacturerId=2, roomId=4, buildingId=2, shelfId=8)
                }                                                                 

    for k in testData:
        db.session.add(testData[k])
    db.session.commit()
    print("Database populated")    
    
