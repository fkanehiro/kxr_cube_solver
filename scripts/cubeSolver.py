#!/usr/bin/env python3

import rospy
from kxr_rubik_test.srv import SendCommand, SendCommandRequest
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge, CvBridgeError
import cv2
import vision
import robot
import kociemba
import random
from threading import Thread
import subprocess

def sendCommand(robot):
    srv_name = "/roseus_command_server/send_command"
    try:
        rospy.wait_for_service(srv_name)
        srv_prox = rospy.ServiceProxy(srv_name, SendCommand)
        req = SendCommandRequest()
        req.command = "(progn "+robot.command+")"
        robot.command = ""
        res = srv_prox(req)
        return res
    except rospy.ServiceException as e:
        print("Service call failed: %s"%e)
        return None

def speak(msg):
    subprocess.run("echo %s | open_jtalk -m /usr/share/hts-voice/mei/mei_normal.htsvoice -x /var/lib/mecab/dic/open-jtalk/naist-jdic/ -ow /tmp/voice.wav"%msg, shell=True)
    subprocess.run("aplay /tmp/voice.wav", shell=True)

def cube2string(faces):
    indexes = vision.faces2sequence(faces)
    print("indexes:",indexes)
    colorIndex2character = {}
    for k,v in faces.items():
        colorIndex2character[v[4]] = k
    ret = ""
    for i in indexes:
        ret += colorIndex2character[i]
    return ret

class cubeSolverFSM:
    def __init__(self):
        self.transitTo("init", 0)
        self.autoTransition = False
        self.start = True
        self.finish = False
        self.scanFaceOrder = ('D','U','L','R','B','F')
        self.solveOperations = None
        self.robot = robot.cubeSolver()
        self.vision = vision.cubeDetector()
        self.faceDetectionCount = 0
        self.maxFaceDetectionCount = 10
        self.tips = ("ルービックキューブは今年で５０周年です。",
                     "ルービックキューブはどんな状態からでも20手以内で解けることが知られています。",
                     "ルービックキューブを解くアルゴリズムは複数あるのですが、私はコシエンバのアルゴリズムを使っています。",
                     "人間によるルービックキューブの世界最速記録は3.13秒です。",
                     "ロボットによる最速記録はなんと0.38秒です。でも手が6本必要です。",
                     "ガンロボットは5本の手で5秒以内でルービックキューブを解くことができます。1万円くらいで買えます。")
        self.tipsIndex = 0
        self.speakProc = None
        self.moveProc = None

    def speak(self, msg):
        self.speakProc = Thread(target=speak, args=(msg,))
        self.speakProc.start()

    def move(self):
        self.moveProc = Thread(target=sendCommand, args=(self.robot,))
        self.moveProc.start()

    def run(self, frame):
        # face detection
        face = self.vision.detectFace(frame)

        msgs = ("state="+self.state+":"+str(self.index)+"/"+str(self.maxIndex),
                "autoTransition="+str(self.autoTransition),
                "finish="+str(self.finish))
        self.vision.drawInfo(frame, face, msgs)
        cv2.imshow('Video', frame)

        if self.state == "init":
            if self.start:
                self.robot.initDemo()
                self.move()
                self.speak("ルービックキューブを手の上に置いてください。")
                self.start = False
            elif not self.isMoving():
                self.finish = True
        if self.state == "start":
            if self.start:
                self.speak("まずは、ルービックキューブの状態を見てみます。")
                self.robot.startDemo()
                self.move()
                self.vision.initFaces()
                self.robot.initGraspingFaces()
                self.tipsIndex = 0
                self.start = False
            elif not self.isMoving():
                self.finish = True
        elif self.state == "scan":
            if self.index == self.maxIndex:
                if self.start:
                    self.robot.finishScan()
                    self.move()
                    self.start = False
                elif not self.isMoving():
                    self.finish = True
            else:
                faceId = self.scanFaceOrder[int(self.index/2)]
                if self.index%2 == 0:
                    if self.start:
                        self.robot.lookAt(faceId)
                        self.move()
                        self.faceDetectionCount = 0
                        self.start = False
                    elif not self.isMoving():
                        self.finish = True
                else:
                    if vision.checkFace(face):
                        if self.vision.faces[faceId] == face:
                            self.faceDetectionCount += 1
                        else:
                            self.faceDetectionCount = 0
                        if self.faceDetectionCount >= self.maxFaceDetectionCount:
                            self.finish = True
                        self.vision.setFace(faceId, face)
                    else:
                        self.faceDetectionCount = 0
                    print("faceDetectionCount=",self.faceDetectionCount)
        elif self.state == "solve":
            if self.start:
                if not self.isSpeaking():
                    r = random.random()
                    if r > 0.5:
                        if self.tipsIndex < len(self.tips):
                            self.speak(self.tips[self.tipsIndex])
                            self.tipsIndex += 1
                        else:
                            self.speak("あと"+str(len(self.solveOperations)-self.index)+"手です。")
                self.robot.solveOneStep(self.solveOperations[self.index])
                self.move()
                self.start = False
            if not self.isMoving():
                self.finish = True
        elif self.state == "end":
            if not self.finish and not self.isSpeaking():
                self.speak("完成しました")
                self.robot.finishDemo()
                sendCommand(self.robot)
                self.autoTransition = False
                self.finish = True

        if self.autoTransition:
            self.stateTransition()

    def isSpeaking(self):
        return self.speakProc.is_alive()

    def isMoving(self):
        return self.moveProc.is_alive()

    def transitTo(self, state, maxIndex=0):
        self.state = state
        self.index = 0
        self.maxIndex = maxIndex
        self.start = True

    def stateTransition(self):
        if not self.finish:
            return
        self.finish = False
        if self.state == "init":
            self.transitTo("start")
        elif self.state == "start":
            self.transitTo("scan", len(self.scanFaceOrder)*2)
        elif self.state == "scan":
            if self.index == self.maxIndex:
                if self.vision.checkCube(self.vision.faces):
                    print ("faces:",self.vision.faces)
                    s = cube2string(self.vision.faces)
                    print ("cube state:",s)
                    s = kociemba.solve(s)
                    self.solveOperations = s.split(' ')
                    print ("solution:",self.solveOperations)
                    self.speak("解き方がわかりました｡"+str(len(self.solveOperations))+"手で解けます。")
                    self.transitTo("solve", len(self.solveOperations)-1)
                else:
                    print("detected cube state is invalid, rescan is necessary")
                    self.speak("見間違えたみたいです。もう一回みてみますね。")
                    self.index = 0
                    self.start = True
            else:
                self.index += 1
                self.start = True
        elif self.state == "solve":
            if self.index == self.maxIndex:
                self.transitTo("end",0)
            else:
                self.index += 1
                self.start = True
        elif self.state == "end":
            self.transitTo("start")

fsm = cubeSolverFSM()

def image_cb(msg):
    bridge = CvBridge()
    frame = None
    try:
        frame = bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        fsm.run(frame)

        key = cv2.waitKey(10) & 0xff
        if key == ord('e'):
            fsm.robot.addCommand("(init-pose)")
            sendCommand(fsm.robot)
            fsm.autoTransition = False
            fsm.finish = True
            fsm.state = "end"
        elif key == ord('n'):
            fsm.stateTransition()
        elif key == ord('x'):
            fsm.robot.addCommand("(send *ri* :neutral)")
            fsm.robot.addCommand("(send *ri* :free)")
            sendCommand(fsm.robot)
        elif key == ord('a'):
            fsm.autoTransition = not fsm.autoTransition
        elif key == ord('s'):
            saveROIs(frame)
    except CvBridgeError as e:
        print(e)
        return

if __name__ == "__main__":
    rospy.init_node("cubeSolver")
    rospy.Subscriber("~image_in", Image, image_cb, queue_size=1)
    rospy.spin()
