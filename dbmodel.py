from flask_sqlalchemy import SQLAlchemy
import datetime
from sqlalchemy.orm import validates, column_property
from dataclasses import dataclass
import decimal
from sqlalchemy import and_
from sqlalchemy.sql import func
import sqlalchemy as sa
from werkzeug.security import generate_password_hash
db = SQLAlchemy()


@dataclass
class tblUser(db.Model):
    __tablename__ = 'user'
    
    id : int
    username : str
    email : str
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
class tblTx(db.Model):
    __tablename__ = 'transactions'
    
    id : int
    userId: int
    txDate : datetime.datetime
    buyCoinPrice : decimal.Decimal
    sellCoinPrice : decimal.Decimal
    buyUnits: decimal.Decimal
    totalPrice: decimal.Decimal
    sellUnits: decimal.Decimal
    buyCoinId: int
    sellCoinId: int
    fxRate: decimal.Decimal
    txFees: decimal.Decimal
    txNotes: str
    exchangeId: int
    isTxSell: bool
    user: None
    buyCoin: None
    sellCoin: None
    fx: None
    exchange: None
    
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False )
    user = db.relationship("tblUser", backref=db.backref("users"))
    txDate = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())
    buyCoinPrice = db.Column(db.Float(precision=18, asdecimal=True, decimal_return_scale=8), nullable=False)
    sellCoinPrice = db.Column(db.Float(precision=18, asdecimal=True, decimal_return_scale=8), default=1.0)
    buyUnits = db.Column(db.Float(precision=18, asdecimal=True, decimal_return_scale=8), nullable=False)
    sellUnits = db.Column(db.Float(precision=18, asdecimal=True, decimal_return_scale=8), nullable=False, default=0)
    totalPrice = column_property(buyCoinPrice * buyUnits / sellCoinPrice)
    #totalPrice = db.Column(db.Float(precision=18, asdecimal=True, decimal_return_scale=8), nullable=True)
    buyCoinId = db.Column(db.Integer, db.ForeignKey('coins.id'), nullable=False )
    buyCoin = db.relationship("tblCoinsLkUp", backref=db.backref("buyCoins"), foreign_keys=[buyCoinId])
    sellCoinId = db.Column(db.Integer, db.ForeignKey('coins.id'), nullable=False, default=1 )
    sellCoin = db.relationship("tblCoinsLkUp", backref=db.backref("sellCoins"), foreign_keys=[sellCoinId])
    fxId = db.Column(db.Integer, db.ForeignKey('fx.id'), nullable=True )
    fx = db.relationship("tblFxLkUp", backref=db.backref("fx"))
    fxRate = db.Column(db.Float(precision=18, asdecimal=True, decimal_return_scale=8), nullable=False)
    txFees = db.Column(db.Float(precision=18, asdecimal=True, decimal_return_scale=8), nullable=False)
    txNotes = db.Column(db.String(512), nullable=True)
    exchangeId = db.Column(db.Integer, db.ForeignKey('exchanges.id'), nullable=True )
    exchange = db.relationship("tblExchangeLkUp", backref=db.backref("exchanges"))
    isTxSell = db.Column(db.Boolean, nullable=False, default=False)
    
    @validates('id', 'user', 'buyCoin', 'sellCoin', 'fx', 'exchange')
    def _no_access(self, key, value):
        raise ValueError(f'Field {key} is not user-writable')

    # @validates('sellCoinPrice')
    # def _setDefault(self,key,value):
    #     return 1

@dataclass
class tblPortfolio(db.Model):
    __tablename__ = 'portfolio'
    
    id: int
    userId: int
    coinId: int
    # firstTxDate : datetime.datetime
    # lastTxDate : datetime.datetime
    unitsHeld: decimal.Decimal
    numBuyTx: int
    numSellTx: int
    user: None
    coin: None
    
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False )
    user = db.relationship("tblUser", backref=db.backref("user"))
    coinId = db.Column(db.Integer, db.ForeignKey('coins.id'), nullable=False )
    coin = db.relationship("tblCoinsLkUp", backref=db.backref("coins"))
    #firstTxDate = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())
    #lastTxDate = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())
    unitsHeld = db.Column(db.Float(precision=18, asdecimal=True, decimal_return_scale=8), nullable=False)
    numBuyTx = db.Column(db.Integer, nullable=False, default=1)
    numSellTx = db.Column(db.Integer, nullable=False, default=0)

    @validates('id', 'user', 'coin')
    def _no_access(self, key, value):
        raise ValueError(f'Field {key} is not user-writable')

    @validates('numBuyTx')
    def _incrementBuyTx(self, key, value):
        if self.numBuyTx > 0:
            return self.numBuyTx + 1
        return 1


@dataclass
class tblCoinsLkUp(db.Model):
    __tablename__ = 'coins'
    
    id: int
    name: str
    ticker: str
    isToken : bool
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    ticker = db.Column(db.String(10), nullable=False)
    isToken = db.Column(db.Boolean, nullable=False, default=False)

    @validates('id')
    def _no_access(self, key, value):
        raise ValueError(f'Field {key} is not user-writable')

    @validates('name')
    def _capitalize(self, key, value):
        return value.capitalize()

    @validates('ticker')
    def _uppercase(self, key, value):
        return value.upper()


@dataclass
class tblExchangeLkUp(db.Model):
    __tablename__ = 'exchanges'
    
    id: int
    name: str
    url: str
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=True)
    
    @validates('id')
    def _no_access(self, key, value):
        raise ValueError(f'Field {key} is not user-writable')

    @validates('name')
    def _capitalize(self, key, value):
        return value.capitalize()

    @validates('url')
    def _uppercase(self, key, value):
        return value.lower()


@dataclass
class tblFxLkUp(db.Model):
    __tablename__ = 'fx'
    
    id: int
    name: str
    ticker: str
    latestRate: decimal.Decimal
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    ticker = db.Column(db.String(10), nullable=False)
    latestRate = db.Column(db.Float(precision=18, asdecimal=True, decimal_return_scale=6), nullable=False)

    
    @validates('id')
    def _no_access(self, key, value):
        raise ValueError(f'Field {key} is not user-writable')


    @validates('url')
    def _uppercase(self, key, value):
        return value.lower()

