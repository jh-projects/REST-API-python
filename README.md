# REST-API-python
 A simple Python REST API using Flask to interact with a SQL backend.  Uses SQLAlchemy for an ORM wrapper.

There are a couple different projects developed using this API.  One is an inventory application, the other is a cryptocurrency portfolio tracker.  Each project has its own branch of the REST API.  Front ends for these applications are built in React; see other repositories for their implementations.

This REST API supports CRUD operations using the standard HTTP verbs - GET, POST, PUT, DELETE.  It includes token access control with usernames/passwords for obtaining tokens, and supports operations across any table that exists in the DB schema.
