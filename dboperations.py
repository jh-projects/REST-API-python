from concurrent.futures import thread
from sqlalchemy import event, desc, asc, and_, or_, create_engine
from sqlalchemy.sql import select, func, case
from sqlalchemy.engine import Engine
from sqlalchemy_utils import create_view
from sqlite3 import Connection as SQLite3Connection
import decimal
import time, requests, threading
from dbmodel import *

# only used
RUN_ONCE_FLAG = False

# top 100 coins by market cap from CoinGecko as of May 2022
coinList = [{'id': 'bitcoin', 'ticker': 'btc'}, {'id': 'ethereum', 'ticker': 'eth'}, {'id': 'tether', 'ticker': 'usdt'}, {'id': 'binancecoin', 'ticker': 'bnb'}, {'id': 'usd-coin', 'ticker': 'usdc'}, {'id': 'ripple', 'ticker': 'xrp'}, {'id': 'solana', 'ticker': 'sol'}, {'id': 'cardano', 'ticker': 'ada'}, {'id': 'terra-luna', 'ticker': 'luna'}, {'id': 'terrausd', 'ticker': 'ust'}, {'id': 'binance-usd', 'ticker': 'busd'}, {'id': 'dogecoin', 'ticker': 'doge'}, {'id': 'polkadot', 'ticker': 'dot'}, {'id': 'avalanche-2', 'ticker': 'avax'}, {'id': 'staked-ether', 'ticker': 'steth'}, {'id': 'wrapped-bitcoin', 'ticker': 'wbtc'}, {'id': 'shiba-inu', 'ticker': 'shib'}, {'id': 'tron', 'ticker': 'trx'}, {'id': 'near', 'ticker': 'near'}, {'id': 'dai', 'ticker': 'dai'}, {'id': 'litecoin', 'ticker': 'ltc'}, {'id': 'matic-network', 'ticker': 'matic'}, {'id': 'crypto-com-chain', 'ticker': 'cro'}, {'id': 'leo-token', 'ticker': 'leo'}, {'id': 'bonded-luna', 'ticker': 'bluna'}, {'id': 'bitcoin-cash', 'ticker': 'bch'}, {'id': 'algorand', 'ticker': 'algo'}, {'id': 'ftx-token', 'ticker': 'ftt'}, {'id': 'chainlink', 'ticker': 'link'}, {'id': 'cosmos', 'ticker': 'atom'}, {'id': 'okb', 'ticker': 'okb'}, {'id': 'stellar', 'ticker': 'xlm'}, {'id': 'monero', 'ticker': 'xmr'}, {'id': 'ethereum-classic', 'ticker': 'etc'}, {'id': 'apecoin', 'ticker': 'ape'}, {'id': 'uniswap', 'ticker': 'uni'}, {'id': 'vechain', 'ticker': 'vet'}, {'id': 'frax', 'ticker': 'frax'}, {'id': 'internet-computer', 'ticker': 'icp'}, {'id': 'hedera-hashgraph', 'ticker': 'hbar'}, {'id': 'filecoin', 'ticker': 'fil'}, {'id': 'elrond-erd-2', 'ticker': 'egld'}, {'id': 'the-sandbox', 'ticker': 'sand'}, {'id': 'magic-internet-money', 'ticker': 'mim'}, {'id': 'axie-infinity', 'ticker': 'axs'}, {'id': 'tezos', 'ticker': 'xtz'}, {'id': 'defichain', 'ticker': 'dfi'}, {'id': 'compound-ether', 'ticker': 'ceth'}, {'id': 'the-graph', 'ticker': 'grt'}, {'id': 'theta-token', 'ticker': 'theta'}, {'id': 'pancakeswap-token', 'ticker': 'cake'}, {'id': 'theta-fuel', 'ticker': 'tfuel'}, {'id': 'eos', 'ticker': 'eos'}, {'id': 'decentraland', 'ticker': 'mana'}, {'id': 'klay-token', 'ticker': 'klay'}, {'id': 'aave', 'ticker': 'aave'}, {'id': 'thorchain', 'ticker': 'rune'}, {'id': 'fantom', 'ticker': 'ftm'}, {'id': 'compound-usd-coin', 'ticker': 'cusdc'}, {'id': 'kucoin-shares', 'ticker': 'kcs'}, {'id': 'waves', 'ticker': 'waves'}, {'id': 'flow', 'ticker': 'flow'}, {'id': 'bittorrent', 'ticker': 'btt'}, {'id': 'chain-2', 'ticker': 'xcn'}, {'id': 'stepn', 'ticker': 'gmt'}, {'id': 'huobi-token', 'ticker': 'ht'}, {'id': 'frax-share', 'ticker': 'fxs'}, {'id': 'zcash', 'ticker': 'zec'}, {'id': 'true-usd', 'ticker': 'tusd'}, {'id': 'huobi-btc', 'ticker': 'hbtc'}, {'id': 'helium', 'ticker': 'hnt'}, {'id': 'bitcoin-cash-sv', 'ticker': 'bsv'}, {'id': 'ecash', 'ticker': 'xec'}, {'id': 'convex-finance', 'ticker': 'cvx'}, {'id': 'iota', 'ticker': 'miota'}, {'id': 'osmosis', 'ticker': 'osmo'}, {'id': 'quant-network', 'ticker': 'qnt'}, {'id': 'radix', 'ticker': 'xrd'}, {'id': 'neo', 'ticker': 'neo'}, {'id': 'zilliqa', 'ticker': 'zil'}, {'id': 'cdai', 'ticker': 'cdai'}, {'id': 'nexo', 'ticker': 'nexo'}, {'id': 'maker', 'ticker': 'mkr'}, {'id': 'paxos-standard', 'ticker': 'usdp'}, {'id': 'celo', 'ticker': 'celo'}, {'id': 'kusama', 'ticker': 'ksm'}, {'id': 'gala', 'ticker': 'gala'}, {'id': 'arweave', 'ticker': 'ar'}, {'id': 'neutrino', 'ticker': 'usdn'}, {'id': 'gatechain-token', 'ticker': 'gt'}, {'id': 'bitdao', 'ticker': 'bit'}, {'id': 'havven', 'ticker': 'snx'}, {'id': 'dash', 'ticker': 'dash'}, {'id': 'curve-dao-token', 'ticker': 'crv'}, {'id': 'amp-token', 'ticker': 'amp'}, {'id': 'enjincoin', 'ticker': 'enj'}, {'id': 'chiliz', 'ticker': 'chz'}, {'id': 'harmony', 'ticker': 'one'}, {'id': 'compound-usdt', 'ticker': 'cusdt'}, {'id': 'blockstack', 'ticker': 'stx'}]

# API key for https://free.currencyconverterapi.com/
FX_API_KEY = '3156eed224a726430a08'
fxPairs = [('USD_CAD', {'name': 'Canadian Dollar', 'id': 1}), ('USD_GBP', {'name': 'British Pounds', 'id': 2}), ('USD_EUR', {'name': 'Euros', 'id':3})]

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
                    'ex1' : tblExchanges(name="NDAX",url="HTTPS://www.ndax.io"),
                    'coin1' : tblCoins(name="US Dollar",ticker="USD"),
                    # 'tx1' : tblTx(userId=1,isTxSell=False,buyCoinPrice=decimal.Decimal(700),buyCoinId=2,buyUnits=decimal.Decimal(2.0),fxRate=decimal.Decimal(1.0),fxId=1,exchangeId=1,txFees=decimal.Decimal(0),txNotes="first transaction"),
                    # 'txx' : tblTx(userId=1,isTxSell=False,buyCoinPrice=decimal.Decimal(300),buyCoinId=2,buyUnits=decimal.Decimal(2.0),fxRate=decimal.Decimal(1.0),fxId=1,exchangeId=1,txFees=decimal.Decimal(0)),
                    # 'tx2' : tblTx(userId=1,isTxSell=True,buyCoinPrice=decimal.Decimal(50),buyCoinId=2,buyUnits=decimal.Decimal(-2.0),fxRate=decimal.Decimal(1.0),fxId=1,exchangeId=1,txFees=decimal.Decimal(0)),
                    # 'txx2' : tblTx(userId=1,isTxSell=False,buyCoinPrice=decimal.Decimal(700),buyCoinId=2,buyUnits=decimal.Decimal(2.0),fxRate=decimal.Decimal(1.0),fxId=1,exchangeId=1,txFees=decimal.Decimal(0)),
                    # 'tx3' : tblTx(userId=1,isTxSell=False,buyCoinPrice=decimal.Decimal(800),buyCoinId=2,buyUnits=decimal.Decimal(2.0),fxRate=decimal.Decimal(1.0),fxId=1,exchangeId=1,txFees=decimal.Decimal(0)),
                    # 'tx4' : tblTx(userId=1,isTxSell=False,buyCoinPrice=decimal.Decimal(50),buyCoinId=3,buyUnits=decimal.Decimal(100.0),fxRate=decimal.Decimal(1.0),fxId=1,exchangeId=1,txFees=decimal.Decimal(0),txNotes="first transaction"),
                    # 'tx5' : tblTx(userId=1,isTxSell=False,buyCoinPrice=decimal.Decimal(30),buyCoinId=3,buyUnits=decimal.Decimal(60.0),fxRate=decimal.Decimal(1.0),fxId=1,exchangeId=1,txFees=decimal.Decimal(0)),
                    # 'tx6' : tblTx(userId=1,isTxSell=False,buyCoinPrice=decimal.Decimal(100),buyCoinId=3,buyUnits=decimal.Decimal(300.0),fxRate=decimal.Decimal(1.0),fxId=1,exchangeId=1,txFees=decimal.Decimal(0)),

                    # 'tx7' : tblTx(userId=2,buyCoinPrice=decimal.Decimal(100),buyCoinId=2,buyUnits=decimal.Decimal(10.0),fxRate=decimal.Decimal(1.0),fxId=1,exchangeId=1,txFees=decimal.Decimal(0),txNotes="first transaction"),
                    # 'tx8' : tblTx(userId=2,buyCoinPrice=decimal.Decimal(80),buyCoinId=2,buyUnits=decimal.Decimal(6.0),fxRate=decimal.Decimal(1.0),fxId=1,exchangeId=1,txFees=decimal.Decimal(0)),
                    # 'tx9' : tblTx(userId=2,buyCoinPrice=decimal.Decimal(50),buyCoinId=2,buyUnits=decimal.Decimal(30.0),fxRate=decimal.Decimal(1.0),fxId=1,exchangeId=1,txFees=decimal.Decimal(0)),
                    # 'tx10' : tblTx(userId=2,buyCoinPrice=decimal.Decimal(5),buyCoinId=3,buyUnits=decimal.Decimal(10.0),fxRate=decimal.Decimal(1.0),fxId=1,exchangeId=1,txFees=decimal.Decimal(0),txNotes="first transaction"),
                    # 'tx11' : tblTx(userId=2,buyCoinPrice=decimal.Decimal(3),buyCoinId=3,buyUnits=decimal.Decimal(6.0),fxRate=decimal.Decimal(1.0),fxId=1,exchangeId=1,txFees=decimal.Decimal(0)),
                    # 'tx12' : tblTx(userId=2,buyCoinPrice=decimal.Decimal(10),buyCoinId=3,buyUnits=decimal.Decimal(30.0),fxRate=decimal.Decimal(1.0),fxId=1,exchangeId=1,txFees=decimal.Decimal(0)),

                }                                                                 

    for k in testData:
        db.session.add(testData[k])

    # create initial FX pair entries, rates will be ingested later
    fxp = tblFx(id=0, name='USD', ticker='USD_USD', latestRate=1.0)
    db.session.add(fxp)
    for fxPair in fxPairs:
        fxp = tblFx(id=fxPair[1]['id'], name=fxPair[1]['name'], ticker=fxPair[0], latestRate=1.0)
        db.session.add(fxp)

    for coin in coinList:
        c = tblCoins(name=coin['id'].capitalize(), ticker=coin['ticker'])
        db.session.add(c)

    fxUpdateThread = threading.Thread(target=updateFxRates, args=[db], daemon=True)
    fxUpdateThread.start()

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
    
# ingest FX Pair rates and update table
def updateFxRates(app, db):

    with app.app_context():

        RATE_UPDATE = 3700

        while True:
            print('Updating FX...')
            for fxPair in fxPairs:
                response = requests.get(f'https://free.currconv.com/api/v7/convert?q={fxPair[0]}&compact=ultra&apiKey=3156eed224a726430a08')
                if response.status_code == 200:
                    fxRate = response.json()[fxPair[0]]
                    fxRecord = tblFx.query.filter_by(id=fxPair[1]['id']).first()
                    fxRecord.latestRate = decimal.Decimal(fxRate)
                    db.session.add(fxRecord)
                else:
                    print("Error communicating with FX API")
            db.session.commit()
            time.sleep(RATE_UPDATE)


def updatePortfolio(user, data):
            portfolioRecord = tblPortfolio.query.filter_by(userId=user, coinId=data['buyCoinId']).first()

            data['fxRate'] = 1.0 if 'fxRate' not in data else decimal.Decimal(data['fxRate'])
            data['buyUnits'] = decimal.Decimal(data['buyUnits'])
            data['buyCoinPrice'] = decimal.Decimal(data['buyCoinPrice'])

            # when buying a new type of asset
            if portfolioRecord == None:
                if data['buyUnits'] <= 0:
                    print(f"Portfolio contains 0 units, cannot sell {data['buyUnits']}")
                    return False
                portfolioRecord =  tblPortfolio()
                portfolioRecord.userId = user
                portfolioRecord.coinId = data['buyCoinId']                    
                portfolioRecord.unitsHeld = data['buyUnits']
                portfolioRecord.numBuyTx = 1
                portfolioRecord.numSellTx = 0
                portfolioRecord.totalInvestmentUSD = data['buyUnits'] * data['buyCoinPrice']
                portfolioRecord.totalInvestmentFx = data['buyUnits'] * data['buyCoinPrice'] * data['fxRate']

            # when buying or selling an existing asset
            else:
                if portfolioRecord._isActive == False:
                    portfolioRecord._isActive = True

                if data['buyUnits'] < 0:
                    if portfolioRecord.unitsHeld + data['buyUnits'] == 0:
                        portfolioRecord._isActive = False

                    if portfolioRecord.unitsHeld + data['buyUnits'] < 0:
                        print(f"Portfolio contains {portfolioRecord.unitsHeld} units, cannot sell {data['buyUnits']}")
                        return False
                    portfolioRecord.numSellTx += 1
                else: 
                    portfolioRecord.numBuyTx += 1 
                portfolioRecord.totalInvestmentUSD += data['buyUnits'] * data['buyCoinPrice']
                portfolioRecord.totalInvestmentFx += data['buyUnits'] * data['buyCoinPrice'] * data['fxRate']
                portfolioRecord.unitsHeld += data['buyUnits']
            
            return portfolioRecord
            

def createViewPortfolio(userId, db, app_config):
    
    # create a view grouped by coin from transactions for a given user
    # only purchases are here, sales (ie negative buyUnits values) are excluded
    # includes aggregations for total units purchased, total USD invested, and number of buy transactions
    buyPricesFilter = case( (tblTx.totalPrice > 0, tblTx.totalPrice), else_ = 0)
    buyCountFilter = case( (tblTx.buyUnits > 0, 1), else_ = None)
    viewQuery = select([tblTx.buyCoinId, tblCoins.name, tblCoins.ticker, func.sum(tblTx.buyUnits).label('units')]) \
    .join(tblCoins, and_(tblTx.buyCoinId == tblCoins.id)) \
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
		
# 		for tx in coinStats[coin]:
# 			if unitSum + tx[1] < 0:
# 				print("Less than 0 units, cannot reconcile accounts, exiting")
# 				break
# 			# if the current transaction is a purchase
# 			if tx[1] > 0:
# 				# if the previous transaction(s) was a sale
# 				# calculate the weighted average using the current purchase price and
# 				# the stored average price before sell transactions for units remaining after sales
# 				if saleFlag:
# 					prodSum = tx[0] * tx[1] + prodSum * tempUnits
# 					tempUnits = 0
# 					saleFlag = False
# 				# otherwise just keep the weighted average tally going
# 				else:
# 					prodSum += tx[0] * tx[1]
# 			# if the current transaction is a sale
# 			else:
# 				# if the previous transaction was not a sale
# 				if not saleFlag:
# 					if unitSum != 0:
#    					prodSum = prodSum / unitSum # store the average price thus far
# 					saleFlag = True
# 				tempUnits = unitSum + tx[1]  # keep a count of how many units remain after sales
            
            # if all units have been sold, start tracking average again from 0
# 			if unitSum + tx[1] == 0:
# 				prodSum = 0
# 			unitSum += tx[1]
			
# 		print(f'Coin: {coin}, unitSum is {unitSum}, product sum is {prodSum}, weighted avg is {prodSum/unitSum}')
