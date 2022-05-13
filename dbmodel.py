from flask_sqlalchemy import SQLAlchemy
import datetime
from sqlalchemy.orm import validates, column_property
from dataclasses import dataclass
import decimal
from sqlalchemy import and_, column
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
    txDateTime : datetime.datetime
    buyCoinPrice : decimal.Decimal
    sellCoinPrice : decimal.Decimal
    buyUnits: decimal.Decimal
    sellUnits: decimal.Decimal
    buyCoinId: int
    sellCoinId: int
    fxRate: decimal.Decimal
    txFees: decimal.Decimal
    txNotes: str
    exchangeId: int
    totalPriceUSD: decimal.Decimal
    totalPriceFx: decimal.Decimal
    user: None
    buyCoin: None
    sellCoin: None
    fx: None
    exchange: None
    
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False )
    user = db.relationship("tblUser", backref=db.backref("users"))
    txDateTime = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())
    buyCoinPrice = db.Column(db.Float(precision=18, asdecimal=True, decimal_return_scale=8), nullable=False)
    sellCoinPrice = db.Column(db.Float(precision=18, asdecimal=True, decimal_return_scale=8), nullable=False, default=1.0)
    buyUnits = db.Column(db.Float(precision=18, asdecimal=True, decimal_return_scale=8), nullable=False)
    sellUnits = db.Column(db.Float(precision=18, asdecimal=True, decimal_return_scale=8), nullable=False)
    fxRate = db.Column(db.Float(precision=18, asdecimal=True, decimal_return_scale=8), nullable=False, default=1.0)
    totalPriceUSD = column_property( buyCoinPrice * buyUnits)
    totalPriceFx = column_property( buyCoinPrice * buyUnits * fxRate)
    buyCoinId = db.Column(db.Integer, db.ForeignKey('coins.id'), nullable=False )
    buyCoin = db.relationship("tblCoins", backref=db.backref("buyCoins"), foreign_keys=[buyCoinId])
    sellCoinId = db.Column(db.Integer, db.ForeignKey('coins.id'), nullable=False, default=1)
    sellCoin = db.relationship("tblCoins", backref=db.backref("sellCoins"), foreign_keys=[sellCoinId])
    fxId = db.Column(db.Integer, db.ForeignKey('fx.id'), nullable=False, default=1)
    fx = db.relationship("tblFx", backref=db.backref("fx"))
    txFees = db.Column(db.Float(precision=18, asdecimal=True, decimal_return_scale=8), nullable=False)
    txNotes = db.Column(db.String(512), nullable=True)
    exchangeId = db.Column(db.Integer, db.ForeignKey('exchanges.id'), nullable=True )
    exchange = db.relationship("tblExchanges", backref=db.backref("exchanges"))

    
    @validates('id', 'user', 'buyCoin', 'sellCoin', 'fx', 'exchange')
    def _no_access(self, key, value):
        raise ValueError(f'Field {key} is not user-writable')

    @validates('sellUnits', 'buyUnits', 'sellCoinPrice', 'fxRate', 'buyCoinPrice', 'txFees')
    def _set_decimals(self, key, value):
        value = decimal.Decimal(value)
        return value

    @validates('txDateTime')
    def _set_tx_datetime(self,key,value):
        print(f' here {value}')
        return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')       


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
    _isActive: None
    totalInvestmentUSD: decimal.Decimal
    totalInvestmentFx: decimal.Decimal
    user: None
    coin: None

    
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False )
    user = db.relationship("tblUser", backref=db.backref("user"))
    coinId = db.Column(db.Integer, db.ForeignKey('coins.id'), nullable=False )
    coin = db.relationship("tblCoins", backref=db.backref("coins"))
    #firstTxDate = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())
    #lastTxDate = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())
    unitsHeld = db.Column(db.Float(precision=18, asdecimal=True, decimal_return_scale=8), nullable=False)
    totalInvestmentUSD = db.Column(db.Float(precision=18, asdecimal=True, decimal_return_scale=8), nullable=False)
    totalInvestmentFx = db.Column(db.Float(precision=18, asdecimal=True, decimal_return_scale=8), nullable=False)
    #totalInvestmentFx = db.Column(db.Float(precision=18, asdecimal=True, decimal_return_scale=8), nullable=False)
    numBuyTx = db.Column(db.Integer, nullable=False, default=1)
    numSellTx = db.Column(db.Integer, nullable=False, default=0)
    _isActive = db.Column(db.Boolean, nullable=False, default=True)

    @validates('id', 'user', 'coin')
    def _no_access(self, key, value):
        raise ValueError(f'Field {key} is not user-writable')

    @validates('unitsHeld','totalInvestmentUSD')
    def _no_negative_values(self,key,value):
        if value < 0:
            raise ValueError(f'Field {key} cannot be < 0')
        return value


@dataclass
class tblCoins(db.Model):
    __tablename__ = 'coins'
    
    id: int
    name: str
    ticker: str
    #isToken : bool
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    ticker = db.Column(db.String(10), nullable=False, unique=True)
    #isToken = db.Column(db.Boolean, nullable=False, default=False)

    @validates('id')
    def _no_access(self, key, value):
        raise ValueError(f'Field {key} is not user-writable')


    @validates('ticker')
    def _uppercase(self, key, value):
        return value.upper()


@dataclass
class tblExchanges(db.Model):
    __tablename__ = 'exchanges'
    
    id: int
    name: str
    url: str
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
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
class tblFx(db.Model):
    __tablename__ = 'fx'
    
    id: int
    name: str
    ticker: str
    latestRate: decimal.Decimal
    isActive: bool
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    ticker = db.Column(db.String(10), nullable=False, unique=True)
    latestRate = db.Column(db.Float(precision=18, asdecimal=True, decimal_return_scale=6), nullable=False)
    isActive = db.Column(db.Boolean, nullable=False, default=True)
    
    # @validates('id')
    # def _no_access(self, key, value):
    #     raise ValueError(f'Field {key} is not user-writable')


    @validates('url')
    def _uppercase(self, key, value):
        return value.lower()

