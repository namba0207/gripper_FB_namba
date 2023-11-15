# # -----------------------------------------------------------------------
# # Author:   Takayoshi Hagiwara (KMD)
# # Created:  2021/10/21
# # Summary:  Load cell manager
# # -----------------------------------------------------------------------

# import threading
# import time

# # ----- Custom class ----- #
# # from RobotArmController.xArmIO import xArmIO
# # from UDP.UDPManager import UDPManager
# from xarm.wrapper import XArmAPI

# # from MotionFilter.MotionFilter import MotionFilter


# class LoadCellManager:
#     def __init__(self, armIP=None):
#         self.arm = XArmAPI(armIP)
#         self.loadcell_setup()
#         self.num_int = 127

#     def loadcell_setup(self):
#         self.arm.set_tgpio_modbus_baudrate(2000000)
#         self.init_loadcell_val = self.arm.get_cgpio_analog(1)[1]
#         self.loadcell_thr = threading.Thread(target=self.get_loadcell_val, daemon=True)
#         self.loadcell_thr.start()

#     def get_loadcell_val(self):
#         while True:
#             self.num = (self.arm.get_cgpio_analog(1)[1] - self.init_loadcell_val) * 1000
#             if self.num > 150:
#                 self.num = 150
#             elif self.num < 0:
#                 self.num = 0
#             self.num_int = int(self.num / 150 * (220 - 127) + 127)

#             time.sleep(0.01)

# def send_loadcell_val(self):

# def __init__(self, arm, wifiAddr) -> None:
#     self.xArmIO = xArmIO()
#     # self.audioManager = AudioManager(7)
#     self.udpManager = UDPManager(9000, wifiAddr)

#     # ----- Initialize MotionFilter ----- #
#     n = 2
#     fs = 44100
#     self.motionFilter = MotionFilter()
#     self.motionFilter.InitHighPassFilter(fs, 600, 300)

#     # ----- Set variables ----- #
#     self.rawLoadValList = []
#     self.isGripping = False
#     self.InitialLoadCellValue = self.xArmIO.GetxArmAnalogInput(arm)[1][1]

#     # ----- Start thread of tactile feedback ----- #
#     eRubberFeedbackThread = threading.Thread(
#         target=self.GrippingLoadFeedback, args=(arm,)
#     )
#     eRubberFeedbackThread.setDaemon(True)
#     eRubberFeedbackThread.start()

#     # squeezeFeedbackThread = threading.Thread(target=self.GrippingLoadFeedbackWithSqueeze, args=(arm,))
#     # squeezeFeedbackThread.setDaemon(True)
#     # squeezeFeedbackThread.start()

# def GetLoadCellAnalogValue(self, arm):
#     """
#     Get load cell analog value

#     Parameters
#     ----------
#     arm: XArmAPI
#         XArmAPI object
#     """

#     return self.xArmIO.GetxArmAnalogInput(arm)

# def GrippingLoadFeedback(
#     self,
#     arm,
#     isAMSignel: bool = True,
#     threshold: float = 0.2,
#     isConst: bool = False,
# ):
#     """
#     Get feedback of gripping load.
#     Default is to get a few frames of raw data from the load cell and present it with HPF applied.

#     Parameters
#     ----------
#     arm: XArmAPI
#         XArmAPI object
#     isAMSignel: (Optional) bool
#         Use amplitude modulation of the signal
#         Default is to get a few frames of raw data from the load cell and present it with HPF applied.
#     threshold: (Optional) float
#         Threshold of load value for detection of grip
#     isConst: (Optional) bool
#         Appear constant vibration when detect gripping
#     """

#     beforeLoadValue = self.InitialLoadCellValue

#     while True:
#         val = self.GetLoadCellAnalogValue(
#             arm
#         )  # まずここで100fpsくらい落ちる (arm.get_tgpio_analog()が遅いもよう)
#         self.rawLoadValList.append(val[1][1])

#         loadVal = abs(val[1][1] - beforeLoadValue)

#         if loadVal < 0:
#             loadVal = 0

#         beforeLoadValue = val[1][1]

#         if isAMSignel:
#             self.audioManager.AddRawAnalogValue(loadVal)
#         else:
#             if len(self.rawLoadValList) > 24:
#                 hpfDat = self.motionFilter.HighPassFilter(self.rawLoadValList)
#                 self.rawLoadValList.pop(0)

#                 self.audioManager.PlayRawAnalog(hpfDat)

#         # ----- Detect gripping ----- #
#         loadDiffFromInit = val[1][1] - self.InitialLoadCellValue
#         if not self.isGripping and loadDiffFromInit > threshold:
#             self.isGripping = True
#         elif self.isGripping and loadDiffFromInit < threshold:
#             self.isGripping = False

#         if self.isGripping and isConst:
#             self.audioManager.PlaySinWave()
#             pass

# def GrippingLoadFeedbackWithSqueeze(self, arm, threshold: float = 2000):
#     """
#     Get feedback of gripping load.
#     Parameters
#     ----------
#     arm: XArmAPI
#         XArmAPI object
#     threshold: (Optional) float
#         Threshold of load value
#     isConst: (Optional) bool
#         Appear constant vibration when detect gripping
#     """

#     beforeLoadValue = self.InitialLoadCellValue

#     while True:
#         val = self.GetLoadCellAnalogValue(arm)
#         loadVal = abs(val[1][1] - beforeLoadValue)

#         angle = loadVal * 1000 / 1.9 + 1000
#         if angle >= threshold:
#             angle = threshold

#         self.udpManager.SendData(angle, "192.168.11.9", 7000)
#         self.udpManager.SendData(angle, "192.168.11.8", 7000)
