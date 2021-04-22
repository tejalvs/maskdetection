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
        color = (0, 0, 255)
    else:
        color = (0, 255, 0)
    thickness = 1
    fScale = round(min([imageWidth,imageHeight])/25)
    img = cv2.rectangle(img,start_point, end_point,color,thickness)
    img = cv2.putText(img, "Confidence :"+ str(round(confidence,1))+"%", start_point, cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), thickness, cv2.LINE_AA)
    return img

def extractFaceDetails(bodyPart):
    confidence = 0.0
    maskStatus = False
    box = None
    if( "EquipmentDetections" in bodyPart):
        for equipement in bodyPart["EquipmentDetections"]:
            box = equipement["BoundingBox"]
            if( "CoversBodyPart" in equipement and "Confidence" in equipement["CoversBodyPart"]):
                confidence = equipement["CoversBodyPart"]["Confidence"]
                maskStatus = equipement["CoversBodyPart"]["Value"]
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
                                print("maskworn? ",maskStatus)
                                if(faceBoxDetails!= None):
                                    frame = showBoundingBoxPositionForFace(h,w,faceBoxDetails,frame,faceCoverConfidence,maskStatus)
                    cv2.imwrite("peopleWithBoundingBoxed.jpg", frame)
                    putImageInBucket()
            cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    while(True):
        captureImage()
        sleep(1)
