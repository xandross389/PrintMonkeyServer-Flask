from flask import Flask, request
from flask_restful import Api, Resource
from flask_pymongo import PyMongo, ObjectId
from config import DevConfig
from http import HTTPStatus
from bson.errors import InvalidId
import datetime

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


@app.route(f"{API_ROOT_PATH}/job", methods=["POST"])
def insert_job():
    """
    Insert print job

    Keyword arguments:
    argument -- post request with print job. Insert a new job. POST - JSON:
    {
        "job_id": 9,
        "printer_name": "NPI602C37 (HP LaserJet 400 M401n)",
        "printer_ip": "192.168.78.82"
        "machine_name": "PC12ads40",
        "machine_ip": "192.168.78.2",
        "user_name": "uasername",
        "document": "new 4",
        "data_type": "RAW",
        "pstatus": "",
        "status": 12288,
        "priority": 1,
        "position": 1,
        "total_pages": 4,
        "pages_printed": 1,
        "submit_time": "2022-01-12 22:03:15"
    }
    Return: return inserted print job in json format
    """
    if request.method == "POST":
        if request.is_json:
            if request.json["job_id"]:
                try:
                    id = db.jobs.insert_one(
                        {
                            "job_id": request.json["job_id"],
                            "printer_name": request.json["printer_name"],
                            "printer_ip": request.json["printer_ip"],
                            "machine_name": request.json["machine_name"],
                            "machine_ip": request.json["machine_ip"],
                            "user_name": request.json["user_name"],
                            "document": request.json["document"],
                            "data_type": request.json["data_type"],
                            "pstatus": request.json["pstatus"],
                            "status": request.json["status"],
                            "priority": request.json["priority"],
                            "position": request.json["position"],
                            "total_pages": request.json["total_pages"],
                            "pages_printed": request.json["pages_printed"],
                            "submit_time": datetime.datetime.strptime(
                                request.json["submit_time"], "%Y-%m-%d %H:%M:%S"
                            ),
                            # "submit_time": datetime.datetime.strptime(
                            #     "2017-10-13 10:53:53", "%Y-%m-%d %H:%M:%S"
                            # ),
                        }
                    ).inserted_id

                    try:
                        return {
                            "id": str(ObjectId(id)),
                            "job_id": request.json["job_id"],
                            "printer_name": request.json["printer_name"],
                            "printer_ip": request.json["printer_ip"],
                            "machine_name": request.json["machine_name"],
                            "machine_ip": request.json["machine_ip"],
                            "user_name": request.json["user_name"],
                            "document": request.json["document"],
                            "data_type": request.json["data_type"],
                            "pstatus": request.json["pstatus"],
                            "status": request.json["status"],
                            "priority": request.json["priority"],
                            "position": request.json["position"],
                            "total_pages": request.json["total_pages"],
                            "pages_printed": request.json["pages_printed"],
                            "submit_time": datetime.datetime.strptime(
                                request.json["submit_time"], "%Y-%m-%d %H:%M:%S"
                            ),
                        }, HTTPStatus.CREATED
                    except Exception as ex:
                        app.logger.error(f"Error returning job entity - {ex}")
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
                    "message": "missing param: job_id could not be enpty"
                }, HTTPStatus.BAD_REQUEST
        else:
            return {"message": "request must be json"}, HTTPStatus.BAD_REQUEST
    else:
        return {"message": "method not allowed"}, HTTPStatus.METHOD_NOT_ALLOWED


@app.route(f"{API_ROOT_PATH}/job/<string:id>", methods=["GET"])
def get_job_by_id(id):
    """Get job by id"""
    if request.is_json:
        if is_valid_oid(id):
            try:
                job = db.jobs.find_one({"_id": ObjectId(id)})

                if job:
                    return {
                        "id": str(job["_id"]),
                        "job_id": job["job_id"],
                        "printer_name": job["printer_name"],
                        "printer_ip": job["printer_ip"],
                        "machine_name": job["machine_name"],
                        "machine_ip": job["machine_ip"],
                        "user_name": job["user_name"],
                        "document": job["document"],
                        "data_type": job["data_type"],
                        "pstatus": job["pstatus"],
                        "status": job["status"],
                        "priority": job["priority"],
                        "position": job["position"],
                        "total_pages": job["total_pages"],
                        "pages_printed": job["pages_printed"],
                        "submit_time": job["submit_time"].strftime("%d/%m/%Y %H:%M:%S"),
                    }, HTTPStatus.OK
                else:
                    return {"message": "resource not found"}, HTTPStatus.NOT_FOUND

            except Exception as ex:
                app.logger.error(f"error ocurred getting job - {ex}")
                return {
                    "message": f"error ocurred getting job - {ex}"
                }, HTTPStatus.INTERNAL_SERVER_ERROR
        else:
            return {"message": "id is not valid"}, HTTPStatus.BAD_REQUEST


# TODO
@app.route(f"{API_ROOT_PATH}/job/<string:id>", methods=["PUT"])
def update_job_by_id(id):
    """Update job by id"""
    if is_valid_oid(id) and request.is_json:
        try:
            qry_filter = {"_id": ObjectId(id)}
            new_values = {
                "$set": {
                    "id": str(ObjectId(id)),
                    "job_id": request.json["job_id"],
                    "printer_name": request.json["printer_name"],
                    "printer_ip": request.json["printer_ip"],
                    "machine_name": request.json["machine_name"],
                    "machine_ip": request.json["machine_ip"],
                    "user_name": request.json["user_name"],
                    "document": request.json["document"],
                    "data_type": request.json["data_type"],
                    "pstatus": request.json["pstatus"],
                    "status": request.json["status"],
                    "priority": request.json["priority"],
                    "position": request.json["position"],
                    "total_pages": request.json["total_pages"],
                    "pages_printed": request.json["pages_printed"],
                    "submit_time": datetime.datetime.strptime(
                        request.json["submit_time"], "%Y-%m-%d %H:%M:%S"
                    ),
                }
            }

            upd_count = db.jobs.update_one(qry_filter, new_values).modified_count

            if upd_count > 0:
                return {"message": f"{upd_count} resources updated"}, HTTPStatus.OK
            else:
                return {"message": "no resource updated"}, HTTPStatus.OK

        except Exception as ex:
            app.logger.error(f"error ocurred getting job - {ex}")
            return {
                "message": f"error ocurred getting job - {ex}"
            }, HTTPStatus.INTERNAL_SERVER_ERROR
    else:
        return {"message": "id is not valid"}, HTTPStatus.BAD_REQUEST


@app.route(f"{API_ROOT_PATH}/job/<string:id>", methods=["DELETE"])
def delete_job_by_id(id):
    """Delete a printer by id"""
    if is_valid_oid(id):
        try:
            db.jobs.delete_one({"_id": ObjectId(id)})
            return {"message": f"resource deleted"}, HTTPStatus.OK

        except Exception as ex:
            app.logger.error(f"error ocurred deleting job - {ex}")
            return {
                "message": f"error ocurred deleting job - {ex}"
            }, HTTPStatus.INTERNAL_SERVER_ERROR
    else:
        return {"message": "id is not valid"}, HTTPStatus.BAD_REQUEST


@app.route(f"{API_ROOT_PATH}/jobs", methods=["POST"])
def insert_jobs_list():
    """
    Insert list of print jobs

    Keyword arguments:
    argument -- post request with jobs list. Create printers in batch. POST JSON array of printers:
    "printers": [
        {
            "job_id": 9,
            "printer_name": "NPI602C37 (HP LaserJet 400 M401n)",
            "printer_ip": "192.168.78.82"
            "machine_name": "PC12ads40",
            "machine_ip": "192.168.78.2",
            "user_name": "uasername",
            "document": "new 4",
            "data_type": "RAW",
            "pstatus": "",
            "status": 12288,
            "priority": 1,
            "position": 1,
            "total_pages": 4,
            "pages_printed": 1,
            "submit_time": "2022-01-12 22:03:15"
        },
        {
            "job_id": 10,
            ...
            "submit_time": "2022-01-12 22:03:15"
        },
        ...
        ]
    }
    Return: return list of inserted print jobs in json format
    """
    if request.is_json:
        if request.json["jobs"]:
            try:
                ids = db.jobs.insert_many(
                    request.json["jobs"],
                    ordered=True,
                ).inserted_ids

                try:
                    inserted_jobs = []

                    for i in range(len(ids)):
                        job = {
                            "id": str(ObjectId(ids[i])),
                            "job_id": request.json["jobs"][i]["job_id"],
                            "printer_name": request.json["jobs"][i]["printer_name"],
                            "printer_ip": request.json["jobs"][i]["printer_ip"],
                            "machine_name": request.json["jobs"][i]["machine_name"],
                            "machine_ip": request.json["jobs"][i]["machine_ip"],
                            "user_name": request.json["jobs"][i]["user_name"],
                            "document": request.json["jobs"][i]["document"],
                            "data_type": request.json["jobs"][i]["data_type"],
                            "pstatus": request.json["jobs"][i]["pstatus"],
                            "status": request.json["jobs"][i]["status"],
                            "priority": request.json["jobs"][i]["priority"],
                            "position": request.json["jobs"][i]["position"],
                            "total_pages": request.json["jobs"][i]["total_pages"],
                            "pages_printed": request.json["jobs"][i]["pages_printed"],
                            "submit_time": datetime.datetime.strptime(
                                request.json["jobs"][i]["submit_time"],
                                "%Y-%m-%d %H:%M:%S",
                            ),
                        }
                        inserted_jobs.append(job)

                    return {"printers": inserted_jobs}, HTTPStatus.CREATED
                except Exception as ex:
                    app.logger.error(f"Error returning inserted jobs - {ex}")
                    return {
                        "message": "Error returning inserted jobs"
                    }, HTTPStatus.CREATED

            except Exception as ex:
                app.logger.error(f"Error creating jobs - {ex}")
                return {
                    "message": "Error creating jobs"
                }, HTTPStatus.INTERNAL_SERVER_ERROR

        else:
            return {
                "message": "missing param: printers could not be empty or list must have elements"
            }, HTTPStatus.BAD_REQUEST
    return {"message": "request must be json"}, HTTPStatus.BAD_REQUEST


@app.route(f"{API_ROOT_PATH}/jobs", methods=["GET"])
def list_jobs():
    if request.method == "GET":
        try:
            jobs_lst = []
            jobs = list(db.jobs.find())

            for job in jobs:
                tmp_job = {
                    "id": str(job["_id"]),
                    "job_id": job["job_id"],
                    "printer_name": job["printer_name"],
                    "printer_ip": job["printer_ip"],
                    "machine_name": job["machine_name"],
                    "machine_ip": job["machine_ip"],
                    "user_name": job["user_name"],
                    "document": job["document"],
                    "data_type": job["data_type"],
                    "pstatus": job["pstatus"],
                    "status": job["status"],
                    "priority": job["priority"],
                    "position": job["position"],
                    "total_pages": job["total_pages"],
                    "pages_printed": job["pages_printed"],
                    "submit_time": job["submit_time"].strftime("%d/%m/%Y %H:%M:%S"),
                }
                jobs_lst.append(tmp_job)
            return {"jobs": jobs_lst}, HTTPStatus.OK
        except Exception as ex:
            app.logger.error(f"error ocurred getting jobs - {ex}")
            return {
                "message": "error ocurred getting jobs"
            }, HTTPStatus.INTERNAL_SERVER_ERROR
    else:
        return {"message": "method not allowed"}, HTTPStatus.METHOD_NOT_ALLOWED


if __name__ == "__main__":
    app.run(port=3000)
