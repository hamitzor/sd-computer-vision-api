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
from codes_loader import codes

DIR = path.dirname(path.abspath(path.realpath(__file__)))
PUBLIC_DIR = path.abspath(path.join(DIR, "../public"))
EXTRACT_VIDEO_METADATA_ROUTE = config["cv_api"]["route"]["object_detection"]["command"]["extract_video_metadata"]
TERMINATE_OBJECT_DETECTION_ROUTE = config["cv_api"]["route"]["object_detection"]["command"]["terminate_object_detection"]
START_OBJECT_DETECTION_ROUTE = config["cv_api"]["route"]["object_detection"]["command"]["start_object_detection"]
OK_STATUS = codes["web_api_status"]["OK"]
INTERNAL_SERVER_ERROR_STATUS = codes["web_api_status"]["INTERNAL_SERVER_ERROR"]


def _ok_res(data={}, _links={}):
    return json.dumps({"status": OK_STATUS, "payload": {**data}, "_links": {**_links}})


def _err_res(data={}, _links={}):
    return json.dumps({"status": INTERNAL_SERVER_ERROR_STATUS, "payload": {**data}, "_links": {**_links}})


@route("/")
def index():
    return static_file("welcome.html", root=PUBLIC_DIR)


@route(util.format_route(EXTRACT_VIDEO_METADATA_ROUTE, {"video_id": "<video_id:path>"}))
def video_metadata(video_id):
    try:
        meta = util.video_metadata(video_id)
        _links = {"self": {"href": util.format_route(EXTRACT_VIDEO_METADATA_ROUTE, {"video_id": video_id})}}
        return _ok_res(meta, _links=_links)
    except:
        log_error(traceback.format_exc())
        return _err_res()


@route(util.format_route(TERMINATE_OBJECT_DETECTION_ROUTE, {"operation_id": "<operation_id:path>"}))
def terminate_object_detection(operation_id):
    response.content_type = "application/json; charset=UTF-8"
    event_emmiter.emit("TERMINATE_OBJECT_DETECTION", {"operation_id": operation_id})
    _links = {"self": {"href": util.format_route(TERMINATE_OBJECT_DETECTION_ROUTE, {"operation_id": operation_id})}}
    return _ok_res(_links=_links)


@route(util.format_route(START_OBJECT_DETECTION_ROUTE, {"video_id": "<video_id:path>"}))
def start_object_detection(video_id):
    response.content_type = "application/json; charset=UTF-8"

    operation_id = str(uuid4())

    object_detection = ObjectDetection(operation_id, video_id)

    thread = threading.Thread(target=object_detection.detect)

    thread.start()

    data = {"operation_id": operation_id}
    _links = {"self": {"href": util.format_route(START_OBJECT_DETECTION_ROUTE, {"video_id": video_id})},
              "terminate": {"href": util.format_route(TERMINATE_OBJECT_DETECTION_ROUTE, {"operation_id": operation_id})}}
    return _ok_res(data=data, _links=_links)


def start_server(host, port):
    run(host=host, port=port)
