import cv2
import numpy as np
from threading import Thread, Lock

import callibration as callib

class WebCams(object):

	def __init__(self, first, second) :
		self.captureLeft = cv2.VideoCapture(first)
		self.captureRight = cv2.VideoCapture(second)
		ret, self.imageLeft = self.captureLeft.read()
		ret, self.imageRight = self.captureRight.read()
		self.rectifiedImageLeft = self.imageLeft
		self.rectifiedImageRight = self.imageRight
		self.camStreamHeight, self.camStreamWidth, channels = self.imageLeft.shape

	def UpdateFrame(self) :
		ret, self.imageLeft = self.captureLeft.read()
		ret, self.imageRight = self.captureRight.read()



class ChassboardParams(object) :
	def __init__(self, nx, ny, squareSize) :
		self.NX = nx
		self.NY = ny
		self.squareSize = squareSize



class Calibrator(object) :

	howManyCapturiesNeed = 0
	number = 1

	isSaveChessboardCorners = True

	path = "C:\\Users\\Pavel\\Documents\\PythonProjects\\OpenCV\\StereoCamProject\\"

	mutexNumber = Lock()
	mutexImage = Lock()

	def __init__(self, isCalibrateNeed, isRecaptureNeed, capturiesNum, chessboard, cams) :
		self.howManyCapturiesNeed = capturiesNum
		self.isCalibrateNeed = isCalibrateNeed
		self.isRecaptureNeed = isRecaptureNeed
		self.chessboard = chessboard
		self.webCams = cams

	def CheckCapture(self, iLeft, iRight) :
		grayLeft = cv2.cvtColor(iLeft, cv2.COLOR_BGR2GRAY)
		grayRight = cv2.cvtColor(iRight, cv2.COLOR_BGR2GRAY)
		foundLeft, cornersLeft = cv2.findChessboardCorners(grayLeft, (self.chessboard.NX, self.chessboard.NY), None)
		foundRight, cornersLeft = cv2.findChessboardCorners(grayRight, (self.chessboard.NX, self.chessboard.NY), None)

		'''
		if self.isSaveChessboardCorners  and foundLeft and foundRight:
			criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
			corners2 = cv2.cornerSubPix(grayLeft, cornersLeft,(11,11), (-1,-1), criteria)
			iLeft = cv2.drawChessboardCorners(iLeft, (self.chessboard.NX, self.chessboard.NY), corners2, foundLeft)
			iLeft.imshow('img', img)
			cv2.waitKey(500)
		'''
		if foundLeft and foundRight :
			return True
		return False

	def CreateDisplay(self) :
		cv2.namedWindow("LEFT", 0)
		cv2.namedWindow("RIGHT", 0)

	def UpdateDisplay(self) :
		self.mutexImage.acquire()
		self.webCams.UpdateFrame()
		self.mutexImage.release()
		cv2.imshow("LEFT", self.webCams.imageLeft)
		cv2.imshow("RIGHT", self.webCams.imageRight)
		cv2.waitKey(1)

	def DestroyDisplay(self) :
		cv2.destroyWindow("LEFT")
		cv2.destroyWindow("RIGHT")

	def SaveStereoCapture(self, iLeft, iRight) :
		print("Saving image " + str(self.number))
		cv2.imwrite(self.path + "Captures/left" + str(self.number) + ".jpg", iLeft)
		cv2.imwrite(self.path + "Captures/right" + str(self.number) + ".jpg", iRight)


	def SaveChessboardIfFound(self, iLeft, iRight) :
		# Find chasboard on image
		if self.CheckCapture(iLeft, iRight) == True :
			self.mutexNumber.acquire()
			print("Chessboard detected!\n")
			self.SaveStereoCapture(iLeft, iRight)
			self.number = self.number + 1
			self.mutexNumber.release()
			

	def StereoRecapture(self) :
		threads = []
		self.CreateDisplay()
		while self.howManyCapturiesNeed != self.number :
			self.UpdateDisplay()

			self.mutexImage.acquire()
			iLeft = self.webCams.imageLeft
			iRight = self.webCams.imageRight
			self.mutexImage.release()

			tCheckImageForChess = Thread(target=self.SaveChessboardIfFound, args=(iLeft, iRight))
			tCheckImageForChess.start()
			threads.append(tCheckImageForChess)
		
		for t in threads :
			t.join()

		self.DestroyDisplay()
		print("\nAll capturies were saved!\n\n")

	def StereoCalibration(self) :


	def StartCallibration(self) :
		if self.chessboard.NX <= 0 or self.chessboard.NY <= 0 or self.chessboard.squareSize <= 0.0 :
			print("ERROR: chessboard params are wrong!\n")
			return False
		self.StereoCalibration()
		return True


cams = WebCams(1, 2)
calibration = Calibrator(True, True, 10, ChassboardParams(9, 6, 6.25), cams)



if calibration.isCalibrateNeed :
	cv2.namedWindow("LEFT", 0)
	cv2.namedWindow("RIGHT", 0)

	print("Starting Calibration ...\n")
	if calibration.isRecaptureNeed :
		calibration.StereoRecapture()

	## Begin calibration
	calibration.StartCallibration()

cv2.namedWindow("LEFT", 0)
cv2.namedWindow("RIGHT", 0)
cv2.namedWindow("DISPARITY", 0)
cv2.namedWindow("OBJECT IDETIFIER", 0)
