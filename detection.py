from ultralytics import YOLO
import asyncio
from database import log_detection

model = YOLO("yolov8s.pt")

async def detect_people(frame, image_filename=None):
    results = model(frame, classes=0)
    number_of_humans = 0

    for box in results[0].boxes:
        if box.conf > 0.5:
            number_of_humans += 1

    if number_of_humans > 0:
        await log_detection(number_of_humans)
        print(f"{number_of_humans} humans detected")
