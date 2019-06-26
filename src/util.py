import cv2
from threading import Thread
from urllib.request import urlopen
from os import path
import json
import uuid
from config_loader import config
from mongo import db
from bson.objectid import ObjectId
import re
from logger import *
import traceback
from config_loader import config

codes = config["codes"]


WEB_API_ADRESS = "http://" + config["web_api"]["hostname"]+":"+str(config["web_api"]["port"])
CV_API_ADDRESS = "http://" + config["cv_api"]["hostname"]+":"+str(config["cv_api"]["port"])

CV_STATUSES = codes["cv_status"]
CV_STATUS_NOT_STARTED = CV_STATUSES["NOT_STARTED"]
CV_STATUS_STARTED = CV_STATUSES["STARTED"]
CV_STATUS_CANCELED = CV_STATUSES["CANCELED"]
CV_STATUS_FAILED = CV_STATUSES["FAILED"]
CV_STATUS_COMPLETED = CV_STATUSES["COMPLETED"]

WEB_STATUSES = codes["web_status"]
WEB_STATUS_OK = WEB_STATUSES["OK"]
WEB_STATUS_INTERNAL_SERVER_ERROR = WEB_STATUSES["INTERNAL_SERVER_ERROR"]

OBJECT_DETECTION_EVENT_CANCEL = "OBJECT_DETECTION_EVENT_CANCEL"


def cv_api_url(route):
    return CV_API_ADDRESS + route


def web_api_url(route):
    return WEB_API_ADRESS + route


def async_get_request(url):
    def request(req_url):
        try:
            urlopen(req_url)
        except:
            log_error(traceback.format_exc())

    thread = Thread(target=request, args=(url,))
    thread.start()
    return thread


def video_metadata(video_id):

    video = db["videos"].find_one({"_id": ObjectId(video_id)})
    video_path = path.join(config["storage"]["videos"], video["filename"])

    thumbnail_dir = config["storage"]["thumbnails"]

    if not path.isfile(video_path):
        raise Exception("%s is not a file" % video_path)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    cap.set(cv2.CAP_PROP_POS_FRAMES, (frame_count/2)-1)
    res, frame = cap.read()
    random = str(uuid.uuid4())
    thumbnail_name = random + ".jpg"
    thumbnail_path = path.join(thumbnail_dir, thumbnail_name)
    cv2.imwrite(thumbnail_path, frame)
    cap.release()

    length = (frame_count/fps)*1000
    size = path.getsize(video_path)

    data = dict(
        length=length,
        size=size,
        fps=fps,
        frame_count=frame_count,
        width=width,
        height=height,
        thumbnail=thumbnail_name)

    return data


def format_route(literal, mapping, delimiters={"left": "<", "right": ">"}):
    pieces = literal.split("/")
    pieces = pieces[1:]
    arg_pattern = re.compile("^"+delimiters["left"]+".+"+delimiters["right"]+"$")

    for piece in pieces:
        if arg_pattern.match(piece):
            arg_name = piece[1:-1]
            if arg_name in mapping:
                val = mapping[arg_name]
                literal = literal.replace(piece, str(val))

    return literal
