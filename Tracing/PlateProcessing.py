import cv2
import numpy as np



# pre-processing input images and pedict with model
def predict_from_model(image, model, labels):
    image = cv2.resize(image, (80, 80))
    image = np.stack((image,) * 3, axis=-1)
    prediction = labels.inverse_transform([np.argmax(model.predict(image[np.newaxis, :]))])
    return prediction



# Create sort_contours() function to grab the contour of each digit from left to right
def sort_contours(cnts, reverse=False):
    i = 0
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
                                        key=lambda b: b[1][i], reverse=reverse))
    return cnts



def character_recognition(crop_characters, model, labels):
    final_string = ''
    for i, character in enumerate(crop_characters):
        title = np.array2string(predict_from_model(character, model, labels))
        final_string += title.strip("'[]")

    return final_string



def contour_detection_and_character_segmentation(plate_rgb, plate_binary, white_background):
    """sort contour on the basis of their starting left and top coordinates """

    if white_background:
        rows, cols = plate_binary.shape
        for j in range(cols):
            count_of_black_pixels = 0
            for i in range(rows):
                if plate_binary[i, j] == 0:
                    count_of_black_pixels += 1
        
            if count_of_black_pixels >= rows/3:
                break
            else:
                for i in range(rows):
                    plate_binary[i, j] = 0


    cont, _ = cv2.findContours(plate_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # create a copy version "test_roi" of plat_image to draw bounding box
    test_roi = plate_rgb.copy()

    crop_characters = []

    # define standard width and height of character
    digit_w, digit_h = 30, 60

    
    if not white_background:
        if len(cont) > 0:
            # add for loop here with height and width condition
            for con in cont:
                (x, y, w, h) = cv2.boundingRect(con)
                ratio = h / plate_rgb.shape[0]
                area = w * h
                
                if ratio >= 0.9 or area > 5000:
                    cv2.drawContours(plate_binary, con, -1, (0, 0, 0), 5)
                    

        cont, _ = cv2.findContours(plate_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


    if len(cont) > 0:
        for c in sort_contours(cont):
            (x, y, w, h) = cv2.boundingRect(c)
            ratio = h / w
            if 0.8 <= ratio <= 4.5:  # Only select contour with defined ratio
                if h / plate_rgb.shape[0] >= 0.2 and h > 10:  # Select contour which has the height larger than 50% of the plate
                    # Draw bounding box around digit number
                    cv2.rectangle(test_roi, (x, y), (x + w, y + h), (0, 255, 0), 2)

                    # Sperate number and gibe prediction
                    curr_num = plate_binary[y:y + h, x:x + w]
                    curr_num = cv2.resize(curr_num, dsize=(digit_w, digit_h))
                    _, curr_num = cv2.threshold(curr_num, 220, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                    crop_characters.append(curr_num)

    return crop_characters


def plate_with_white_background(plate_rgb, input_img, model, labels):
    plate_gray = input_img.copy()

    rows, cols = plate_gray.shape

    for i in range(rows):
        for j in range(cols):
            if plate_gray[i, j] > 100:
                plate_gray[i, j] = 255
            else:
                plate_gray[i, j] = 0

    plate_binary = cv2.threshold(plate_gray, 180, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    crop_characters = contour_detection_and_character_segmentation(plate_rgb, plate_binary, 1)
    final_string = character_recognition(crop_characters, model, labels)

    return final_string



def plate_with_dark_color_background(plate_rgb, input_img, model, labels):
    plate_gray = input_img.copy()

    rows, cols = plate_gray.shape

    for i in range(rows):
        for j in range(cols):
            if plate_gray[i, j] > 160:
                plate_gray[i, j] = 255
            else:
                plate_gray[i, j] = 0

    plate_binary = cv2.threshold(plate_gray, 180, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    crop_characters = contour_detection_and_character_segmentation(plate_rgb, plate_binary, 0)
    final_string = character_recognition(crop_characters, model, labels)

    return final_string