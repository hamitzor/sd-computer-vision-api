"""
python3 src/object_detection.py --mongodb-host localhost --mongodb-user sdadmin --mongodb-password root --video-id 5d034c09c78a738ec7f36dc9
"""

import json
import argparse
from db import DB
from object_detection import detect_objects_in_video
import threading
from bottle import route, run, template, response, request
import traceback
from urllib.request import urlopen
from urllib.parse import urlencode, quote_plus


argparse = argparse.ArgumentParser()
argparse.add_argument("-dbh", "--mongodb-host", required=True, help="MongoDB host")
argparse.add_argument("-dbu", "--mongodb-user", required=True, help="MongoDB username")
argparse.add_argument("-dbp", "--mongodb-password", required=True, help="MongoDB password")
argparse.add_argument("-p", "--port", default=8000, help="Server port", type=int)


args = argparse.parse_args()

db = DB(args.mongodb_user, args.mongodb_password, args.mongodb_host)

old_percentage = -1


@route('/start-object-detection/<video_id:path>/<progress_endpoint:path>')
def detect_objects(video_id, progress_endpoint):
    response.content_type = 'application/json; charset=UTF-8'

    video = db.get_video(video_id)

    video_path = video["path"]

    def handle_error(err_message):
        db.delete_detected_objects(video_id)
        db.update_video(video_id, {"object_detection_status": "ERROR"})
        db.insert_log("error", err_message)

    def handle_result(percentage, detected_objects):
        if len(detected_objects) > 0:
            for detected_object in detected_objects:
                detected_object["video_id"] = video_id
            db.insert_detected_objects(detected_objects)

        global old_percentage

        if(old_percentage != percentage):
            urlopen(progress_endpoint + "/" + video_id + "/" + str(percentage))
            db.update_video(video_id, {"object_detection_progress": percentage})

        old_percentage = percentage

    def handle_complete():
        db.update_video(video_id, {"object_detection_status": "COMPLETED"})

    thread = threading.Thread(target=detect_objects_in_video, args=(video_path, handle_result, handle_complete, handle_error))
    db.update_video(video_id, {"object_detection_status": "STARTED"})
    thread.start()

    return json.dumps({"status": "OK"})


if __name__ == "__main__":
    run(host='localhost', port=args.port)
