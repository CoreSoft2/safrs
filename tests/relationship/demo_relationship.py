#!/usr/bin/env python3
"""
  This demo application demonstrates the functionality of the safrs documented REST API
  After installing safrs with pip, you can run this app standalone:
  $ python3 demo_relationship.py [Listener-IP]

  This will run the example on http://Listener-Ip:5000

  - A database is created and a user is added
  - A rest api is available
  - swagger documentation is generated

  This is a minimal example, you'll probably want to use demo_relationship_ext.py instead!!!
"""
import sys
import logging
import builtins
from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
from safrs import SAFRSBase, SAFRSAPI, jsonapi_rpc

db = SQLAlchemy()

# Example sqla database object
class User(SAFRSBase, db.Model):
    """
        description: User description
    """

    __tablename__ = "Users"
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, default="")
    email = db.Column(db.String, default="")
    books = db.relationship("Book", back_populates="user", lazy="dynamic")

    # Following method is exposed through the REST API
    # This means it can be invoked with a HTTP POST
    @classmethod
    @jsonapi_rpc(http_methods=["POST"])
    def send_mail(self, **args):
        """
        description : Send an email
        args:
            email:
                type : string
                example : test email
        """
        return {"result": args}


class Book(SAFRSBase, db.Model):
    """
        description: Book description
    """

    __tablename__ = "Books"
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, default="")
    user_id = db.Column(db.String, db.ForeignKey("Users.id"))
    user = db.relationship("User", back_populates="books")


def populate_db():
    """
        Add some items to the db
    """
    user0 = User(name="user0", email="em@il0")
    book0 = Book(name="test_book0")
    user0.books.append(book0)
    user1 = User(name="user1", email="em@il1")
    book1 = Book(name="test_book1", user=user1)
    book2 = Book(name="test_book2")
    user1 = User(name="user2", email="em@il2", books=[book2])


if __name__ == "__main__":
    HOST = sys.argv[1] if len(sys.argv) > 1 else "0.0.0.0"
    PORT = 5000
    app = Flask("SAFRS Demo Application")
    app.config.update(SQLALCHEMY_DATABASE_URI="sqlite://", DEBUG=True)
    db.init_app(app)
    db.app = app
    # Create the database
    db.create_all()
    API_PREFIX = ""

    with app.app_context():
        api = SAFRSAPI(app, host="{}:{}".format(HOST, PORT), port=PORT, prefix=API_PREFIX)
        populate_db()
        # Expose the database objects as REST API endpoints
        api.expose_object(User)
        api.expose_object(Book)
        # Register the API at /api/docs
        print("Starting API: http://{}:{}{}".format(HOST, PORT, API_PREFIX))
        app.run(host=HOST, port=PORT)
