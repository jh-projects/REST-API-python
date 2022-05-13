from flask import Flask, jsonify, request, abort, make_response
from flask_cors import CORS
from werkzeug.security import check_password_hash
from werkzeug.exceptions import HTTPException
import jwt
from functools import wraps
import datetime
from sqlalchemy import exc
from sqlalchemy.orm import exc as exc2
import os
import threading
from dboperations import createViewPortfolio, populateDB, updatePortfolio, updateFxRates
import dbmodel
from dbmodel import *

# create a dictionary with all the DB tables for use with routing operations, minus the user table
dbTablesMap = {t.lower().removeprefix("tbl") : eval(t) for t in dir(dbmodel) if t.startswith("tbl") and (t != 'tblUser' or t != 'tblPortfolio')}

def create_app():

    app = Flask("app")
    app.secret_key = "keepmeasecret"
    app.config['DEBUG'] = True

    # ******** FOR DEBUGGING
    # for clearing DB on restarts - deletes DB file before rebuilding
    # so that unique keys don't cause errors
    if os.path.exists('cryptofolio.db'):
        os.remove('cryptofolio.db')


    # database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cryptofolio.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_ECHO'] = False

    # required to make SQLAlchemy and Flask work together
    with app.app_context():

        CORS(app)   # process CORS mode requests silently
        db.init_app(app)
        populateDB(db)
        fxUpdateThread = threading.Thread(target=updateFxRates, args=(app, db), daemon=True)
        fxUpdateThread.start()
        
    # validates JWT token for authenticating REST API
    def validate_token(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            
            token = None
            if request.method == "OPTIONS": # CORS preflight handling
                response = make_response()
                response.headers.add("Access-Control-Allow-Origin", "*")
                response.headers.add('Access-Control-Allow-Headers', "*")
                response.headers.add('Access-Control-Allow-Methods', "*")
                return response
           
            #TESTING ONLY **************** * bypasses token validation and grants admin access to anyone
            return f(1, *args, **kwargs)
            
            if 'x-access-tokens' in request.headers:
                token = request.headers['x-access-tokens']
            if not token:
                abort(make_response({'data': { 'id' : 400, 'message' : 'token is missing'}}, 400))
            try:
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
                current_user = tblUser.query.filter_by(id=data['id']).first().id
            except:
                abort(make_response({'data': { 'id' : 401, 'message' : 'token is invalid'}}, 401))

            # sends back the user ID embedded in the token for gating access to API operations as needed
            return f(current_user, *args, **kwargs)
            
        return decorator
       

    @app.errorhandler(400)
    def bad_request(e):
        print(e)
        return jsonify(error=str(e)), 400


    @app.errorhandler(401)
    def unauthorized(e):
        print(e)
        return jsonify(error=str(e)), 401

    @app.errorhandler(403)
    def forbidden(e):
        print(e)
        return jsonify(error=str(e)), 403
        
    @app.errorhandler(404)
    def resource_not_found(e):
        print(e)
        return jsonify(error=str(e)), 404

    # used for trying to add a record that already exists
    @app.errorhandler(409)
    def resource_conflict(e):
        print(e)
        return jsonify(error=str(e)), 409

    @app.errorhandler(500)
    def server_error(e):
        print(e)
        return jsonify(error=str(e)), 500
        

    # login method
    @app.route("/api/login", methods=['POST'])
    def login():
       
        data = request.json
        user = tblUser.query.filter_by(username=data['username']).first()

        # invalid username/password check
        if not user or not check_password_hash(user.password, data['password']):
            abort(make_response({'data': { 'id' : 401, 'message' : 'bad username/password'}}, 401))

        # create API token and give back to client
        token = jwt.encode({'id' : user.id, 'exp' : datetime.datetime.now() + datetime.timedelta(minutes=1440)}, app.config['SECRET_KEY'], "HS256")
        response = jsonify( {'data' : { 'id' : 200, 'message' : 'logged in as ' + data['username'], 'token' : token }} )
        return response


    # add a new user for API access
    @app.route("/api/adduser/", methods=['POST'])
    @validate_token
    def add_user(current_user):
        data = request.json
        
        # only allow admin users to add new users
        if ( db.session.query(tblUser.isAdmin).filter(tblUser.id==current_user).first()[0] ):

            try:
                newUser = tblUser()
                setattr(newUser, "email", data['email'])
                setattr(newUser, "username", data['username'])
                setattr(newUser, "password", data['password'])
                setattr(newUser, "isAdmin", data['isAdmin'])
                db.session.add(newUser)
                db.session.commit()

                return jsonify({'data': { 'id' : 201, 'message' : f'user {data["username"]} added'}}), 201
            
            except exc.SQLAlchemyError as e:
                print(e)
                db.session.rollback()
                abort(make_response({'data': { 'id' : 400, 'message' : 'client error, user not added'}}, 400))
            except BaseException as e:
                print(e)
                db.session.rollback()
                abort(make_response({'data': { 'id' : 500, 'message' : 'server error, user not added'}}, 500))

        abort(make_response({'data': { 'id' : 403, 'message' : 'access denied to non-admin users'}}, 403))
            

    # list operations
    # allows listing of all items in an entity, or a single item retrieved by an id
    @app.route("/api/list/<entity>/", methods=['GET'])
    @app.route("/api/list/<entity>/<id>", methods=['GET'])
    @validate_token
    def list_entity(current_user, entity, id=None):
        r = None
        try:
            entity = entity.lower()
            
            # code to create and return portfolio view
            # viewPortfolio = createViewPortfolio(current_user, db, app.config['SQLALCHEMY_DATABASE_URI'])
            # x = db.session.query(viewPortfolio)
            # for r in x:
            #     print(r)

            # for searching items records, search single items by serial number
            if entity == "tx":
                    r = tblTx.query.filter_by(userId=current_user).all()

            # for searching lookup table records
            elif entity in dbTablesMap and entity != "tx":
                if id !=None: # use table ID when searching single records
                    r = dbTablesMap[entity].query.filter_by(id=id, isActive=True).first()
                else:
                    r = dbTablesMap[entity].query.filter_by(isActive=True).all()

        except exc.SQLAlchemyError as e:
            print(e)
            abort(make_response({'data': { 'id' : 400, 'message' : 'client error, list failed'}}, 400))
        except BaseException as e:
            print(e)
            abort(make_response({'data': { 'id' : 500, 'message' : 'server error, list failed'}}, 500))

        # catch queries where no record matched search criteria
        if r == None:
            abort(make_response({'data': { 'id' : 404, 'message' : f'{entity}{"/" + id if id != None else ""} record not found'}}, 404))
            
        response = jsonify({'data': { 'id': 200, 'message':r}})
        return response


    # add a new record to an entity
    @app.route("/api/add/<entity>/", methods=['POST'])
    @validate_token
    def add_record(current_user, entity):
        data = request.json
        try:
        
            entity = entity.lower()
     
            if entity in dbTablesMap:

                newRecord = dbTablesMap[entity]()
                # get the fields available for modification in the record using the dataclass attributes
                # dataclass for relationship fields is set to None in dbmodels so they get filtered out
                recordFields =[f for f in newRecord.__dataclass_fields__.keys() if newRecord.__dataclass_fields__[f].type != None]
                
                for field in data:
                    if field in recordFields:
                        setattr(newRecord, field, data[field])
                newRecord.userId = current_user # this field is not included in request data, since it is derived from token

            else: 
                abort(400)

            # for transaction operations - update the portfolio record
            if entity == 'tx':
                portfolioRecord = updatePortfolio(current_user, data)
                if portfolioRecord == False:
                    abort(400)

                db.session.add(portfolioRecord)


            
            db.session.add(newRecord)

            db.session.commit()
            return jsonify({'data': { 'id' : 201, 'message' : newRecord}}), 201

        except HTTPException as e:
            db.session.rollback()
            abort(make_response({'data': { 'id' : 400, 'message' : f'client error, {entity} does not exist'}}, 400))
        except exc.SQLAlchemyError as e:
            print(e)
            db.session.rollback()
            abort(make_response({'data': { 'id' : 400, 'message' : f'client error, {entity} record not added'}}, 400))
        except BaseException as e:
            print(e)
            db.session.rollback()
            abort(make_response({'data': { 'id' : 500, 'message' : f'server error, {entity} record not added'}}, 500))


    # update an existing record in an entity
    @app.route("/api/edit/<entity>/<id>", methods=['PUT'])
    @validate_token
    def edit_record(current_user, entity, id):
        data = request.json
        try:
            entity = entity.lower()
            editRecord = None
            
            # otherwise use id
            if entity in dbTablesMap:
                editRecord = dbTablesMap[entity].query.filter_by(id=id).first()

            if editRecord == None:
                abort(404)

            # get the fields available for modification in the record using the dataclass attributes
            # dataclass for relationship fields is set to None in dbmodels so they get filtered out
            recordFields =[f for f in editRecord.__dataclass_fields__.keys() if editRecord.__dataclass_fields__[f].type != None]
                
            for field in data:
                if field in recordFields:
                    setattr(editRecord, field, data[field])
            db.session.commit()
            return jsonify({'data': { 'id' : 204, 'message' : f'{entity}/{id} updated'}})

        except HTTPException:
            abort(make_response({'data': { 'id' : 404, 'message' : f'{entity}/{id} record not found'}}, 404))
        except exc.SQLAlchemyError as e: 
            print(e)
            db.session.rollback()
            abort(make_response({'data': { 'id' : 400, 'message' : f'client error, {entity}/{id} not updated'}}, 400))
        except BaseException as e:
            print(e)
            db.session.rollback()
            abort(make_response({'data': { 'id' : 500, 'message' : f'server error, {entity}/{id} not updated'}}, 500))


    # remove a record from an entity
    @app.route("/api/remove/<entity>/<id>", methods=['DELETE'])
    @validate_token
    def remove_entity(current_user, entity, id):
        try:
            entity = entity.lower()
            # if entity is item, get record to delete by serial number
            if entity == "item":
                if dbTablesMap[entity].query.filter_by(serialNumber=id.upper()).delete() == 0:
                    abort(404)
                
            # if entity is a lookup table, mark record as inactive so it can't be used for future entries
            # but remains for existing entries
            elif entity in dbTablesMap:
                record = dbTablesMap[entity].query.filter_by(id=id).first()
                if record == None:
                    abort(404)
                setattr(record, "isActive", False)
            
            db.session.commit()     
            return jsonify({'data': { 'id' : 204, 'message' : f'{entity}/{id} removed'}})            
        except HTTPException:
            abort(make_response({'data': { 'id' : 404, 'message' : f'{entity}/{id} record not found'}}, 404))            
        except exc.SQLAlchemyError as e:
            print(e)
            db.session.rollback()
            abort(make_response({'data': { 'id' : 400, 'message' : f'client error, {entity}/{id} not removed'}}, 400))
        except BaseException as e:
            print(e)
            db.session.rollback()
            abort(make_response({'data': { 'id' : 500, 'message' : f'server error, {entity}/{id} not removed'}}, 500))
                
    app.run(use_reloader=False)    

create_app()


    
