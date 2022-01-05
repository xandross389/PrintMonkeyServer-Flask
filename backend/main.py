from flask import Flask, request
from flask_restx import Api, Resource
from flask_pymongo import PyMongo, ObjectId
from config import DevConfig
from http import HTTPStatus


app = Flask(__name__)
# app.config["MONGO_URI"] = f"mongodb://{SERVER_ADDRESS}/printmonkey"
app.config.from_object(DevConfig)
api = Api(app, doc="/docs")
mongo = PyMongo(app)


@api.route("/printers")
class PrintersResource(Resource):
    def get(self):
        """Get all printers"""
        pass

    def post(self):
        """Create a new printer"""
        printer = {"name": request.json("name"), "user": request.json("user")}


@api.route("/printer/<int:id>")
class PrinterResource(Resource):
    def get(self, id):
        """Get printer by id"""
        printers = mongo.printers.find({"_id": ObjectId(id)})

        return printers.jsonify(), HTTPStatus.OK

    def delete(self, id):
        """Delete a printer by id"""
        printers = mongo.printers.delete({"_id": ObjectId(id)})

        return {"message": "deleted"}, HTTPStatus.OK


if __name__ == "__main__":
    app.run(port=3000)
