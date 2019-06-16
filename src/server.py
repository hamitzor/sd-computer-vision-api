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


@route("/terminate-object-detection/<operation_id:path>/<information_endpoint:path>")
def terminate_object_detection_with_information(operation_id, information_endpoint):
    return _terminate_object_detection(operation_id, information_endpoint)


@route("/terminate-object-detection/<operation_id:path>")
def terminate_object_detection_without_information(operation_id):
    return _terminate_object_detection(operation_id)


@route("/start-object-detection/<video_id:path>/<progress_endpoint:path>")
def start_object_detection_with_progress(video_id, progress_endpoint):
    return _start_object_detection(video_id, progress_endpoint)


@route("/start-object-detection/<video_id:path>")
def start_object_detection_without_progress(video_id):
    return _start_object_detection(video_id)


def _terminate_object_detection(operation_id, information_endpoint=None):
    response.content_type = "application/json; charset=UTF-8"
    event_emmiter.emit("TERMINATE_OBJECT_DETECTION", {"operation_id": operation_id, "information_endpoint": information_endpoint})
    return json.dumps({"status": "OK"})


def _start_object_detection(video_id, progress_endpoint=None):
    response.content_type = "application/json; charset=UTF-8"

    operation_id = str(uuid4())

    print(video_id, progress_endpoint)

    object_detection = ObjectDetection(operation_id, video_id, progress_endpoint)

    thread = threading.Thread(target=object_detection.detect)

    thread.start()

    return json.dumps({"status": "OK", "operation_id": operation_id})


def start_server(host, port):
    run(host=host, port=port)
