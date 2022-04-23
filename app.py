from flask import Flask, jsonify, request, abort, make_response
from flask_cors import CORS
from werkzeug.security import check_password_hash
from werkzeug.exceptions import HTTPException
import jwt
from functools import wraps
from dboperations import populateDB
import dbmodel
from dbmodel import tblUser, tblItem, tblCategory, tblManufacturer, tblModelNumber, tblBuilding, tblRoom, tblShelf, tblPartQuantity
import datetime
from sqlalchemy import exc
from sqlalchemy.orm import exc as exc2

# create a dictionary with all the DB tables for use with routing operations, minus the user table
dbTablesMap = {t.lower().removeprefix("tbl") : eval(t) for t in dir(dbmodel) if t.startswith("tbl") and t != 'tblUser'}

def create_app():
    app = Flask("app")
    app.secret_key = "keepmeasecret"
    
    # database configuration
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory2.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_ECHO'] = False


    from dbmodel import db
    # required to make SQLAlchemy and Flask work together
    with app.app_context():
        CORS(app)   # process CORS mode requests silently
        db.init_app(app)
        populateDB(db)
        
        
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
           
            # TESTING ONLY **************** * bypasses token validation and grants admin access to anyone
            #return f(1, *args, **kwargs)
            
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
            
        try:
        
            if 'username' not in data or 'password' not in data:
                abort(400)
                            
            user = tblUser.query.filter_by(username=data['username']).first()

            # invalid username/password check
            if not user or not check_password_hash(user.password, data['password']):
                abort(401)

            # create API token and give back to client
            token = jwt.encode({'id' : user.id, 'exp' : datetime.datetime.now() + datetime.timedelta(minutes=1440)}, app.config['SECRET_KEY'], "HS256")
            response = jsonify( {'data' : { 'id' : 200, 'message' : 'Logged in as ' + data['username'], 'token' : token }} )
            return response

        except HTTPException as e:
            print(e)
            if e.code == 401:
                abort(make_response({'data': { 'id' : 401, 'message' : 'invalid username/password'}}, 401))
            abort(make_response({'data': { 'id' : 400, 'message' : f'client error, bad request data'}}, 400))
        except exc.SQLAlchemyError as e:
                print(e)
                db.session.rollback()
                abort(make_response({'data': { 'id' : 400, 'message' : 'client error, login failed'}}, 400))
        except BaseException as e:
                print(e)
                db.session.rollback()
                abort(make_response({'data': { 'id' : 500, 'message' : 'server error, login failed'}}, 500))

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
            
            # for searching items records, search single items by serial number
            if entity == "item":
                if id != None:
                    r = tblItem.query.filter_by(serialNumber=id.upper()).first()
                else:
                    r = tblItem.query.all()

            # for searching lookup table records
            elif entity in dbTablesMap and entity != "item":
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
            
        response = jsonify({'data': { 'id': 200, 'message': r }});
        return response


    # add a new record to an entity
    @app.route("/api/add/<entity>/", methods=['POST'])
    @validate_token
    def add_record(current_user, entity):
        data = request.json

        try:
        
            entity = entity.lower()
            if entity in dbTablesMap:

                # special check to make sure not trying to use an existing serial number that exists in tblItems
                if 'serialNumber' in data:
                    
                    if tblItem.query.filter_by(serialNumber=data['serialNumber'].upper()).first() != None:
                        abort(409)


                newRecord = dbTablesMap[entity]()
                # get the fields available for modification in the record using the dataclass attributes
                # dataclass for relationship fields is set to None in dbmodels so they get filtered out
                recordFields =[f for f in newRecord.__dataclass_fields__.keys() if newRecord.__dataclass_fields__[f].type != None]
                
                for field in data:
                    if field in recordFields:
                        setattr(newRecord, field, data[field])
                newRecord.userId = current_user # this field is not included in request data, since it is derived from token
                newRecord.isPart = False    #no parts for now
            else: 
                abort(400)
            
            db.session.add(newRecord)
            db.session.commit()
            return jsonify({'data': { 'id' : 201, 'message' : newRecord}}), 201

        except HTTPException as e:
            db.session.rollback()
            if e.code == 409:
                abort(make_response({'data': { 'id' : 409, 'message' : f'item with serial number {data["serialNumber"]} already exists'}}, 409))
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
            
            # if entity is item, get record to updated by serial number
            if entity == "item":
                editRecord = dbTablesMap[entity].query.filter_by(serialNumber=id.upper()).first()


            # otherwise use id
            elif entity in dbTablesMap:
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
                
    app.run(debug=True)    

create_app()


    
