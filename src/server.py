from config_loader import config
import json
from object_detection import ObjectDetection
import threading
from bottle import route, run, template, response, request
from uuid import uuid4
from event_emmiter import event_emmiter
from bottle import static_file
from os import path
from util import *
from logger import *
import traceback
from codes_loader import codes

DIR = path.dirname(path.abspath(path.realpath(__file__)))
PUBLIC_DIR = path.abspath(path.join(DIR, "../public"))

OBJECT_DETECTION_ROUTES = config["cv_api"]["route"]["object_detection"]
EXTRACT_VIDEO_METADATA_ROUTE = OBJECT_DETECTION_ROUTES["extract_video_metadata"]
CANCEL_OBJECT_DETECTION_ROUTE = OBJECT_DETECTION_ROUTES["cancel_object_detection"]
START_OBJECT_DETECTION_ROUTE = OBJECT_DETECTION_ROUTES["start_object_detection"]


def _ok_res(data={}, _links={}):
    return json.dumps({"status": WEB_STATUS_OK, "payload": {**data}, "_links": {**_links}})


def _err_res(data={}, _links={}):
    return json.dumps({"status": WEB_STATUS_INTERNAL_SERVER_ERROR, "payload": {**data}, "_links": {**_links}})


@route("/")
def index():
    return static_file("welcome.html", root=PUBLIC_DIR)


@route(format_route(EXTRACT_VIDEO_METADATA_ROUTE, {"video_id": "<video_id:path>"}))
def extract_video_metadata(video_id):
    try:
        response.content_type = "application/json; charset=UTF-8"
        meta = video_metadata(video_id)
        _links = {"self": {"href": cv_api_url(format_route(EXTRACT_VIDEO_METADATA_ROUTE, {"video_id": video_id}))}}
        return _ok_res(meta, _links=_links)
    except:
        log_error(traceback.format_exc())
        return _err_res()


@route(format_route(CANCEL_OBJECT_DETECTION_ROUTE, {"video_id": "<video_id:path>"}))
def cancel_object_detection(video_id):
    response.content_type = "application/json; charset=UTF-8"
    event_emmiter.emit(OBJECT_DETECTION_EVENT_CANCEL, {"video_id": video_id})
    _links = {"self": {"href": cv_api_url(format_route(CANCEL_OBJECT_DETECTION_ROUTE, {"video_id": video_id}))}}
    return _ok_res(_links=_links)


@route(format_route(START_OBJECT_DETECTION_ROUTE, {"video_id": "<video_id:path>"}))
def start_object_detection(video_id):
    response.content_type = "application/json; charset=UTF-8"

    object_detection = ObjectDetection(video_id)

    thread = threading.Thread(target=object_detection.detect)

    thread.start()

    data = {"video_id": video_id}
    _links = {"self": {"href": cv_api_url(format_route(START_OBJECT_DETECTION_ROUTE, {"video_id": video_id}))},
              "cancel": {"href": cv_api_url(format_route(CANCEL_OBJECT_DETECTION_ROUTE, {"video_id": video_id}))}}
    return _ok_res(data=data, _links=_links)


def start_server(host, port):
    run(host=host, port=port)
