"""
python3 src/server.py --mongodb-user sdadmin --mongodb-password root --mongodb-host localhost --mongodb-name sd --port 8001
"""

import json
import argparse
from db import db
from object_detection import ObjectDetection
import threading
from bottle import route, run, template, response, request
import traceback
from uuid import uuid4
from event_emmiter import event_emmiter

argparse = argparse.ArgumentParser()
argparse.add_argument("-dbh", "--mongodb-host", required=True, help="MongoDB host")
argparse.add_argument("-dbu", "--mongodb-user", required=True, help="MongoDB username")
argparse.add_argument("-dbp", "--mongodb-password", required=True, help="MongoDB password")
argparse.add_argument("-dbn", "--mongodb-name", required=True, help="MongoDB database name")
argparse.add_argument("-p", "--port", default=8000, help="Server port", type=int)


args = argparse.parse_args()

db.connect(args.mongodb_host, args.mongodb_user, args.mongodb_password, args.mongodb_name)


@route('/terminate-object-detection/<operation_id:path>')
def terminate_object_detection(operation_id):
    response.content_type = 'application/json; charset=UTF-8'
    event_emmiter.emit("TERMINATE_OBJECT_DETECTION", {"operation_id": operation_id})
    return json.dumps({"status": "OK"})


@route('/start-object-detection/<video_id:path>/<progress_endpoint:path>')
def start_object_detection(video_id, progress_endpoint):
    response.content_type = 'application/json; charset=UTF-8'

    operation_id = str(uuid4())

    object_detection = ObjectDetection(video_id, progress_endpoint)

    def termination_handler(data):
        if data["operation_id"] == operation_id:
            object_detection.terminate_asap()

    event_emmiter.on("TERMINATE_OBJECT_DETECTION", termination_handler)

    thread = threading.Thread(target=object_detection.detect)

    thread.start()

    return json.dumps({"status": "OK", "operation_id": operation_id})


if __name__ == "__main__":
    run(host='localhost', port=args.port)
