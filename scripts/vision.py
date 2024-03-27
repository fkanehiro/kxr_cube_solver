import cv2
import numpy as np
import math
from helpers import ciede2000, bgr2lab
import config

def computeROIs(roi_center_x, roi_center_y, roi_size, roi_gap, roi_rotation):
    cth = math.cos(roi_rotation)
    sth = math.sin(roi_rotation)
    roi_step = roi_size+roi_gap
    rois = []
    for i in range(-1,2):
        dy = roi_step*i
        for j in range(-1,2):
            dx = roi_step*j
            x = roi_center_x + int(cth*dx - sth*dy - roi_size/2)
            y = roi_center_y + int(sth*dx + cth*dy - roi_size/2)
            rois.append((x,y))
    return rois

def getROI(frame, pos, size):
    return frame[pos[1]:pos[1]+size, pos[0]:pos[0]+size]

def faces2sequence(faces):
    return faces['U']+faces['R']+faces['F']+faces['D']+faces['L']+faces['B']

def checkFace(face):
    return face.count(-1) == 0

class cubeDetector:
    def __init__(self):
        # ROI for color detection
        self.roi_size = 70
        self.roi_gap = 40
        self.roi_rotation = math.pi/4
        self.rois = computeROIs(config.roi_center_x, config.roi_center_y, self.roi_size, self.roi_gap, self.roi_rotation)

        # display
        self.thickness = 2
        self.white = (255,255,255)
        self.font = cv2.FONT_HERSHEY_SIMPLEX

        self.initFaces()

    def initFaces(self):
        self.faces = {}
        self.faces['U'] = (-1,-1,-1,-1,-1,-1,-1,-1,-1)
        self.faces['F'] = (-1,-1,-1,-1,-1,-1,-1,-1,-1)
        self.faces['D'] = (-1,-1,-1,-1,-1,-1,-1,-1,-1)
        self.faces['B'] = (-1,-1,-1,-1,-1,-1,-1,-1,-1)
        self.faces['L'] = (-1,-1,-1,-1,-1,-1,-1,-1,-1)
        self.faces['R'] = (-1,-1,-1,-1,-1,-1,-1,-1,-1)

    def drawFace(self, frame, face, pos, size, gap):
        for i in range(9):
            if face[i] == -1:
                c = (0,0,0)
            else:
                c = config.colors[face[i]][1]
            x = pos[0] + (i%3)*(size+gap)
            y = pos[1] + int(i/3)*(size+gap)
            cv2.rectangle(frame, (x,y), (x+size,y+size), c, cv2.FILLED)

    def setFace(self, c, face):
        if not checkFace(face):
            print("face(",face,") is not valid")
            return False
        else:
            self.faces[c] = face
            return True

    def drawCube(self, frame):
        size = 15
        gap = 2
        face_step = size*3+gap*2+5
        start_x =  10
        start_y = 300
        positions = [(start_x +   face_step,start_y            ), #U
                     (start_x + 2*face_step,start_y+  face_step), #R
                     (start_x +   face_step,start_y+  face_step), #F
                     (start_x +   face_step,start_y+2*face_step), #D
                     (start_x              ,start_y+  face_step), #L 
                     (start_x + 3*face_step,start_y+  face_step)] #B
        order = ['U','R','F','D','L','B']
        for p, f in zip(positions, order):
            self.drawFace(frame, self.faces[f],  p, size, gap)

    def checkCube(self, faces):
        for f in faces.values():
            if not checkFace(f):
                return False
        cs = faces2sequence(faces)
        for i in range(6):
            if cs.count(i) != 9:
                print("Unexpected number of blocks(color=",config.colors[i][0],", n=",cs.count(i),")")
                return False
        return True

    def detectFace(self, frame):
        face = []
        for i,roi in enumerate(self.rois):
            img = getROI(frame, roi, self.roi_size)
            bgr = get_dominant_color(img)
            cc = get_closest_color(bgr, config.colors)
            for i,c in enumerate(config.colors):
                if cc["color_name"] == c[0]:
                    res = i
            face.append(res)
        return face

    def drawInfo(self, frame, face, msgs):
        # draw ROIs
        for roi in self.rois:
            x,y = roi
            cv2.rectangle(frame, roi, (x+self.roi_size, y+self.roi_size), self.white, self.thickness)
        # draw dection result
        self.drawFace(frame, face, (10,10), 50, 10)
        # draw cube state
        self.drawCube(frame)
        # draw messages
        y = 400
        for msg in msgs:
            cv2.putText(frame, msg, (600, y), self.font, 0.5, self.white, 2)
            y += 20

    def saveROIs(self,frame):
        for i,r in enumerate(self.rois):
            img = getROI(frame, r, self.roi_size)
            cv2.imwrite(str(i)+".png", img)
        print("saved")

# taken from https://github.com/kkoomen/qbr/blob/master/src/colordetection.py

def get_dominant_color(roi):
    """
    Get dominant color from a certain region of interest.

    :param roi: The image list.
    :returns: tuple
    """
    pixels = np.float32(roi.reshape(-1, 3))

    n_colors = 1
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
    flags = cv2.KMEANS_RANDOM_CENTERS
    _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
    _, counts = np.unique(labels, return_counts=True)
    dominant = palette[np.argmax(counts)]
    return tuple(dominant)

def get_closest_color(bgr, colors):
    """
    Get the closest color of a BGR color using CIEDE2000 distance.

    :param bgr tuple: The BGR color to use.
    :returns: dict
    """
    lab = bgr2lab(bgr)
    distances = []
    for color_name, color_bgr in colors:
        distances.append({
            'color_name': color_name,
            'color_bgr': color_bgr,
            'distance': ciede2000(lab, bgr2lab(color_bgr))
        })
    closest = min(distances, key=lambda item: item['distance'])
    return closest

