from sqlalchemy import event, desc, asc, and_, or_, create_engine
from sqlalchemy.sql import select, func, case
from sqlalchemy.engine import Engine
from sqlalchemy_utils import create_view
from sqlite3 import Connection as SQLite3Connection
import decimal
from dbmodel import *


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()
    
def populateDB(db):
    db.create_all()

    testData = {    
                    'admin' : tblUser(username="admin",email="a@b.com",password="password", isAdmin=True),
                    'user1' : tblUser(username="user1",email="aa@bb.com",password="password", isAdmin=False),
                    'ex1' : tblExchangeLkUp(name="NDAX",url="HTTPS://www.ndax.io"),
                    'fx1' : tblFxLkUp(name="Canada/USD",ticker="CAD",latestRate="0.78"),
                    'coin1' : tblCoinsLkUp(name="US Dollar",ticker="USD", isToken=False),
                    'coin2' : tblCoinsLkUp(name="Bitcoin",ticker="BTC", isToken=False),
                    'coin3' : tblCoinsLkUp(name="Ethereum",ticker="ETH", isToken=False),
                    'tx1' : tblTx(userId=1,buyCoinPrice=decimal.Decimal(700),buyCoinId=2,buyUnits=decimal.Decimal(2.0),fxRate=decimal.Decimal(1.0),fxId=1,exchangeId=1,txFees=decimal.Decimal(0),txNotes="first transaction"),
                    'txx' : tblTx(userId=1,buyCoinPrice=decimal.Decimal(300),buyCoinId=2,buyUnits=decimal.Decimal(2.0),fxRate=decimal.Decimal(1.0),fxId=1,exchangeId=1,txFees=decimal.Decimal(0)),
                    'tx2' : tblTx(userId=1,buyCoinPrice=decimal.Decimal(0),buyCoinId=2,buyUnits=decimal.Decimal(-2.0),fxRate=decimal.Decimal(1.0),fxId=1,exchangeId=1,txFees=decimal.Decimal(0)),
                    'txx2' : tblTx(userId=1,buyCoinPrice=decimal.Decimal(700),buyCoinId=2,buyUnits=decimal.Decimal(2.0),fxRate=decimal.Decimal(1.0),fxId=1,exchangeId=1,txFees=decimal.Decimal(0)),
                    'tx3' : tblTx(userId=1,buyCoinPrice=decimal.Decimal(800),buyCoinId=2,buyUnits=decimal.Decimal(2.0),fxRate=decimal.Decimal(1.0),fxId=1,exchangeId=1,txFees=decimal.Decimal(0)),
                    'tx4' : tblTx(userId=1,buyCoinPrice=decimal.Decimal(50),buyCoinId=3,buyUnits=decimal.Decimal(100.0),fxRate=decimal.Decimal(1.0),fxId=1,exchangeId=1,txFees=decimal.Decimal(0),txNotes="first transaction"),
                    'tx5' : tblTx(userId=1,buyCoinPrice=decimal.Decimal(30),buyCoinId=3,buyUnits=decimal.Decimal(60.0),fxRate=decimal.Decimal(1.0),fxId=1,exchangeId=1,txFees=decimal.Decimal(0)),
                    'tx6' : tblTx(userId=1,buyCoinPrice=decimal.Decimal(100),buyCoinId=3,buyUnits=decimal.Decimal(300.0),fxRate=decimal.Decimal(1.0),fxId=1,exchangeId=1,txFees=decimal.Decimal(0)),

                    'tx7' : tblTx(userId=2,buyCoinPrice=decimal.Decimal(100),buyCoinId=2,buyUnits=decimal.Decimal(10.0),fxRate=decimal.Decimal(1.0),fxId=1,exchangeId=1,txFees=decimal.Decimal(0),txNotes="first transaction"),
                    'tx8' : tblTx(userId=2,buyCoinPrice=decimal.Decimal(80),buyCoinId=2,buyUnits=decimal.Decimal(6.0),fxRate=decimal.Decimal(1.0),fxId=1,exchangeId=1,txFees=decimal.Decimal(0)),
                    'tx9' : tblTx(userId=2,buyCoinPrice=decimal.Decimal(50),buyCoinId=2,buyUnits=decimal.Decimal(30.0),fxRate=decimal.Decimal(1.0),fxId=1,exchangeId=1,txFees=decimal.Decimal(0)),
                    'tx10' : tblTx(userId=2,buyCoinPrice=decimal.Decimal(5),buyCoinId=3,buyUnits=decimal.Decimal(10.0),fxRate=decimal.Decimal(1.0),fxId=1,exchangeId=1,txFees=decimal.Decimal(0),txNotes="first transaction"),
                    'tx11' : tblTx(userId=2,buyCoinPrice=decimal.Decimal(3),buyCoinId=3,buyUnits=decimal.Decimal(6.0),fxRate=decimal.Decimal(1.0),fxId=1,exchangeId=1,txFees=decimal.Decimal(0)),
                    'tx12' : tblTx(userId=2,buyCoinPrice=decimal.Decimal(10),buyCoinId=3,buyUnits=decimal.Decimal(30.0),fxRate=decimal.Decimal(1.0),fxId=1,exchangeId=1,txFees=decimal.Decimal(0)),

                }                                                                 

    for k in testData:
        db.session.add(testData[k])
    db.session.commit()
    print("Database populated")

    # caseStmt = case( (tblTx.totalPrice > 0, tblTx.totalPrice), else_ = 0)
    # buyCountFilter = case( (tblTx.buyUnits > 0, 1), else_ = None)
    # q = db.session.query(tblTx, tblCoinsLkUp).filter_by(userId=1).join(tblCoinsLkUp, and_(tblTx.buyCoinId == tblCoinsLkUp.id)) \
    #     .with_entities(tblCoinsLkUp.name, tblCoinsLkUp.ticker, tblTx.buyCoinId, func.sum(tblTx.buyUnits), func.sum(caseStmt), func.count(buyCountFilter)).group_by(tblTx.buyCoinId).all()

    # for r in q:
    #     print(r)


    # # portfolio units held, grouped by coin for a given user
    # queryUnitsHeld = tblTx.query.filter_by(userId=1).with_entities(tblTx.buyCoinId, func.sum(tblTx.buyUnits), func.count(tblTx.buyUnits)).group_by(tblTx.buyCoinId).all()

    # queryAvgPrice = tblTx.query.filter_by(userId=1).order_by(desc(tblTx.buyCoinId)).with_entities(tblTx.buyCoinId,tblTx.buyCoinPrice,tblTx.buyUnits).all()
    
    #print(queryUnitsHeld)

    # coinIds = {}
    # for r in queryAvgPrice:
    #     if r[0] not in coinIds:
    #         coinIds[r[0]] = []
    #     coinIds[r[0]].append((r[1],r[2]))
    
    # print(coinIds)

    # for coinId in coinIds:
    #     sum = 0
    #     prodSum = 0
    #     for buyTx in coinIds[coinId]:
    #         sum += buyTx[1]
    #         prodSum += buyTx[0] * buyTx[1]
    #     print(f"CoinId: {coinId}, sum is: {sum}, product sum is: {prodSum}, weighted average is: {prodSum/sum}")
    
    #for a in queryAvgPrice:

def createViewPortfolio(userId, db, app_config):
    
    # create a view grouped by coin from transactions for a given user
    # only purchases are here, sales (ie negative buyUnits values) are excluded
    # includes aggregations for total units purchased, total USD invested, and number of buy transactions
    buyPricesFilter = case( (tblTx.totalPrice > 0, tblTx.totalPrice), else_ = 0)
    buyCountFilter = case( (tblTx.buyUnits > 0, 1), else_ = None)
    viewQuery = select([tblTx.buyCoinId, tblCoinsLkUp.name, tblCoinsLkUp.ticker, func.sum(tblTx.buyUnits).label('units')]) \
    .join(tblCoinsLkUp, and_(tblTx.buyCoinId == tblCoinsLkUp.id)) \
    .where(tblTx.userId==userId) \
    .group_by(tblTx.buyCoinId)

    # buyPricesFilter = case( (tblTx.totalPrice > 0, tblTx.totalPrice), else_ = 0)
    # buyCountFilter = case( (tblTx.buyUnits > 0, 1), else_ = None)
    # viewQuery = select([tblCoinsLkUp.name, tblCoinsLkUp.ticker, tblTx.buyCoinId, func.sum(tblTx.buyUnits).label('units'), func.sum(buyPricesFilter).label('invested'), func.count(buyCountFilter).label('buy tx count')]) \
    # .join(tblCoinsLkUp, and_(tblTx.buyCoinId == tblCoinsLkUp.id)) \
    # .where(tblTx.userId==userId) \
    # .group_by(tblTx.buyCoinId)    

    db_metadata = db.MetaData(bind=create_engine(app_config))
    viewPortfolio = create_view('viewPortfolio', viewQuery, db_metadata)
    db_metadata.create_all()
    return viewPortfolio

# # weighted average that ignores sales

# results =[ (2,700,4.0), (2,800,6.0), (2,800,-4.0), (2,600,10.0), (2,800,-6.0), (2,800,-2.0), (2,800,4.0), (2,300,2.0), (2,796,-2.0), (2,700,-2.0), (2,800,2.0), (3,7000,20.0), (3,3000,20.0), (3,7960,-20.0), (3,7000,20.0), (3,8000,20.0) ]

# for r in results:
# 	if r[0] not in coinStats:
# 		coinStats[r[0]] = []
# 	coinStats[r[0]].append(r[1],r[2])

# def wav(coinStats):	
# 	for coin in coinStats:
# 		unitSum = 0
# 		prodSum = 0
# 		tempUnits = 0
# 		saleFlag = False
		
# 		for buyTx in coinStats[coin]:
# 			if unitSum + buyTx[1] < 0:
# 				print("Less than 0 units, cannot reconcile accounts, exiting")
# 				break
# 			# if the current transaction is a purchase
# 			if buyTx[1] > 0:
# 				# if the previous transaction(s) was a sale
# 				# calculate the weighted average using the current purchase price and
# 				# the stored average price before sell transactions for units remaining after sales
# 				if saleFlag:
# 					prodSum = buyTx[0] * buyTx[1] + prodSum * tempUnits
# 					tempUnits = 0
# 					saleFlag = False
# 				# otherwise just keep the weighted average tally going
# 				else:
# 					prodSum += buyTx[0] * buyTx[1]
# 			# if the current transaction is a sale
# 			else:
# 				# if the previous transaction was not a sale
# 				if not saleFlag:
# 					if unitSum != 0:
#    					prodSum = prodSum / unitSum # store the average price thus far
#                   else:
#                       prodSum = 0
## 					saleFlag = True
# 				tempUnits = unitSum + buyTx[1]  # keep a count of how many units remain after sales
            
            # if all units have been sold, start tracking average again from 0
# 			if unitSum + buyTx[1] == 0:
# 				prodSum = 0
# 			unitSum += buyTx[1]
			
# 		print(f'Coin: {coin}, unitSum is {unitSum}, product sum is {prodSum}, weighted avg is {prodSum/unitSum}')
