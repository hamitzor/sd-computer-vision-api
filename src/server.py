import json
from object_detection import ObjectDetection
import threading
from bottle import route, run, template, response, request
from uuid import uuid4
from event_emmiter import event_emmiter
from bottle import static_file
from os import path
import util
from config_loader import config
from logger import *
import traceback

DIR = path.dirname(path.abspath(path.realpath(__file__)))
PUBLIC_DIR = path.abspath(path.join(DIR, "../public"))
EXTRACT_VIDEO_METADATA_ENDPOINT = config["cv-api"]["endpoint"]["object-detection"]["command"]["extract-video-metadata"]
TERMINATE_OBJECT_DETECTION_ENDPOINT = config["cv-api"]["endpoint"]["object-detection"]["command"]["terminate-object-detection"]
START_OBJECT_DETECTION_ENDPOINT = config["cv-api"]["endpoint"]["object-detection"]["command"]["start-object-detection"]


def _ok_res(data={}, _links={}):
    return json.dumps({"status": "OK", "payload": {**data}, "_links": {**_links}})


def _err_res(data={}, _links={}):
    return json.dumps({"status": "ERROR", "payload": {**data}, "_links": {**_links}})


@route("/")
def index():
    return static_file("welcome.html", root=PUBLIC_DIR)


@route(EXTRACT_VIDEO_METADATA_ENDPOINT+"/<video_id:path>")
def video_metadata(video_id):
    try:
        meta = util.video_metadata(video_id)
        return _ok_res(meta)
    except:
        log_error(traceback.format_exc())
        return _err_res()


@route(TERMINATE_OBJECT_DETECTION_ENDPOINT+"/<operation_id:path>")
def terminate_object_detection(operation_id):
    response.content_type = "application/json; charset=UTF-8"
    event_emmiter.emit("TERMINATE_OBJECT_DETECTION", {"operation_id": operation_id})
    _links = {"self": {"href": TERMINATE_OBJECT_DETECTION_ENDPOINT+"/"+operation_id}}
    return _ok_res(_links=_links)


@route(START_OBJECT_DETECTION_ENDPOINT+"/<video_id:path>")
def start_object_detection(video_id):
    response.content_type = "application/json; charset=UTF-8"

    operation_id = str(uuid4())

    object_detection = ObjectDetection(operation_id, video_id)

    thread = threading.Thread(target=object_detection.detect)

    thread.start()

    data = {"operation_id": operation_id}
    _links = {"self": {"href": START_OBJECT_DETECTION_ENDPOINT+"/"+video_id},
              "terminate": {"href": TERMINATE_OBJECT_DETECTION_ENDPOINT+"/"+operation_id}}
    return _ok_res(data=data, _links=_links)


def start_server(host, port):
    run(host=host, port=port)
