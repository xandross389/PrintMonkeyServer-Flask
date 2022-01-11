from flask import Flask, request
from flask_restful import Api, Resource
from flask_pymongo import PyMongo, ObjectId
from config import DevConfig
from http import HTTPStatus
from bson.errors import InvalidId

API_ROOT_PATH = "/api/v1"

app = Flask(__name__)
app.config.from_object(DevConfig)
# api = Api(app, doc="/docs")
api = Api(app)
mongo = PyMongo(app)
db = mongo.db


def is_valid_oid(oid):
    """
    Checks if a `oid` string is valid or not.

    Keyword arguments:
    oid -- the object id to validate
    Return: True or False
    """
    if not oid:
        return False

    try:
        ObjectId(oid)
        return True
    except (InvalidId, TypeError):
        return False


@app.route(f"{API_ROOT_PATH}/printers", methods=["GET"])
def list_printers():
    if request.method == "GET":
        try:
            printers_lst = []
            printers = list(db.printers.find())

            for printer in printers:
                tmp_printer = {
                    "id": str(printer["_id"]),
                    "name": printer["name"],
                    "desc": printer["desc"],
                    "computer_name": printer["computer_name"],
                    "computer_ip": printer["computer_ip"],
                    "comment": printer["comment"],
                    "flags": printer["flags"],
                }
                printers_lst.append(tmp_printer)
            return {"printers": printers_lst}, HTTPStatus.OK
        except Exception as ex:
            app.logger.error(f"error ocurred getting printers - {ex}")
            return {
                "message": "error ocurred getting printers"
            }, HTTPStatus.INTERNAL_SERVER_ERROR
    else:
        return {"message": "method not allowed"}, HTTPStatus.METHOD_NOT_ALLOWED


@app.route(f"{API_ROOT_PATH}/printer", methods=["POST"])
def insert_printer():
    """
    Create a new printer. POST - JSON:
    {
        "name": "Microsoft Print to PDF",
        "desc": "Microsoft virtual printer",
        "computer_name": "desktop1.domain.com",
        "computer_ip": "desktop1.domain.com",
        "comment": "some comment",
        "flags": ""
    }
    """
    if request.method == "POST":
        if request.is_json:
            if request.json["name"]:
                try:
                    id = db.printers.insert_one(
                        {
                            "name": request.json["name"],
                            "desc": request.json["desc"],
                            "computer_name": request.json["computer_name"],
                            "computer_ip": request.json["computer_ip"],
                            "comment": request.json["comment"],
                            "flags": request.json["flags"],
                        }
                    ).inserted_id

                    try:
                        return {
                            "id": str(ObjectId(id)),
                            "name": request.json["name"],
                            "desc": request.json["desc"],
                            "comment": request.json["comment"],
                            "computer_name": request.json["computer_name"],
                            "computer_ip": request.json["computer_ip"],
                            "flags": request.json["flags"],
                        }, HTTPStatus.CREATED
                    except Exception as ex:
                        app.logger.error(f"Error returning inserted entity - {ex}")
                        return {
                            "message": "Error returning inserted entity"
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
        else:
            return {"message": "request must be json"}, HTTPStatus.BAD_REQUEST
    else:
        return {"message": "method not allowed"}, HTTPStatus.METHOD_NOT_ALLOWED


@app.route(f"{API_ROOT_PATH}/printers", methods=["POST"])
def insert_printers_list():
    """
    Create printers in batch. POST JSON array of printers:
    "printers": [
        {
            "name": "Microsoft Print to PDF 2",
            "desc": "Microsoft virtual printer 1",
            "computer_name": "desktop1.domain.com",
            "computer_ip": "desktop1.domain.com",
            "comment": "no comments",
            "flags": ""
        },
        {
            "name": "Microsoft Print to PDF 2",
            "desc": "Microsoft virtual printer 2",
            "computer_name": "desktop1.domain.com",
            "computer_ip": "desktop1.domain.com",
            "comment": "no comments",
            "flags": ""
        },
        ...
        ]
    }
    """
    if request.is_json:
        if request.json["printers"]:
            try:
                ids = db.printers.insert_many(
                    request.json["printers"],
                    ordered=True,
                ).inserted_ids

                try:
                    inserted_printers = []

                    for i in range(len(ids)):
                        printer = {
                            "id": str(ObjectId(ids[i])),
                            "name": request.json["printers"][i]["name"],
                            "desc": request.json["printers"][i]["desc"],
                            "computer_name": request.json["printers"][i][
                                "computer_name"
                            ],
                            "computer_ip": request.json["printers"][i]["computer_ip"],
                            "comment": request.json["printers"][i]["comment"],
                            "flags": request.json["printers"][i]["flags"],
                        }
                        inserted_printers.append(printer)

                    return {"printers": inserted_printers}, HTTPStatus.CREATED
                except Exception as ex:
                    app.logger.error(f"Error returning inserted printers - {ex}")
                    return {
                        "message": "Error returning inserted printers"
                    }, HTTPStatus.CREATED

            except Exception as ex:
                app.logger.error(f"Error creating printers - {ex}")
                return {
                    "message": "Error creating printers"
                }, HTTPStatus.INTERNAL_SERVER_ERROR

        else:
            return {
                "message": "missing param: printers could not be empty or list must have elements"
            }, HTTPStatus.BAD_REQUEST
    return {"message": "request must be json"}, HTTPStatus.BAD_REQUEST


@app.route(f"{API_ROOT_PATH}/printer/<string:id>", methods=["GET"])
def get_printer_by_id(id):
    """Get printer by id"""
    if request.is_json:
        if is_valid_oid(id):
            try:
                printer = db.printers.find_one({"_id": ObjectId(id)})

                if printer:
                    return {
                        "id": str(printer["_id"]),
                        "name": printer["name"],
                        "desc": printer["desc"],
                        "computer_name": printer["computer_name"],
                        "computer_ip": printer["computer_ip"],
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


# @app.route(f"{API_ROOT_PATH}/printer/<string:name>", methods=["GET"])
# def get_printer_by_name(id):
#     """Get printer by name"""
#     if request.is_json:
#         if is_valid_oid(id):
#             try:
#                 printer = db.printers.find_one({"name": ObjectId(id)})

#                 if printer:
#                     return {
#                         "id": str(printer["_id"]),
#                         "name": printer["name"],
#                         "desc": printer["desc"],
#                         "computer_name": printer["computer_name"],
#                         "computer_ip": printer["computer_ip"],
#                         "comment": printer["comment"],
#                         "flags": printer["flags"],
#                     }, HTTPStatus.OK
#                 else:
#                     return {"message": "resource not found"}, HTTPStatus.NOT_FOUND

#             except Exception as ex:
#                 app.logger.error(f"error ocurred getting printers - {ex}")
#                 return {
#                     "message": f"error ocurred getting printer - {ex}"
#                 }, HTTPStatus.INTERNAL_SERVER_ERROR
#         else:
#             return {"message": "id is not valid"}, HTTPStatus.BAD_REQUEST


@app.route(f"{API_ROOT_PATH}/printer/<string:id>", methods=["DELETE"])
def delete_printer_by_id(id):
    """Delete a printer by id"""
    if is_valid_oid(id):
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


@app.route(f"{API_ROOT_PATH}/printer/<string:id>", methods=["PUT"])
def update_printer_by_id(id):
    """Update printer by id"""
    if is_valid_oid(id) and request.is_json:
        try:
            qry_filter = {"_id": ObjectId(id)}
            new_values = {
                "$set": {
                    "id": str(ObjectId(id)),
                    "name": request.json["name"],
                    "desc": request.json["desc"],
                    "computer_name": request.json["computer_name"],
                    "computer_ip": request.json["computer_ip"],
                    "comment": request.json["comment"],
                    "flags": request.json["flags"],
                }
            }

            upd_count = db.printers.update_one(qry_filter, new_values).modified_count

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


@app.route(f"{API_ROOT_PATH}/print-jobs", methods=["POST"])
def insert_print_job(printer):
    pass


@app.route(f"{API_ROOT_PATH}/printer/<string:id>/", methods=["POST"])
def delete_print_job(printer):
    pass


if __name__ == "__main__":
    app.run(port=3000)
