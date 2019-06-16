import cv2
import traceback
import darknet
from db import db
from bson.objectid import ObjectId
from threading import Thread
from logger import *
from urllib.request import urlopen
from event_emmiter import event_emmiter
import sys


class ObjectDetection:
    def __init__(self, video_id, progress_endpoint):
        self._terminate_asap = False
        self._video_id = video_id
        self._progress_endpoint = progress_endpoint

    def terminate_asap(self):
        self._terminate_asap = True

    def _update_progress(self, progress):
        db.update_one("videos", {"$set": {"object_detection_progress": progress}}, {"_id": ObjectId(self._video_id)})
        Thread(target=lambda: urlopen(self._progress_endpoint + "/" + self._video_id + "/" + str(progress))).start()

    def _update_status(self, status):
        db.update_one("videos", {"$set": {"object_detection_status": status}}, {"_id": ObjectId(self._video_id)})

    def detect(self):
        try:
            self._update_status("STARTED")
            video = db.find_one("videos", {"_id": ObjectId(self._video_id)})
            path = video["path"]

            cap = cv2.VideoCapture(path)

            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)

            self._update_progress(0)

            old_percentage = 0

            while(cap.isOpened()):
                if self._terminate_asap:
                    raise RuntimeError("terminated by user")

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
        except:
            db.delete_many("detected_objects", {"video_id": ObjectId(self._video_id)})
            self._update_status("ERROR")
            log_error(traceback.format_exc())
