from flask import Flask, request
from flask_pymongo import PyMongo
from werkzeug.exceptions import MethodNotAllowed
from werkzeug.wrappers import response
from werkzeug.wsgi import responder

SERVER_ADDRESS = "192.168.194.207"


app = Flask(__name__)
app.config["MONGO_URI"] = f"mongodb://{SERVER_ADDRESS}/printmonkey"

mongo = PyMongo(app)


@app.route("/api/print_job", methods=["POST"])
def save_print_job():
    """
    {'JobId': 9, 'pPrinterName': 'NPI602C37 (HP LaserJet 400 M401n)',
    'pMachineName': '\\\\PC12ads40', 'pUserName': 'uasername', 'pDocument': 'new 4',
    'pDatatype': 'RAW', 'pStatus': None, 'Status': 12288, 'Priority': 1, 'Position': 1,
    'TotalPages': 1, 'PagesPrinted': 1, 'Submitted': pywintypes.datetime(2021, 12, 27, 16, 46, 17, 74000,
    tzinfo=TimeZoneInfo('GMT Standard Time', True))}
    """
    job_id = request.json["job_id"]
    printer_name = request.json["printer_name"]
    machine_name = request.json["machine_name"]
    user_name = request.json["user_name"]
    document = request.json["document"]

    if job_id and printer_name and machine_name and user_name and document:
        inserted_id = mongo.db.print_jobs.upinsert_one(
            {
                "job_id": job_id,
                "printer_name": printer_name,
                "machine_name": machine_name,
                "user_name": user_name,
                "document": document,
            }
        )

        response = {
            "id": inserted_id,
            "job_id": job_id,
            "printer_name": printer_name,
            "machine_name": machine_name,
            "user_name": user_name,
            "document": document,
        }
        # return response
        return {"message": "ok"}
    else:
        return {"message": "error, missing paramas"}


@app.route("/printer", methods=["POST"])
def save_printer(foo):

    return {"message": "ok"}


if __name__ == "__main__":
    app.run(port=3000, debug=True)
