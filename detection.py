from ultralytics import YOLO
import asyncio
from datetime import datetime
from database import log_detection

TIME_DELAY = 10
recent_detections = {}

model = YOLO("yolov8s.pt")

async def cleanup_old_detections():
    """Remove entries in `recent_detections` older than TIME_DELAY"""
    now = datetime.now()
    for key, detection_time in list(recent_detections.items()):
        if (now - detection_time).total_seconds() > TIME_DELAY:
            del recent_detections[key]

async def detect_people(frame, image_filename=None):
    results = model(frame, classes=0)
    number_of_humans = 0

    for box in results[0].boxes:
        if box.conf > 0.5:
            number_of_humans += 1

    redundant_detection = False

    # Get the last detection time for the current number of humans, if it exists
    last_detection_time = recent_detections.get(number_of_humans)
    
    if last_detection_time is not None:
        delta = datetime.now() - last_detection_time
        if delta.total_seconds() < TIME_DELAY:
            redundant_detection = True

    # If no redundancy, log detection and update the dictionary
    if number_of_humans > 0 and not redundant_detection:
        await log_detection(number_of_humans)
        print(f"{number_of_humans} humans detected")
        recent_detections.update({number_of_humans: datetime.now()})

    # Clean up old detections asynchronously
    await cleanup_old_detections()
