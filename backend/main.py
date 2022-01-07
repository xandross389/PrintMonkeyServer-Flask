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

from flask import Flask, request
from flask_restx import Api, Resource
from flask_pymongo import PyMongo, ObjectId
from config import DevConfig
from http import HTTPStatus
from bson.errors import InvalidId

app = Flask(__name__)
app.config.from_object(DevConfig)
api = Api(app, doc="/docs")
mongo = PyMongo(app)
db = mongo.db


@api.route("/api/v1/printers")
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


@api.route("/api/v1/printer/<string:id>")
class PrinterResource(Resource):
    def is_valid_oid(cls, oid):
        """Checks if a `oid` string is valid or not.

        :Parameters:
          - `oid`: the object id to validate

        .. versionadded:: 2.3
        """
        if not oid:
            return False

        try:
            ObjectId(oid)
            return True
        except (InvalidId, TypeError):
            return False

    def get(self, id):
        """Get printer by id"""
        if self.is_valid_oid(id):
            try:
                printer = db.printers.find_one({"_id": ObjectId(id)})

                if printer:
                    return {
                        "id": str(printer["_id"]),
                        "name": printer["name"],
                        "desc": printer["desc"],
                        "comment": printer["comment"],
                        "flags": printer["flags"],
                    }, HTTPStatus.OK
                else:
                    return {"message": "resource not found"}, HTTPStatus.NOT_FOUND

            except Exception as ex:
                app.logger.error(f"error ocurred getting printers - {ex}")
                return {
                    "message": f"error ocurred getting printer - {ex}"
                }, HTTPStatus.INTERNAL_SERVER_ERROR
        else:
            return {"message": "id is not valid"}, HTTPStatus.BAD_REQUEST

    def delete(self, id):
        """Delete a printer by id"""
        if self.is_valid_oid(id):
            try:
                db.printers.delete_one({"_id": ObjectId(id)})
                return {"message": f"resource deleted"}, HTTPStatus.OK

            except Exception as ex:
                app.logger.error(f"error ocurred deleting printer - {ex}")
                return {
                    "message": f"error ocurred deleting printer - {ex}"
                }, HTTPStatus.INTERNAL_SERVER_ERROR
        else:
            return {"message": "id is not valid"}, HTTPStatus.BAD_REQUEST

    def put(self, id):
        """Update printer by id"""
        if self.is_valid_oid(id) and request.is_json:
            try:
                qry_filter = {"_id": ObjectId(id)}
                new_values = {
                    "$set": {
                        "id": str(ObjectId(id)),
                        "name": request.json["name"],
                        "desc": request.json["desc"],
                        "comment": request.json["comment"],
                        "flags": request.json["flags"],
                    }
                }

                upd_count = db.printers.update_one(
                    qry_filter, new_values
                ).modified_count

                if upd_count > 0:
                    return {"message": f"{upd_count} resources updated"}, HTTPStatus.OK
                else:
                    return {"message": "no resource updated"}, HTTPStatus.OK

            except Exception as ex:
                app.logger.error(f"error ocurred getting printers - {ex}")
                return {
                    "message": f"error ocurred getting printer - {ex}"
                }, HTTPStatus.INTERNAL_SERVER_ERROR
        else:
            return {"message": "id is not valid"}, HTTPStatus.BAD_REQUEST


if __name__ == "__main__":
    app.run(port=3000)
