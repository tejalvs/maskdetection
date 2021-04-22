import cv2
import numpy as np
import youtube_dl
import boto3
import math
from time import sleep

def showBoundingBoxPositionsForEachPerson(imageHeight, imageWidth, box, img): 
    left = imageWidth * box['Left']
    top = imageHeight * box['Top']
    start_point = (int(left), int(top))
    end_point = (math.ceil(left + (imageWidth*box['Width'])), math.ceil(top + (imageHeight*box['Height'])))
    color = (0, 0, 0)
    thickness = 2
    img = cv2.rectangle(img,start_point, end_point,color,thickness)
    return img

def showBoundingBoxPositionForFace(imageHeight, imageWidth, box, img, confidence ,maskStatus):
    left = imageWidth * box['Left']
    top = imageHeight * box['Top']
    start_point = (int(left), int(top))
    end_point = (math.ceil(left + (imageWidth*box['Width'])), math.ceil(top + (imageHeight*box['Height'])))
    if(maskStatus == "true"):
        color = (0, 255, 0)
    else:
        color = (0, 0, 255)
    thickness = 2
    img = cv2.rectangle(img,start_point, end_point,color,thickness)
    img = cv2.putText(img, "Confidence :"+ str(confidence), start_point, cv2.FONT_HERSHEY_SIMPLEX, 
                   1, color, thickness, cv2.LINE_AA)
    return img

def extractFaceDetails(bodyPart):
    print(bodyPart)
    confidence = 0.0
    maskStatus = False
    box = None
    print(bodyPart["EquipmentDetections"].keys())
    if( "EquipmentDetections" in bodyPart and "BoundingBox" in bodyPart["EquipmentDetections"]):
        box = bodyPart["EquipmentDetections"]["BoundingBox"]
        if( CoversBodyPart in bodyPart["EquipmentDetections"] and "Confidence" in bodyPart["EquipmentDetections"]["CoversBodyPart"]):
            confidence = bodyPart["EquipmentDetections"]["CoversBodyPart"]["Confidence"]
            maskStatus = bodyPart["EquipmentDetections"]["CoversBodyPart"]["Value"]
    return box,confidence,maskStatus

def putImageInBucket():
    s3Bucket = boto3.client('s3', region_name='us-east-1')
    s3Bucket.upload_file("peopleWithBoundingBoxed.jpg", "wegmansmaskdetection", "peopleWithBoundingBoxes.jpg")

def captureImage():
    video_url = 'https://www.youtube.com/watch?v=oIBERbq2tLA'

    ydl_opts = {}
    ydl = youtube_dl.YoutubeDL(ydl_opts)
    try:
        ydl.cache.remove()
        info_dict = ydl.extract_info(video_url, download=False)
    except youtube_dl.DownloadError as error:
        pass
    formats = info_dict.get('formats',None)
    for f in formats:
        if(f["height"] == 720):
            url = f['url']
            cap = cv2.VideoCapture(url)
            ret, videoFrame = cap.read()
            frame = videoFrame.copy()
            if ret:
                hasFrame, imageBytes = cv2.imencode(".jpg", frame)
                if hasFrame:
                    session = boto3.session.Session()
                    rekognition = session.client('rekognition', region_name='us-east-1')
                    response = rekognition. detect_protective_equipment(
                            Image={
                                'Bytes': imageBytes.tobytes(),
                            }
                        )
                    for i in range(len(response['Persons'])):
                        person = response['Persons'][i]
                        h, w, c = frame.shape
                        frame = showBoundingBoxPositionsForEachPerson(h,w,person["BoundingBox"],frame)
                        for i in range(len(person["BodyParts"])):
                            bodyPart = person["BodyParts"][i]
                            if("Name" in bodyPart and bodyPart["Name"] == "FACE"):
                                faceBoxDetails,faceCoverConfidence,maskStatus = extractFaceDetails(bodyPart)
                                print(faceBoxDetails,faceCoverConfidence,maskStatus)
                                if(faceBoxDetails!= None):
                                    frame = showBoundingBoxPositionForFace(h,w,faceBoxDetails,frame,faceCoverConfidence,maskStatus)
                    cv2.imwrite("peopleWithBoundingBoxed.jpg", frame)
                    putImageInBucket()
            cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
#     while(True):
#         captureImage()
#         sleep(1)
    bodyPart = {'Name': 'FACE', 'Confidence': 94.63019561767578, 'EquipmentDetections': [{'BoundingBox': {'Width': 0.021624954417347908, 'Height': 0.04056299477815628, 'Left': 0.004337030928581953, 'Top': 0.6144181489944458}, 'Confidence': 97.91883850097656, 'Type': 'FACE_COVER', 'CoversBodyPart': {'Confidence': 99.0463638305664, 'Value': True}}]}
    faceBoxDetails,faceCoverConfidence,maskStatus = extractFaceDetails(bodyPart)
