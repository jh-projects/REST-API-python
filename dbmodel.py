from flask_sqlalchemy import SQLAlchemy
import datetime
from sqlalchemy.orm import validates
from dataclasses import dataclass
from werkzeug.security import generate_password_hash
db = SQLAlchemy()


@dataclass
class tblUser(db.Model):
    __tablename__ = 'user'
    
    #id : int
    username : str
    #email : str
    #password : str
    #isAdmin: bool
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    create_time = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())
    isAdmin = db.Column(db.Boolean, nullable=False, default=False)
    
    @validates('id', 'create_time')
    def _no_access(self, key, value):
        raise ValueError(f'Field {key} is not user-writable')

    @validates('password')
    def _create_password(self, key, value):
        return generate_password_hash(value, method="sha256")

    @validates('username', 'email')
    def _lowercase(self, key, value):
        return value.lower()
        
@dataclass
class tblItem(db.Model):
    __tablename__ = 'item'
    
    id : int
    poNumber : int
    serialNumber : str
    isPart : bool
    rcvdDate : datetime.datetime
    userId: int
    user : None
    categoryId : int
    category : None
    modelNumberId : int
    modelNumber : None
    manufacturerId : int
    manufacturer : None
    buildingId : int
    building : None
    roomId : int
    room : None
    shelfId : int
    shelf : None

    id = db.Column(db.Integer, primary_key=True)
    poNumber = db.Column(db.String(255), nullable=False)
    serialNumber = db.Column(db.String(255), unique=True, nullable=False)
    isPart = db.Column(db.Boolean, nullable=False)
    rcvdDate = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False )
    user = db.relationship("tblUser", backref=db.backref("user"))
    categoryId = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship("tblCategory", backref=db.backref("itemcategory"))
    modelNumberId = db.Column(db.Integer, db.ForeignKey('modelnumber.id'), nullable=False)
    modelNumber = db.relationship("tblModelNumber", backref=db.backref("itemmodel"))
    manufacturerId = db.Column(db.Integer, db.ForeignKey('manufacturer.id'), nullable=False)
    manufacturer = db.relationship("tblManufacturer", backref=db.backref("itemmanufacturer"))
    buildingId = db.Column(db.Integer, db.ForeignKey('building.id'), nullable=False)
    building = db.relationship("tblBuilding", backref=db.backref("itembuilding"))
    roomId = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)  
    room = db.relationship("tblRoom", backref=db.backref("itemroom"))
    shelfId = db.Column(db.Integer, db.ForeignKey('shelf.id'), nullable=False)
    shelf = db.relationship("tblShelf", backref=db.backref("itemshelf"))
    
    @validates('id', 'rcvdDate', 'user', 'category', 'modelNumber', 'manufacturer', 'building', 'room', 'shelf')
    def _no_access(self, key, value):
        raise ValueError(f'Field {key} is not user-writable')

    @validates('serialNumber','poNumber')
    def _uppercase(self, key, value):
        # put a prefix on PO numbers
        if key == 'poNumber' and value[:3].upper() != 'PO-':
            value = f'PO-{value}'

        return value.upper()



class tblPartQuantity(db.Model):
    __tablename__ = 'partquantity'
    id = db.Column(db.Integer, primary_key=True)
    itemId = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    

@dataclass
class tblCategory(db.Model):
    __tablename__ = 'category'
    
    id : int
    name : str
    description : str
    isActive : bool
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    isActive = db.Column(db.Boolean, nullable=False, default=True)

    @validates('id')
    def _no_access(self, key, value):
        raise ValueError(f'Field {key} is not user-writable')
        
    @validates('name')
    def _uppercase(self, key, value):
        return value.upper()

@dataclass
class tblModelNumber(db.Model):
    __tablename__ = 'modelnumber'
    
    id: int
    name: str
    description: str
    isActive : bool
    #categoryId : int
    #category: None
    manufacturerId : int
    manufacturer: None
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    isActive = db.Column(db.Boolean, nullable=False, default=True)
    description = db.Column(db.String(255), nullable=False)
    #categoryId = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    #category = db.relationship("tblCategory", backref=db.backref("modelcategory"))
    manufacturerId = db.Column(db.Integer, db.ForeignKey('manufacturer.id'), nullable=False)
    manufacturer = db.relationship("tblManufacturer", backref=db.backref("modelmanufacturer"))
    
    @validates('id', 'manufacturer') #'category',
    def _no_access(self, key, value):
        raise ValueError(f'Field {key} is not user-writable')

    @validates('name')
    def _uppercase(self, key, value):
        return value.upper()

@dataclass
class tblManufacturer(db.Model):
    __tablename__ = 'manufacturer'
    
    id : int
    name: str
    isActive : bool
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    isActive = db.Column(db.Boolean, nullable=False, default=True)
    
    @validates('id')
    def _no_access(self, key, value):
        raise ValueError(f'Field {key} is not user-writable')
    
    @validates('name')
    def _uppercase(self, key, value):
        return value.upper()


@dataclass
class tblBuilding(db.Model):
    __tablename__ = 'building'
    
    id: int
    name: str
    street: str
    city: str
    region: str
    country: str
    isActive : bool
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    street = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255), nullable=False)
    region = db.Column(db.String(255), nullable=False)
    country = db.Column(db.String(255), nullable=False)
    isActive = db.Column(db.Boolean, nullable=False, default=True)
    
    @validates('id')
    def _no_access(self, key, value):
        raise ValueError(f'Field {key} is not user-writable')

    @validates('name')
    def _uppercase(self, key, value):
        return value.upper()


@dataclass
class tblRoom(db.Model):
    __tablename__ = 'room'
    
    id : int
    name : str
    buildingId : int
    building : None
    isActive : bool
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    buildingId = db.Column(db.Integer, db.ForeignKey('building.id'), nullable=False)
    building = db.relationship("tblBuilding", backref=db.backref("roombuilding"))
    isActive = db.Column(db.Boolean, nullable=False, default=True)
    
    @validates('id', 'building')
    def _no_access(self, key, value):
        raise ValueError(f'Field {key} is not user-writable')

    @validates('name')
    def _uppercase(self, key, value):
        return value.upper()


@dataclass
class tblShelf(db.Model):
    __tablename__ = 'shelf'
    
    id : int
    name : str
    roomId : int
    room : None
    isActive : bool
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    roomId = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    room = db.relationship("tblRoom", backref=db.backref("shelfroom"))
    isActive = db.Column(db.Boolean, nullable=False, default=True)
    
    @validates('id', 'room')
    def _no_access(self, key, value):
        raise ValueError(f'Field {key} is not user-writable')

    @validates('name')
    def _uppercase(self, key, value):
        return value.upper()

