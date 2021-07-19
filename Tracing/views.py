from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from datetime import datetime, date, timedelta
from django.conf import settings
from Tracing.PlateFinder import PlateFinder
from Tracing.PlateProcessing import plate_with_dark_color_background, plate_with_white_background
from keras.models import model_from_json
from sklearn.preprocessing import LabelEncoder
import numpy as np
import json
import glob
import cv2


NUMBER_OF_CAMERAS = 16
cityCamerasNetwork = [
    [],
    [2, 3, 4],
    [1, 3, 7],
    [1, 2, 4, 5, 6],
    [1, 3, 5, 8],
    [3, 4, 9, 10],
    [3, 7, 10, 11],
    [2, 6, 11],
    [4, 9],
    [5, 8, 15, 16],
    [5, 6, 12, 15],
    [6, 7, 12, 13],
    [10, 11, 13, 15],
    [11, 12, 14],
    [13, 15, 16],
    [9, 10, 12, 14, 16],
    [9, 14, 15]
]

bfs_traversal = []
# nodeToTimeStampMapping = {}

# # function to set some base timestamp to each node
# def set_base_time_with_each_camera_node():
#     visited = [0]*(NUMBER_OF_CAMERAS+1)
#     today = date.today()
#     yesterday = today - timedelta(days = 1)
#     baseTimeStamp = datetime(yesterday.year, yesterday.month, yesterday.day, 10, 0, 0)

#     startNode = 1
#     nodeToTimeStampMapping[startNode] = str(baseTimeStamp)

#     queue = []
#     queue.append({startNode: baseTimeStamp})
#     visited[startNode] = 1

#     while len(queue) > 0:
#         nodeDetails = queue.pop(0)
#         node = list(nodeDetails.keys())[0]
#         nodeTimeStamp = nodeDetails[node]
        

#         for i in range(len(cityCamerasNetwork[node])):
#             if not visited[cityCamerasNetwork[node][i]]:
#                 newTimeStamp = nodeTimeStamp + timedelta(minutes= 10)
#                 nodeToTimeStampMapping[cityCamerasNetwork[node][i]] = str(newTimeStamp)
#                 queue.append({cityCamerasNetwork[node][i]: newTimeStamp})
#                 visited[cityCamerasNetwork[node][i]] = 1

#     # print(nodeToTimeStampMapping)


def bfs_of_camera_structure():
    visited = [0]*(NUMBER_OF_CAMERAS+1)
    startNode = 1
    
    queue = []
    queue.append(startNode)
    visited[startNode] = 1

    while len(queue) > 0:
        node = queue.pop(0)
        bfs_traversal.append(node)

        for i in range(len(cityCamerasNetwork[node])):
            if not visited[cityCamerasNetwork[node][i]]:
                queue.append(cityCamerasNetwork[node][i])
                visited[cityCamerasNetwork[node][i]] = 1
    
    # print(bfs_traversal)



# set_base_time_with_each_camera_node()
bfs_of_camera_structure()
findPlate = PlateFinder()


# Load pretrained OCR model architecture, weight and labels
json_file = open(settings.BASE_DIR + '/pretrained_OCR/MobileNets_character_recognition.json', 'r')
loaded_model_json = json_file.read()
json_file.close()

model = model_from_json(loaded_model_json)
model.load_weights(settings.BASE_DIR + '/pretrained_OCR/License_character_recognition_weight.h5')
print("[INFO] Model loaded successfully...")

labels = LabelEncoder()
labels.classes_ = np.load(settings.BASE_DIR + '/pretrained_OCR/license_character_classes.npy')
print("[INFO] Labels loaded successfully...")




def homepage(request):
    return render(request, 'Tracing/index.html')



# function to handle trace vehicle path request
@csrf_exempt
def getVehiclePath(request):
    if request.method == 'POST':

        # extracting form data coming from ajax request
        json_data = json.loads(request.POST['data'])
        licensePlateNumber = json_data['licensePlateNumber']
 
        # response object to return as response to ajax request
        context = {
            'isSuccessful': '',
            'vehiclePath': [],
        }

        # RESULT DICTIONARY WITH TIMESTAMPS
        vehiclePath = {}
        today = date.today()
        yesterday = today - timedelta(days = 1)
        baseTimeStamp = datetime(yesterday.year, yesterday.month, yesterday.day, 10, 0, 0)


        # Iterating through all the camera nodes
        # for video_path in sorted(glob.glob(settings.BASE_DIR + '/cameraClips/*')):
        for video_name in bfs_traversal:
            video_path = settings.BASE_DIR + '/cameraClips/' + str(video_name) + '.mp4' 
            print(video_path)
            # video_name = (video_path.split('.')[0]).split('/')[-1]

            cap = cv2.VideoCapture(video_path)
            frames_count = 0
            isMatchFound = 0
            while cap.isOpened():
                ret, img = cap.read()
                if ret:
                    frames_count += 1
                    if frames_count % 20 == 1:
                        possible_plates = findPlate.find_possible_plates(img)
                        if possible_plates is not None:
                            for i, plate in enumerate(possible_plates):
                                plate_rgb = plate
                                
                                # convert to grayscale and blur the image
                                plate_gray = cv2.cvtColor(plate_rgb, cv2.COLOR_BGR2GRAY)

                                predicted_number_plate_value = plate_with_dark_color_background(plate_rgb, plate_gray, model, labels)
                                if predicted_number_plate_value == licensePlateNumber:
                                    isMatchFound = 1
                                    break

                                predicted_number_plate_value = plate_with_white_background(plate_rgb, plate_gray, model, labels)
                                if predicted_number_plate_value == licensePlateNumber:
                                    isMatchFound = 1
                                    break


                            if isMatchFound:
                                break        
                else:
                    break
            cap.release()
            cv2.destroyAllWindows()

            if isMatchFound:
                print('found', video_name)
                # vehiclePath[video_name] = nodeToTimeStampMapping[int(video_name)]
                vehiclePath[video_name] = str(baseTimeStamp)
                newTimeStamp = baseTimeStamp + timedelta(minutes= 10)
                baseTimeStamp = newTimeStamp

            else:
                print('not_found', video_name)

        sortedVehiclePath = sorted(vehiclePath.items(), key=lambda x: x[1])
        # print(sortedVehiclePath)

        context['vehiclePath'] = sortedVehiclePath
        context['isSuccessful'] = 'Results Found!!'
        return JsonResponse(context)
    else:
        return render(request, 'templates/404.html')