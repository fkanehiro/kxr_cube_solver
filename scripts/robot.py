def oppositeFace(f):
    opposite_face = {'F': 'B', 'B': 'F', 'U': 'D', 'D': 'U', 'L': 'R', 'R': 'L'}
    return opposite_face[f]

def surroundedFace(f1, f2):
    if (f1=='D' and f2=='R') or (f1=='R' and f2=='U') or (f1=='U' and f2=='L') or (f1=='L' and f2=='D'):
        return 'F'
    elif (f1=='D' and f2=='L') or (f1=='L' and f2=='U') or (f1=='U' and f2=='R') or (f1=='R' and f2=='D'):
        return 'B'
    elif (f1=='F' and f2=='U') or (f1=='U' and f2=='B') or (f1=='B' and f2=='D') or (f1=='D' and f2=='F'):
        return 'L'
    elif (f1=='F' and f2=='R') or (f1=='R' and f2=='B') or (f1=='B' and f2=='L') or (f1=='L' and f2=='F'):
        return 'U'
    elif (f1=='F' and f2=='L') or (f1=='L' and f2=='B') or (f1=='B' and f2=='R') or (f1=='R' and f2=='F'):
        return 'D'
    else:
        print("surroundedFace(): unexpected combination,",f1,"and",f2)
        return None

class gripper:
    def __init__(self, name, robot):
        self.angle = 0 # gripper yaw angle
        self.name = name
        self.robot = robot

    def release(self):
        self.robot.addCommand("(release %s)"%self.name)

    def grasp(self):
        self.robot.addCommand("(grasp %s)"%self.name)

    def setAngle(self, angle): # absolute angle
        self.angle = angle
        self.robot.addCommand("(angle %s %d)"%(self.name,angle))

    def regrasp(self, angle): # absolute angle
        if self.angle == angle:
            return
        self.release()
        self.setAngle(angle)
        self.grasp()

    def rotate(self, angle): # relative angle
        if angle == 180:
            if self.angle == 90:
                angle = -180
            elif self.angle == 0:
                self.regrasp(-90)
        elif angle == -180:
            if self.angle == -90:
                angle = 180
            elif self.angle == 0:
                self.regrasp(90)
        elif angle == 90 and self.angle == 90:
            self.regrasp(-90)
        elif angle == -90 and self.angle == -90:
            self.regrasp(90)
            
        self.setAngle(self.angle + angle)
    
class cubeSolver:
    def __init__(self):
        self.gripperR = gripper(":rarm", self)
        self.gripperL = gripper(":larm", self)
        self.command = ""
        self.initGraspingFaces()

    def initGraspingFaces(self):
        self.graspingFaces = {'L': 'D', 'R': 'R'}

    def addCommand(self, com):
        print(com)
        self.command += com

    def rotateCube(self, lr, angle):
        if lr == 'L':
            g1 = self.gripperL
            g2 = self.gripperR
        else:
            g1 = self.gripperR
            g2 = self.gripperL
        if angle == 180:
            g2.regrasp(0)
            a1 = 0
            a2 = -90
        elif angle == 90:
            a1 =  90
            a2 = -90
        elif angle == -90:
            a1 = -90
            a2 =  90
        if g1.angle == a1:
            g1.regrasp(a2)
        g2.release()
        if g1.angle +angle != 0 and g2.angle != 0:
            g2.setAngle(0)
        g1.rotate(angle)
        g2.grasp()

    def rotateFace(self, face, angle):
        if self.graspingFaces['R'] == face:
            self.gripperL.regrasp(0)
            self.gripperR.rotate(angle)
        elif self.graspingFaces['L'] == face:
            self.gripperR.regrasp(0)
            self.gripperL.rotate(angle)
        elif oppositeFace(self.graspingFaces['R']) == face:
            print(";; opposite R")
            self.rotateCube('L', 180)
            self.graspingFaces['R'] = face
            self.gripperL.regrasp(0)
            self.gripperR.rotate(angle)
        elif oppositeFace(self.graspingFaces['L']) == face:
            print(";; opposite L")
            self.rotateCube('R', 180)
            self.graspingFaces['L'] = face
            self.gripperR.regrasp(0)
            self.gripperL.rotate(angle)
        elif surroundedFace(self.graspingFaces['L'], self.graspingFaces['R']) == face:
            print(";; surrounded L and R")
            self.rotateCube('R', -90)
            self.graspingFaces['L'] = face
            self.gripperR.regrasp(0)
            self.gripperL.rotate(angle)
        elif surroundedFace(self.graspingFaces['R'], self.graspingFaces['L']) == face:
            print(";; surrounded R and L")
            self.rotateCube('R', 90)
            self.graspingFaces['L'] = face
            self.gripperR.regrasp(0)
            self.gripperL.rotate(angle)
        else:
            print("Error: rotateFace(",face,",",angle,"): unexpected state")

    def solveOneStep(self, op):
        print()
        print("operation:",op,", Left:(", self.gripperL.angle,",",self.graspingFaces['L'],"), Right:(",self.gripperR.angle,",",self.graspingFaces['R'],")")
        face = op[0]
        angle = 90
        if len(op) == 2:
            if op[1] == '2':
                angle = 180
            elif op[1] == '\'':
                angle = -90
        self.rotateFace(face, angle)
        
    def lookAt(self, faceId):
        if faceId == 'D':
            self.gripperL.release()
            self.gripperR.rotate(95)
        elif faceId == 'U':
            self.gripperR.rotate(-185)
        elif faceId == 'L':
            self.gripperR.rotate(90)
            self.gripperL.grasp()
            self.gripperR.release()
            self.gripperL.rotate(90)
        elif faceId == 'R':
            self.gripperL.rotate(-180)
        elif faceId == 'B':
            self.gripperR.grasp()
            self.gripperL.release()
            self.gripperL.rotate(90)
            self.gripperL.grasp()
            self.gripperR.release()
            self.gripperL.rotate(-90)
        elif faceId == 'F':
            self.gripperL.rotate(180)

    def finishScan(self):
        self.gripperR.grasp()
        self.gripperL.release()
        self.gripperL.rotate(-90)
        self.gripperL.grasp()

    def initDemo(self):
        self.addCommand("(send *ri* :hold)")
        self.addCommand("(init-pose)")

    def startDemo(self):
        self.gripperR.grasp()
        self.gripperL.grasp()

    def finishDemo(self):
        self.gripperR.regrasp(0)
        self.gripperL.regrasp(0)
        self.addCommand("(init-pose)")
