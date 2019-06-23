import cv2
import traceback
import darknet
from mongo import db
from bson.objectid import ObjectId
from threading import Thread
from logger import *
from event_emmiter import event_emmiter
import sys
from util import *
from config_loader import config
from os import path


class CanceledByUserError(Exception):
    pass


FEEDBACK_ROUTES = config["web_api"]["route"]["cv_feedback"]
FEEDBACK_SUB_ROUTE = FEEDBACK_ROUTES["sub_route"]
PROGRESS_ROUTE = FEEDBACK_SUB_ROUTE + FEEDBACK_ROUTES["object_detection_progress"]
STATUS_ROUTE = FEEDBACK_SUB_ROUTE + FEEDBACK_ROUTES["object_detection_status"]


class ObjectDetection:
    def __init__(self, video_id):
        self._cancel_asap = False
        self._video_id = video_id
        self._video_dir = config["storage"]["videos"]

    def _update_progress(self, progress):
        if not PROGRESS_ROUTE is "":
            fill = {"video_id": self._video_id, "progress": progress}
            async_get_request(web_api_url(format_route(PROGRESS_ROUTE, fill)))

    def _update_status(self, status):
        if not STATUS_ROUTE is "":
            fill = {"video_id": self._video_id, "status": status}
            async_get_request(web_api_url(format_route(STATUS_ROUTE, fill)))

    def detect(self):
        try:
            self._update_status(CV_STATUS_STARTED)

            def cancellation_handler(data):
                if data["video_id"] == self._video_id:
                    self._cancel_asap = True

            event_emmiter.on(OBJECT_DETECTION_EVENT_CANCEL, cancellation_handler)

            video = db["videos"].find_one({"_id": ObjectId(self._video_id)})
            video_path = path.join(self._video_dir, video["filename"])
            cap = cv2.VideoCapture(video_path)

            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)

            self._update_progress(0)

            old_percentage = 0

            while(cap.isOpened()):
                if self._cancel_asap:
                    raise CanceledByUserError()

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
                                     "h":o[2][3]} for o in result]

                if old_percentage != percentage:
                    self._update_progress(percentage)
                old_percentage = percentage
                if len(detected_objects) > 0:
                    inserted_ids = db["detected_objects"].insert_many(detected_objects).inserted_ids
                    db["videos"].update_one({"_id": ObjectId(self._video_id)}, {"$push": {"object_detection.detections."+str(int(frame_no)): {"$each": inserted_ids}}}, upsert=True)
            cap.release()
            self._update_status(CV_STATUS_COMPLETED)
            self._update_progress(100)
        except CanceledByUserError:
            self._update_status(CV_STATUS_CANCELED)
            db["detected_objects"].delete_many({"video_id": ObjectId(self._video_id)})
            log_error("Object detection was canceled by user.")
        except:
            db["detected_objects"].delete_many({"video_id": ObjectId(self._video_id)})
            self._update_status(CV_STATUS_FAILED)
            log_error(traceback.format_exc())
