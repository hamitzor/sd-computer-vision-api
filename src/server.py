import json
from object_detection import ObjectDetection
import threading
from bottle import route, run, template, response, request
from uuid import uuid4
from event_emmiter import event_emmiter
from bottle import static_file
from os import path


DIR = path.dirname(path.abspath(path.realpath(__file__)))
PUBLIC_DIR = path.abspath(path.join(DIR, "../public"))


@route("/")
def index():
    return static_file("welcome.html", root=PUBLIC_DIR)


@route("/terminate-object-detection/<operation_id:path>")
def terminate_object_detection(operation_id):
    response.content_type = "application/json; charset=UTF-8"
    event_emmiter.emit("TERMINATE_OBJECT_DETECTION", {"operation_id": operation_id})
    return json.dumps({"status": "OK"})


@route("/start-object-detection/<video_id:path>/<progress_endpoint:path>")
def start_object_detection(video_id, progress_endpoint):
    response.content_type = "application/json; charset=UTF-8"

    operation_id = str(uuid4())

    object_detection = ObjectDetection(video_id, progress_endpoint)

    def termination_handler(data):
        if data["operation_id"] == operation_id:
            object_detection.terminate_asap()

    event_emmiter.on("TERMINATE_OBJECT_DETECTION", termination_handler)

    thread = threading.Thread(target=object_detection.detect)

    thread.start()

    return json.dumps({"status": "OK", "operation_id": operation_id})


def start_server(host, port):
    run(host=host, port=port)
