import cv2
import traceback
import darknet
from db import db
from bson.objectid import ObjectId
from threading import Thread
from logger import *
from event_emmiter import event_emmiter
import sys
from util import async_get_request
from util import format_route
from config_loader import config
from os import path


class TerminatedByUserError(Exception):
    pass


PROGRESS_ROUTE = config["cv_api"]["route"]["object_detection"]["feedback"]["progress"]
TERMINATION_INFORMATION_ROUTE = config["cv_api"]["route"]["object_detection"]["feedback"]["termination_information"]
WEB_API_ADRESS = "http://" + config["web_api"]["host"]+":"+str(config["web_api"]["port"])


class ObjectDetection:
    def __init__(self, operation_id, video_id):
        self._operation_id = operation_id
        self._terminate_asap = False
        self._video_id = video_id
        self._video_dir = config["storage"]["video"]

    def _update_progress(self, progress):
        db.update_one("videos", {"$set": {"object_detection_progress": progress}}, {"_id": ObjectId(self._video_id)})

        if not PROGRESS_ROUTE is "":
            fill = {"operation_id": self._operation_id, "progress": progress}
            async_get_request(WEB_API_ADRESS + format_route(PROGRESS_ROUTE, fill))

    def _inform_termination(self, status):
        if not TERMINATION_INFORMATION_ROUTE is "":
            fill = {"operation_id": self._operation_id, "status": status}
            async_get_request(WEB_API_ADRESS + format_route(TERMINATION_INFORMATION_ROUTE, fill))

    def _update_status(self, status):
        db.update_one("videos", {"$set": {"object_detection_status": status}}, {"_id": ObjectId(self._video_id)})

    def detect(self):
        try:
            def termination_handler(data):
                if data["operation_id"] == self._operation_id:
                    self._terminate_asap = True

            event_emmiter.on("TERMINATE_OBJECT_DETECTION", termination_handler)

            video = db.find_one("videos", {"_id": ObjectId(self._video_id)})
            video_path = path.join(self._video_dir, video["filename"])
            cap = cv2.VideoCapture(video_path)

            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)

            self._update_progress(0)

            old_percentage = 0

            while(cap.isOpened()):
                if self._terminate_asap:
                    raise TerminatedByUserError()

                ret, frame = cap.read()

                if not ret or frame is None:
                    break

                frame_no = cap.get(cv2.CAP_PROP_POS_FRAMES)
                result = darknet.detect(darknet.net, darknet.meta, frame)

                percentage = int(frame_no/frame_count*100)

                detected_objects = [{"class": o[0],
                                     "confidence":round(o[1], 2),
                                     "x":o[2][0],
                                     "y":o[2][1],
                                     "w":o[2][2],
                                     "h":o[2][3],
                                     "frame_no":int(frame_no),
                                     "video_id":ObjectId(self._video_id)} for o in result]

                if old_percentage != percentage:
                    self._update_progress(percentage)
                old_percentage = percentage

                if len(detected_objects) > 0:
                    db.insert_many("detected_objects", detected_objects)

            cap.release()
            self._update_status("COMPLETED")
            self._update_progress(100)
        except TerminatedByUserError:
            self._inform_termination("OK")
            db.delete_many("detected_objects", {"video_id": ObjectId(self._video_id)})
            self._update_status("INTERRUPTED")
            log_error("Operation was terminated by user.")
        except:
            db.delete_many("detected_objects", {"video_id": ObjectId(self._video_id)})
            self._update_status("ERROR")
            log_error(traceback.format_exc())
