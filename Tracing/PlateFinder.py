import cv2
import numpy as np



class PlateFinder:
    def __init__(self):
        self.min_area = 3500  # minimum area of the plate
        self.max_area = 25000  # maximum area of the plate

        self.element_structure = cv2.getStructuringElement(shape=cv2.MORPH_RECT, ksize=(22, 3))


    def preprocess(self, image):

        image = cv2.GaussianBlur(image, (7, 7), 0)
        g = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        g = cv2.bilateralFilter(g, 13, 15, 15)
        edge = cv2.Canny(g, 60, 180)
        
        return edge


    def extract_contours(self, after_preprocess, input_img):
        contours, _ = cv2.findContours(after_preprocess, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_NONE)
        
        return contours


    def clean_plate(self, plate):
        gray = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)


        if contours:
            areas = [cv2.contourArea(c) for c in contours]
            max_index = np.argmax(areas)  # index of the largest contour in the area array

            max_cnt = contours[max_index]
            max_cntArea = areas[max_index]
            x, y, w, h = cv2.boundingRect(max_cnt)
            rect = cv2.minAreaRect(max_cnt)

            rotatedPlate = plate
            return plate, True, [x, y, w, h]
        else:
            return plate, False, None



    def check_plate(self, input_img, contour):
        min_rect = cv2.minAreaRect(contour)
        if self.validateRatio(min_rect, input_img, contour):
            x, y, w, h = cv2.boundingRect(contour)
            ratio = float(w) / float(h)
            ratioMin = 2.5
            ratioMax = 7
            if (ratio < ratioMin or ratio > ratioMax):
                return None, None, None

            orig_height, orig_width, orig_channels = input_img.shape

            after_validation_img = input_img[max(y - 5, 0):min(y + h + 5, orig_height), max(x - 5, 0):min(x + w + 5, orig_width)]

            after_clean_plate_img, plateFound, coordinates = self.clean_plate(after_validation_img)
            if plateFound:
                characters_on_plate = ''

                if True:
                    x1, y1, w1, h1 = coordinates
                    coordinates = x1 + x, y1 + y
                    after_check_plate_img = after_clean_plate_img
                    return after_check_plate_img, characters_on_plate, coordinates
        return None, None, None



    def find_possible_plates(self, input_img):
        """
        Finding all possible contours that can be plates
        """
        plates = []
        self.char_on_plate = []
        self.corresponding_area = []

        self.after_preprocess = self.preprocess(input_img)
        possible_plate_contours = self.extract_contours(self.after_preprocess, input_img)


        for cnts in possible_plate_contours:
            plate, characters_on_plate, coordinates = self.check_plate(input_img, cnts)
            if plate is not None:
                plates.append(plate)
                self.char_on_plate.append(characters_on_plate)
                self.corresponding_area.append(coordinates)

        if (len(plates) > 0):
            return plates
        else:
            return None

    
    def preRatioCheck(self, area, width, height):
        min = self.min_area
        max = self.max_area

        ratioMin = 2.5
        ratioMax = 7

        ratio = float(width) / float(height)
      
        if (area < min or area > max) or (ratio < ratioMin or ratio > ratioMax):
            return False
        return True

    def validateRatio(self, rect, input_img, contour):
        (x, y), (width, height), rect_angle = rect
        x, y, w, h = cv2.boundingRect(contour)

        if (width > height):
            angle = -rect_angle
        else:
            angle = 90 + rect_angle

        if (height == 0 or width == 0):
            return False

        area = width * height
        area = w * h
        if not self.preRatioCheck(area, w, h):
            return False
        else:
            return True