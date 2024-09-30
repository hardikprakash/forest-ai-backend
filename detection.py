from ultralytics import YOLO

model = YOLO("yolov8n.pt")

async def detect_people(frame):
    results = model(frame, classes=0)
    number_of_humans = 0

    # for i in range(len(results[0].boxes)):
    #     if (results[0].boxes[i].conf[0].item() > 0.5):
    #         number_of_humans+=1

    for box in results[0].boxes:
        if box.conf > 0.5:  # confidence threshold of 0.5
            number_of_humans += 1

    if number_of_humans > 0:
        # async fxn call to log to database
        print(number_of_humans, "humans detected")
        pass

if __name__=='__main__':
    detect_people('./uploads/testimg2.jpg')