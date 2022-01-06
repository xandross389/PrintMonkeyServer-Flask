from flask import Flask, request
from flask_restx import Api, Resource
from flask_pymongo import PyMongo, ObjectId
from config import DevConfig
from http import HTTPStatus

app = Flask(__name__)
app.config.from_object(DevConfig)
api = Api(app, doc="/docs")
mongo = PyMongo(app)
db = mongo.db


@api.route("/printers")
class PrintersResource(Resource):
    """
    flags, desc, name, comment
    """

    def get(self):
        """Get all printers"""

        try:
            printers_lst = []
            printers = list(db.printers.find())

            for printer in printers:
                tmp_printer = {
                    "id": str(printer["_id"]),
                    "name": printer["name"],
                    "desc": printer["desc"],
                    "comment": printer["comment"],
                    "flags": printer["flags"],
                }
                printers_lst.append(tmp_printer)

            return printers_lst, HTTPStatus.OK

        except Exception as ex:
            app.logger.error(f"error ocurred getting printers - {ex}")
            return {
                "message": "error ocurred getting printers"
            }, HTTPStatus.INTERNAL_SERVER_ERROR

    def post(self):
        """
        Create a new printer. POST - JSON:
        {
            "name": "Microsoft Print to PDF",
            "desc": "Microsoft virtual printer",
            "comment": "some comment",
            "flags": ""
        }
        """
        if request.is_json:
            if request.json["name"]:
                try:
                    id = db.printers.insert_one(
                        {
                            "name": request.json["name"],
                            "desc": request.json["desc"],
                            "comment": request.json["comment"],
                            "flags": request.json["flags"],
                        }
                    ).inserted_id

                    return {
                        "id": str(ObjectId(id)),
                        "name": request.json["name"],
                        "desc": request.json["desc"],
                        "comment": request.json["comment"],
                        "flags": request.json["flags"],
                    }, HTTPStatus.CREATED
                except Exception as ex:
                    app.logger.error(f"Error creating entity - {ex}")
                    return {
                        "message": "Error creating entity"
                    }, HTTPStatus.INTERNAL_SERVER_ERROR
            else:
                return {
                    "message": "missing param: name could not be enpty"
                }, HTTPStatus.BAD_REQUEST
        return {"message": "request must be json"}, HTTPStatus.BAD_REQUEST


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
