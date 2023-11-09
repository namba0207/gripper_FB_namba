# -----------------------------------------------------------------------
# Author:   Takayoshi Hagiwara (KMD)
# Created:  2021/8/19
# Summary:  Robot arm motion control manager
# -----------------------------------------------------------------------

import datetime
import threading
import time
from ctypes import windll
from datetime import datetime
from enum import Flag

import numpy as np
from BendingSensor.BendingSensorManager import BendingSensorManager
from CyberneticAvatarMotion.CyberneticAvatarMotionBehaviour import (
    CyberneticAvatarMotionBehaviour,
)
from FileIO.FileIO import FileIO
from Graph.Graph_2D import Graph_2D
from LoadCell.LoadCellManager import LoadCellManager
from matplotlib.pyplot import flag
from ParticipantMotion.ParticipantMotionManager import ParticipantMotionManager
from Recorder.DataRecordManager import DataRecordManager
from RobotArmController.WeightSliderManager import WeightSliderManager

# ----- Custom class ----- #
from RobotArmController.xArmTransform import xArmTransform

# from VibrotactileFeedback.VibrotactileFeedbackManager import VibrotactileFeedbackManager
from xarm.wrapper import XArmAPI

# ---------- Settings: xArm connection and UDP connection and OptiTrack connection ---------- #
xArmIP = ""  # xArm ip address
localIP = ""  # local ip address
wirelessIP = ""  # ip address for bending sensor and weight slider
mocapserverAddress = ""  # mocap server address
mocaplocalAddress = ""  # mocap local address


def address_setting(lab):
    global xArmIP
    global localIP
    global wirelessIP
    global mocapserverAddress
    global mocaplocalAddress

    if lab == "KMD":
        xArmIP = "192.168.1.223"
        localIP = "127.0.0.1"
        wirelessIP = "192.168.80.202"
        mocapserverAddress = "192.168.1.1"
        mocaplocalAddress = "192.168.1.2"
    elif lab == "TANAKA":
        xArmIP = "192.168.1.240"
        localIP = "127.0.0.1"
        wirelessIP = "192.168.11.6"
        mocapserverAddress = "192.168.1.30"
        mocaplocalAddress = "192.168.1.30"


# ---------- Settings: Number of recorded motion, rigidbodies and devices ---------- #
bendingSensorCount = 1  # Number of bending sensors
otherRigidBodyCount = 0  # Number of RigidBodies of non-participants

recordedParticipantMotionCount = 0  # Number of motion data of pre recorded
recordedGripperValueCount = 0  # Number of gripper data of pre recorded

# ---------- Settings: Input mode ---------- #
motionDataInputMode = "optitrack"
gripperDataInputMode = "bendingsensor"

# ---------- Settings: Shared method ---------- #
sharedMethod = "integration"

# ---------- Settings: Direction of participants ---------- #
directionOfParticipants = "same"
oppositeParticipants = ["participant1"]
# oppositeParticipants    = ['participant1', 'participant2']
inversedAxes = ["y", "z"]

# ----- Safety settings. Unit: [mm] ----- #
movingDifferenceLimit = 1000


class RobotControlManagerClass:
    def __init__(self) -> None:
        fileIO = FileIO()

        dat = fileIO.Read("settings.csv", ",")
        xArmIP1 = [addr for addr in dat if "xArmIPAddress1" in addr[0]][0][1]
        # xArmIP2      = [addr for addr in dat if 'xArmIPAddress2' in addr[0]][0][1]
        wirelessIP = [addr for addr in dat if "wirelessIPAddress" in addr[0]][0][1]
        localIP = [addr for addr in dat if "localIPAddress" in addr[0]][0][1]
        motiveserverIP = [addr for addr in dat if "motiveServerIPAddress" in addr[0]][
            0
        ][1]
        motivelocalIP = [addr for addr in dat if "motiveLocalIPAddress" in addr[0]][0][
            1
        ]
        bendingSensorPortParticipant1 = [
            addr for addr in dat if "bendingSensorPortParticipant1" in addr[0]
        ][0][1]
        bendingSensorPortParticipant2 = [
            addr for addr in dat if "bendingSensorPortParticipant2" in addr[0]
        ][0][1]
        bendingSensorCom1 = [addr for addr in dat if "bendingSensorCom1" in addr[0]][0][
            1
        ]
        bendingSensorCom2 = [addr for addr in dat if "bendingSensorCom2" in addr[0]][0][
            1
        ]
        weightSliderPort = [addr for addr in dat if "weightSliderPort" in addr[0]][0][1]
        weightSliderListPos = [addr for addr in dat if "weightSliderListPos" in addr[0]]
        weightSliderListRot = [addr for addr in dat if "weightSliderListRot" in addr[0]]
        bendingSensorNumber = [
            addr for addr in dat if "bendingSensorNumber" in addr[0]
        ][0][1]
        self.xArmIpAddress1 = xArmIP1
        # self.xArmIpAddress2          = xArmIP2
        self.wirelessIpAddress = wirelessIP
        self.localIpAddress = localIP
        self.motiveserverIpAddress = motiveserverIP
        self.motivelocalIpAddress = motivelocalIP
        self.bendingSensorPorts = [
            int(bendingSensorPortParticipant1),
            int(bendingSensorPortParticipant2),
        ]
        self.bendingSensorComs = [bendingSensorCom1, bendingSensorCom2]
        self.weightSliderPort = int(weightSliderPort)
        self.weightSliderListPos = weightSliderListPos
        self.weightSliderListRot = weightSliderListRot
        self.bendinSensorNumber = bendingSensorNumber

        self.participantname = "Kato"
        # self.condition = input('---実験条件---\nFB無し-->A, 相手-->B, ロボット-->C   :')
        # self.number = input('---試行回数---\n何回目   :')
        self.condition = "2"
        self.number = "1"

        _i = input("mode: solo-->a, collaboration-->b : ")
        if _i == "a":
            self.weightSliderListPos = [["weightSliderListPos", "1", "0"]]
            self.weightSliderListRot = [["weightSliderListRot", "1", "0"]]
        elif _i == "b":
            self.weightSliderListPos = [["weightSliderListPos", "0.5", "0.5"]]
            self.weightSliderListRot = [["weightSliderListRot", "0.5", "0.5"]]

    def SendDataToRobot(
        self,
        participantNum,
        executionTime: int = 9999,
        isFixedFrameRate: bool = False,
        frameRate: int = 90,
        isChangeOSTimer: bool = False,
        isExportData: bool = True,
        isEnablexArm: bool = True,
    ):
        """
        Send the position and rotation to the xArm

        Parameters
        ----------
        participantNum: int
            Number of participants
        executionTime: (Optional) int
            Unit: [s]
            Execution time
        isFixedFrameRate: (Optional) bool
            Use fixed frame rate.
            Default is depending on the PC specs.
        frameRate: (Optional) int
            Frame rate of the loop of this method
        isChangeOSTimer: (Optional, only for Windows) bool
            Change the Windows OS timer.
            ----- CAUTION -----
                Since this option changes the OS timer, it will affect the performance of other programs.
                Ref: https://python-ai-learn.com/2021/02/07/time/
                Ref: https://docs.microsoft.com/en-us/windows/win32/api/timeapi/nf-timeapi-timebeginperiod
        isExportData: (Optional) bool
            Export recorded data.
            Participants' motion data (Position: xyz, Quaternion: xyzw)
            Other rigid bodys' motion data (Position: xyz, Quaternion: xyzw)
            Gripper value.
        isEnablexArm: (Optional) bool
            For debug mode. If False, xArm will not be enabled.
        """

        # ----- Change OS timer ----- #
        if isFixedFrameRate and isChangeOSTimer:
            windll.winmm.timeBeginPeriod(1)

        # ----- Process info ----- #
        self.loopCount = 0
        self.taskTime = []
        self.errorCount = 0
        taskStartTime = 0

        # ----- Set loop time from frameRate ----- #
        loopTime = 1 / frameRate
        loopStartTime = 0
        processDuration = 0
        listFrameRate = []
        if isFixedFrameRate:
            print("Use fixed frame rate > " + str(frameRate) + "[fps]")

        # ----- Instantiating custom classes ----- #
        caBehaviour = CyberneticAvatarMotionBehaviour(
            defaultParticipantNum=participantNum
        )
        transform_1 = xArmTransform()
        # transform_2                         = xArmTransform()
        dataRecordManager = DataRecordManager(
            participantNum=participantNum, otherRigidBodyNum=otherRigidBodyCount
        )
        participantMotionManager = ParticipantMotionManager(
            defaultParticipantNum=participantNum,
            recordedParticipantNum=recordedParticipantMotionCount,
            motionInputSystem=motionDataInputMode,
            mocapServer=self.motiveserverIpAddress,
            mocapLocal=self.motivelocalIpAddress,
            gripperInputSystem=gripperDataInputMode,
            bendingSensorNum=bendingSensorCount,
            recordedGripperValueNum=recordedGripperValueCount,
            BendingSensor_ConnectionMethod="wired",
            bendingSensorUdpIpAddress=self.wirelessIpAddress,
            bendingSensorUdpPort=self.bendingSensorPorts,
            bendingSensorSerialCOMs=self.bendingSensorComs,
        )
        # weightSliderManager                 = WeightSliderManager(WeightSlider_ConnectionMethod='wireless',ip=self.wirelessIpAddress,port=self.weightSliderPort)
        # vibrotactileFeedbackManager         = VibrotactileFeedbackManager(condition=self.condition)
        Graph2DManager = Graph_2D(n=2)

        # ----- Initialize robot arm ----- #
        if isEnablexArm:
            arm_1 = XArmAPI(self.xArmIpAddress1)
            self.InitializeAll(arm_1, transform_1)

            # arm_2 = XArmAPI(self.xArmIpAddress2)
            # self.InitializeAll(arm_2, transform_2)

        # bendingFeedback = LoadCellManager(arm)

        # ----- Control flags ----- #
        isMoving = False

        # ----- Internal flags ----- #
        isPrintFrameRate = False  # For debug
        isPrintData = False  # For debug
        # ----- Mainloop ----- #
        try:
            while True:
                # if time.perf_counter() - taskStartTime > executionTime:
                #     # ----- Exit processing after task time elapses ----- #
                #     isMoving    = False

                #     self.taskTime.append(time.perf_counter() - taskStartTime)
                #     self.PrintProcessInfo()

                #     # ----- Export recorded data ----- #
                #     if isExportData:
                #         dataRecordManager.ExportSelf(dirPath='C:/Users/cmm13037/Documents/Nishimura',participant=self.participantname,conditions=self.condition)

                #     # ----- Disconnect ----- #
                #     if isEnablexArm:
                #         arm_1.disconnect()
                #         # arm_2.disconnect()

                #     windll.winmm.timeEndPeriod(1)

                #     print('----- Finish task -----')
                #     break

                if isMoving:
                    # ---------- Start control process timer ---------- #
                    loopStartTime = time.perf_counter()

                    # ----- Get transform data----- #
                    localPosition = participantMotionManager.LocalPosition(
                        loopCount=self.loopCount
                    )
                    localRotation = participantMotionManager.LocalRotation(
                        loopCount=self.loopCount
                    )

                    # ----- For opposite condition ----- #
                    if directionOfParticipants == "opposite":
                        for oppositeParticipant in oppositeParticipants:
                            # yz: Mirror mode, xz: Natural mode
                            localRotation[
                                oppositeParticipant
                            ] = caBehaviour.InversedRotation(
                                localRotation[oppositeParticipant], axes=inversedAxes
                            )

                    # ----- Calculate shared transform ----- #
                    # position, rotation = caBehaviour.GetSharedTransform(localPosition, localRotation, sharedMethod, 0.5)
                    # rotation = caBehaviour.Quaternion2Euler(rotation)

                    # ----- For weight slider (Made by Ogura-san) ----- #
                    # weightSliderList = weightSliderManager.GetSliderValue()
                    # weightSliderList = [0.5, 0.5]
                    # weightSlider = [[1-weightSliderList[0], weightSliderList[0]], [1-weightSliderList[1], weightSliderList[1]]]

                    # ----- weight slider list (For participantNum)  ----- #
                    # weightSliderList = []
                    # weightSliderList_0 = [1/participantNum for n in range(participantNum)]
                    # weightSliderList = [weightSliderList_0,weightSliderList_0]

                    (
                        position_1,
                        rotation_1,
                    ) = caBehaviour.GetSharedTransformWithCustomWeight(
                        localPosition, localRotation, weightSliderList
                    )

                    position_1 = position_1 * 1000
                    # position_2 = position_2 * 1000

                    # ----- Set xArm transform ----- #
                    transform_1.x, transform_1.y, transform_1.z = (
                        position_1[2],
                        position_1[0],
                        position_1[1],
                    )
                    transform_1.roll, transform_1.pitch, transform_1.yaw = (
                        rotation_1[2],
                        rotation_1[0],
                        rotation_1[1],
                    )

                    # ----- Safety check (Position) ---- #
                    diffX_1 = transform_1.x - beforeX_1
                    diffY_1 = transform_1.y - beforeY_1
                    diffZ_1 = transform_1.z - beforeZ_1
                    beforeX_1, beforeY_1, beforeZ_1 = (
                        transform_1.x,
                        transform_1.y,
                        transform_1.z,
                    )

                    if (
                        diffX_1 == 0
                        and diffY_1 == 0
                        and diffZ_1 == 0
                        and isFixedFrameRate
                    ):
                        print(
                            "[WARNING] >> Rigid body is not captured by the mocap camera."
                        )
                    elif (
                        abs(diffX_1) > movingDifferenceLimit
                        or abs(diffY_1) > movingDifferenceLimit
                        or abs(diffZ_1) > movingDifferenceLimit
                    ):
                        isMoving = False
                        print(
                            '[ERROR] >> A rapid movement has occurred. Please enter "r" to reset xArm, or "q" to quit'
                        )
                    else:
                        if isEnablexArm:
                            # ----- Send to xArm ----- #
                            arm_1.set_servo_cartesian(
                                transform_1.Transform(
                                    isLimit=False, isOnlyPosition=False
                                )
                            )
                            # arm_2.set_servo_cartesian(transform_2.Transform(isLimit=False,isOnlyPosition=False))

                    # ----- Bending sensor ----- #
                    dictBendingValue = participantMotionManager.GripperControlValue(
                        loopCount=self.loopCount
                    )

                    # ----- Bending sensor for integration or one side ----- #                  #control側は一人がする役割分担で良い
                    if self.bendinSensorNumber == "1":
                        gripperValue_1 = dictBendingValue["gripperValue1"]
                    elif self.bendinSensorNumber == "2":
                        gripperValue_1 = (
                            dictBendingValue["gripperValue1"]
                            + dictBendingValue["gripperValue2"]
                        ) / 2

                    # ----- Gripper control ----- #
                    if isEnablexArm:
                        code_1, ret_1 = arm_1.getset_tgpio_modbus_data(
                            self.ConvertToModbusData(gripperValue_1)
                        )
                        # code_2, ret_2 = arm_2.getset_tgpio_modbus_data(self.ConvertToModbusData(gripperValue_2))

                    # # ----- Vibrotactile Feedback ----- #
                    # if participantNum == 2:
                    #     if sharedMethod == 'integration':
                    #         vibrotactileFeedbackManager.forIntegration(localPosition, localRotation, 0.5)

                    #         # Graph2DManager.make_list(time.perf_counter()-taskStartTime,d1,d2)
                    #     elif sharedMethod == 'divisionofroles':
                    #         vibrotactileFeedbackManager.forDivisionOfRoles(localPosition, localRotation)

                    # ----- Data recording ----- #
                    # relativePosition = CyberneticAvatarMotionBehaviour.GetRelativePosition_r(position=localPosition)
                    # relativeRotation = CyberneticAvatarMotionBehaviour.GetRelativeRotation_r(rotation=localRotation)
                    # dataRecordManager.Record(relativePosition, relativeRotation, dictBendingValue, time.perf_counter()-taskStartTime)
                    # dataRecordManager.Record(localPosition, localRotation, dictBendingValue, time.perf_counter()-taskStartTime)

                    # ----- If xArm error has occured ----- #
                    if isEnablexArm and arm_1.has_err_warn:
                        isMoving = False
                        self.errorCount += 1
                        self.taskTime.append(time.perf_counter() - taskStartTime)
                        print(
                            '[ERROR] >> xArm Error has occured. Please enter "r" to reset xArm, or "q" to quit'
                        )

                    # if isEnablexArm and arm_2.has_err_warn:
                    #     isMoving    = False
                    #     self.errorCount += 1
                    #     self.taskTime.append(time.perf_counter() - taskStartTime)
                    #     print('[ERROR] >> xArm Error has occured. Please enter "r" to reset xArm, or "q" to quit')

                    # ---------- End control process timer ---------- #
                    processDuration = (
                        time.perf_counter() - loopStartTime
                    )  # For loop timer

                    # ----- Fixed frame rate ----- #
                    if isFixedFrameRate:
                        sleepTime = loopTime - processDuration
                        if sleepTime < 0:
                            pass
                        else:
                            time.sleep(sleepTime)

                    # ----- (Optional) Check frame rate ----- #
                    if self.loopCount % 20 == 0 and isPrintFrameRate:
                        if self.loopCount != 0:
                            listFrameRate.append(
                                1 / (time.perf_counter() - loopStartTime)
                            )
                            print(
                                "Average FPS: ", sum(listFrameRate) / len(listFrameRate)
                            )

                    # ----- (Optional) Check data ----- #
                    if isPrintData:
                        print(
                            "xArm transform > "
                            + str(np.round(transform_1.Transform(), 1))
                            + "   Bending sensor > "
                            + str(dictBendingValue)
                        )
                        # print('xArm transform > ' + str(np.round(transform_2.Transform(), 1)) + '   Bending sensor > ' + str(dictBendingValue_2))

                    self.loopCount += 1

                else:
                    keycode = input(
                        'Input > "q": quit, "r": Clean error and init arm, "s": start control \n'
                    )
                    if keycode == "s":
                        caBehaviour.SetOriginPosition(
                            participantMotionManager.LocalPosition()
                        )
                        caBehaviour.SetInversedMatrix(
                            participantMotionManager.LocalRotation()
                        )

                        # # ----- weight slider list (For participantNum)  ----- #
                        # weightSliderList = []
                        # weightSliderList_0 = [1/participantNum for n in range(participantNum)]
                        # weightSliderList = [weightSliderList_0,weightSliderList_0]

                        # ----- weight slider list ----- #
                        self.weightSliderListPos[0].remove("weightSliderListPos")
                        self.weightSliderListRot[0].remove("weightSliderListRot")
                        weightSliderListPosstr = self.weightSliderListPos[0]
                        weightSliderListRotstr = self.weightSliderListRot[0]
                        weightSliderListPosfloat = list(
                            map(float, weightSliderListPosstr)
                        )
                        weightSliderListRotfloat = list(
                            map(float, weightSliderListRotstr)
                        )
                        weightSliderList = [
                            weightSliderListPosfloat,
                            weightSliderListRotfloat,
                        ]

                        # self.weightSliderList = [[0,1],[0,1]]
                        # self.weightSliderList = [[0.5,0.5],[0.5,0.5]]

                        # print(weightSliderList)

                        (
                            position_1,
                            rotation_1,
                        ) = caBehaviour.GetSharedTransformWithCustomWeight(
                            participantMotionManager.LocalPosition(),
                            participantMotionManager.LocalRotation(),
                            weightSliderList,
                        )
                        beforeX_1, beforeY_1, beforeZ_1 = (
                            position_1[2],
                            -1 * position_1[1],
                            position_1[0],
                        )
                        # beforeX_2, beforeY_2, beforeZ_2 = position_2[2], position_2[0], position_2[1]

                        participantMotionManager.SetInitialBendingValue()

                        isMoving = True
                        taskStartTime = time.perf_counter()

        except KeyboardInterrupt:
            print("\nKeyboardInterrupt >> Stop: RobotControlManager.SendDataToRobot()")

            self.taskTime.append(time.perf_counter() - taskStartTime)
            self.PrintProcessInfo()

            # Graph2DManager.soloy_graph()

            if isExportData:
                dataRecordManager.ExportSelf(
                    dirPath="C:/Users/kimih/Documents/Nishimura",
                    participant=self.participantname,
                    conditions=self.condition,
                    number=self.number,
                )

            # ----- Disconnect ----- #
            if isEnablexArm:
                arm_1.disconnect()
                # arm_2.disconnect()

            windll.winmm.timeEndPeriod(1)

        except:
            print("----- Exception has occurred -----")
            windll.winmm.timeEndPeriod(1)
            import traceback

            traceback.print_exc()

    def InitRobotArm(self, robotArm, transform, isSetInitPosition=True):
        """
        Initialize the xArm

        Parameters
        ----------
        robotArm: XArmAPI
            XArmAPI object.
        transform: xArmTransform
            xArmTransform object.
        isSetInitPosition: (Optional) bool
            True -> Set to "INITIAL POSITION" of the xArm studio
            False -> Set to "ZERO POSITION" of the xArm studio
        """

        robotArm.connect()
        robotArm.motion_enable(enable=True)
        robotArm.set_mode(0)  # set mode: position control mode
        robotArm.set_state(state=0)  # set state: sport state

        if isSetInitPosition:
            robotArm.clean_error()
            robotArm.clean_warn()
            (
                initX,
                initY,
                initZ,
                initRoll,
                initPitch,
                initYaw,
            ) = transform.GetInitialTransform()
            robotArm.set_position(
                x=initX,
                y=initY,
                z=initZ,
                roll=initRoll,
                pitch=initPitch,
                yaw=initYaw,
                wait=True,
            )
        else:
            robotArm.reset(wait=True)

        robotArm.motion_enable(enable=True)
        robotArm.set_mode(1)
        robotArm.set_state(state=0)

        time.sleep(0.5)
        print("Initialized > xArm")

    def InitGripper(self, robotArm):
        """
        Initialize the gripper

        Parameters
        ----------
        robotArm: XArmAPI
            XArmAPI object.
        """

        robotArm.set_tgpio_modbus_baudrate(2000000)
        robotArm.set_gripper_mode(0)
        robotArm.set_gripper_enable(True)
        robotArm.set_gripper_position(0, speed=5000)

        robotArm.getset_tgpio_modbus_data(self.ConvertToModbusData(425))

        time.sleep(0.5)
        print("Initialized > xArm gripper")

    def ConvertToModbusData(self, value: int):
        """
        Converts the data to modbus type.

        Parameters
        ----------
        value: int
            The data to be converted.
            Range: 0 ~ 800
        """

        if int(value) <= 255 and int(value) >= 0:
            dataHexThirdOrder = 0x00
            dataHexAdjustedValue = int(value)

        elif int(value) > 255 and int(value) <= 511:
            dataHexThirdOrder = 0x01
            dataHexAdjustedValue = int(value) - 256

        elif int(value) > 511 and int(value) <= 767:
            dataHexThirdOrder = 0x02
            dataHexAdjustedValue = int(value) - 512

        elif int(value) > 767 and int(value) <= 1123:
            dataHexThirdOrder = 0x03
            dataHexAdjustedValue = int(value) - 768

        modbus_data = [0x08, 0x10, 0x07, 0x00, 0x00, 0x02, 0x04, 0x00, 0x00]
        modbus_data.append(dataHexThirdOrder)
        modbus_data.append(dataHexAdjustedValue)

        return modbus_data

    def PrintProcessInfo(self):
        """
        Print process information.
        """

        print("----- Process info -----")
        print("Total loop count > ", self.loopCount)
        for ttask in self.taskTime:
            print("Task time\t > ", ttask, "[s]")
        print("Error count\t > ", self.errorCount)
        print("------------------------")

    # ----- For debug ----- #
    def BendingSensorTest(self):
        """
        For testing.
        Only get the value of the bending sensor.
        """

        bendingSensorManagerMaster = BendingSensorManager(
            ip=self.wirelessIpAddress, port=self.bendingSensorPorts[0]
        )
        bendingSensorManagerBeginner = BendingSensorManager(
            ip=self.wirelessIpAddress, port=self.bendingSensorPorts[1]
        )

        # ----- Start receiving bending sensor value from UDP socket ----- #
        bendingSensorThreadMaster = threading.Thread(
            target=bendingSensorManagerMaster.StartReceiving
        )
        bendingSensorThreadMaster.setDaemon(True)
        bendingSensorThreadMaster.start()

        bendingSensorThreadBeginner = threading.Thread(
            target=bendingSensorManagerBeginner.StartReceiving
        )
        bendingSensorThreadBeginner.setDaemon(True)
        bendingSensorThreadBeginner.start()

        try:
            while True:
                bendingSensorValue1 = bendingSensorManagerMaster.bendingValue
                bendingSensorValue2 = bendingSensorManagerBeginner.bendingValue
                print(
                    "Sensor1 > "
                    + str(bendingSensorValue1)
                    + "   Sensor2 > "
                    + str(bendingSensorValue2)
                )

        except KeyboardInterrupt:
            print("KeyboardInterrupt >> Stop: RobotControlManager.BendingSensorTest()")
            bendingSensorManagerMaster.EndReceiving()
            bendingSensorManagerBeginner.EndReceiving()

    def LoadCellTest(self):
        """
        For testing.
        Only get the value of the load cell.
        """

        transform = xArmTransform()
        loadCellManager = LoadCellManager()

        arm = XArmAPI(self.xArmIpAddress)
        self.InitRobotArm(arm, transform)

        while True:
            val = loadCellManager.GetLoadCellAnalogValue(arm)
            print(val)

    def AudioTest(self):
        """
        For testing.
        Only play the audio.
        """

        audioManager = AudioManager()

        while True:
            keycode = input()
            if keycode == "p":
                audioManager.PlayPositive()

    def eRubberTactileFeedbackTest(self):
        arm = XArmAPI(self.xArmIpAddress)
        transform = xArmTransform()
        self.InitRobotArm(arm, transform)
        self.InitGripper(arm)

        loadCellManager = LoadCellManager(arm)
        audioManager = AudioManager(6)

        bendingSensorManager = BendingSensorManager(
            ip=self.wirelessIpAddress, port=self.bendingSensorPorts[0]
        )

        # ----- Start receiving bending sensor value from UDP socket ----- #
        bendingSensorThread = threading.Thread(
            target=bendingSensorManager.StartReceiving
        )
        bendingSensorThread.setDaemon(True)
        bendingSensorThread.start()

        beforeLoadValue = loadCellManager.InitialLoadCellValue

        isGripping = False
        threshold = 0.2

        from MotionFilter.MotionFilter import MotionFilter

        n = 2
        fs = 180
        motionFilter = MotionFilter(n, 1, fs)
        loadValList = []

        try:
            while True:
                code, ret = arm.getset_tgpio_modbus_data(
                    self.ConvertToModbusData(bendingSensorManager.bendingValue)
                )

                val = loadCellManager.GetLoadCellAnalogValue(arm)
                loadVal = abs(val[1][1] - beforeLoadValue)
                # print(val[1][1])

                # audioManager.AddRawAnalogValue(loadVal)

                if loadVal < 0:
                    loadVal = 0

                beforeLoadValue = val[1][1]

                # ----- Detect gripping ----- #
                loadDiffFromInit = val[1][1] - loadCellManager.InitialLoadCellValue
                if not isGripping and loadDiffFromInit > threshold:
                    isGripping = True
                elif isGripping and loadDiffFromInit < threshold:
                    isGripping = False

                if isGripping:
                    print("Gripping")
                    # audioManager.PlaySinWave()

                loadValList.append(val[1][1])
                if len(loadValList) > 9:
                    hpfDat = motionFilter.HighPassFilter(loadValList)
                    loadValList.pop(0)

                    audioManager.PlayRawAnalog(hpfDat)
                    # print(hpfDat)

        except KeyboardInterrupt:
            print("End")

    def CheckGraph(self):
        # ----- Settings: Plot ----- #
        import math

        import matplotlib.pyplot as plt

        times = [0 for i in range(200)]
        loads = [0 for i in range(200)]
        grippers = [0 for i in range(200)]

        time = 0
        load = 0
        gripper = 0

        # initialize matplotlib
        plt.ion()
        plt.figure()
        (li_load,) = plt.plot(times, loads, color="red", label="Load value")
        (li_gripper,) = plt.plot(times, grippers, color="blue", label="Gripper")

        plt.ylim(-0.1, 900)
        plt.xlabel("time")
        plt.ylabel("diff load value")
        # plt.title("real time plot")
        # ----- End settings: Plot ----- #

        arm = XArmAPI(self.xArmIpAddress)
        transform = xArmTransform()
        self.InitRobotArm(arm, transform)
        self.InitGripper(arm)

        loadCellManager = LoadCellManager(arm)
        beforeLoadValue = loadCellManager.InitialLoadCellValue

        bendingSensorManager = BendingSensorManager(
            ip=self.wirelessIpAddress, port=self.bendingSensorPorts[0]
        )

        # ----- Start receiving bending sensor value from UDP socket ----- #
        bendingSensorThread = threading.Thread(
            target=bendingSensorManager.StartReceiving
        )
        bendingSensorThread.setDaemon(True)
        bendingSensorThread.start()

        try:
            while True:
                # code, ret = arm.getset_tgpio_modbus_data(self.ConvertToModbusData(bendingSensorManager.bendingValue))

                val = loadCellManager.GetLoadCellAnalogValue(arm)
                loadVal = abs(val[1][1] - beforeLoadValue)
                beforeLoadValue = val[1][1]

                time += 0.1
                load = loadVal * 10000
                gripper = arm.get_gripper_position()[1]

                times.append(time)
                times.pop(0)
                loads.append(load)
                loads.pop(0)
                grippers.append(gripper)
                grippers.pop(0)

                li_load.set_xdata(times)
                li_load.set_ydata(loads)
                li_gripper.set_xdata(times)
                li_gripper.set_ydata(grippers)

                plt.xlim(min(times), max(times))
                plt.draw()
                plt.legend()

                plt.pause(0.01)

        except KeyboardInterrupt:
            print("END")

    def InitializeAll(self, robotArm, transform, isSetInitPosition=True):
        """
        Initialize the xArm

        Parameters
        ----------
        robotArm: XArmAPI
            XArmAPI object.
        transform: xArmTransform
            xArmTransform object.
        isSetInitPosition: (Optional) bool
            True -> Set to "INITIAL POSITION" of the xArm studio
            False -> Set to "ZERO POSITION" of the xArm studio
        """

        robotArm.connect()
        if robotArm.warn_code != 0:
            robotArm.clean_warn()
        if robotArm.error_code != 0:
            robotArm.clean_error()
        robotArm.motion_enable(enable=True)
        robotArm.set_mode(0)  # set mode: position control mode
        robotArm.set_state(state=0)  # set state: sport state
        if isSetInitPosition:
            (
                initX,
                initY,
                initZ,
                initRoll,
                initPitch,
                initYaw,
            ) = transform.GetInitialTransform()
            robotArm.set_position(
                x=initX,
                y=initY,
                z=initZ,
                roll=initRoll,
                pitch=initPitch,
                yaw=initYaw,
                wait=True,
            )
        else:
            robotArm.reset(wait=True)
        print("Initialized > xArm")

        robotArm.set_tgpio_modbus_baudrate(2000000)
        robotArm.set_gripper_mode(0)
        robotArm.set_gripper_enable(True)
        robotArm.set_gripper_position(850, speed=5000)
        robotArm.getset_tgpio_modbus_data(self.ConvertToModbusData(425))
        print("Initialized > xArm gripper")

        robotArm.set_mode(1)
        robotArm.set_state(state=0)
