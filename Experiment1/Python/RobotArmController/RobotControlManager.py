# -----------------------------------------------------------------------
# Author:   Takayoshi Hagiwara (KMD)
# Created:  2021/8/19
# Summary:  Robot arm motion control manager
# -----------------------------------------------------------------------

import csv
import time
from ctypes import windll

import numpy as np
import RobotArmController.Robotconfig as RC
import RobotArmController.Robotconfig_pos as RP
from CyberneticAvatarMotion.CyberneticAvatarMotionBehaviour import (
    CyberneticAvatarMotionBehaviour,
)
from ParticipantMotion.ParticipantMotionManager import ParticipantMotionManager
from Recorder.DataRecordManager import DataRecordManager

# from VibrotactileFeedback.VibrationFeedback import Vibrotactile
# ----- Custom class ----- #
from RobotArmController.xArmTransform import xArmTransform
from xarm.wrapper import XArmAPI

# ---------- Settings: xArm connection and UDP connection ---------- #
localPort = 8000
bendingSensorPortParticipant1 = 9000
bendingSensorPortParticipant2 = 9010
bendingSensorPorts = [bendingSensorPortParticipant1, bendingSensorPortParticipant2]

# ---------- Settings: Number of recorded motion, rigidbodies and devices ---------- #
bendingSensorCount = 2  # Number of bending sensors
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
inversedAxes = ["y", "z"]

# ----- Safety settings. Unit: [mm] ----- #
movingDifferenceLimit = 50


class RobotControlManager:
    def __init__(self) -> None:
        self.xArmIpAddress = "192.168.1.199"
        self.wirelessIpAddress = None
        self.num_int = 127

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
        transform = xArmTransform()
        dataRecordManager = DataRecordManager(
            participantNum=participantNum, otherRigidBodyNum=otherRigidBodyCount
        )
        participantMotionManager = ParticipantMotionManager(
            defaultParticipantNum=participantNum,
            recordedParticipantNum=recordedParticipantMotionCount,
            motionInputSystem=motionDataInputMode,
            gripperInputSystem=gripperDataInputMode,
            bendingSensorNum=bendingSensorCount,
            recordedGripperValueNum=recordedGripperValueCount,
            bendingSensorUdpIpAddress=self.wirelessIpAddress,
            bendingSensorUdpPort=bendingSensorPorts,
        )

        # vibrotactile = Vibrotactile()

        # ----- Initialize robot arm ----- #
        if isEnablexArm:
            self.arm = XArmAPI(self.xArmIpAddress)
            self.InitializeAll(self.arm, transform)

        # ----- Control flags ----- #
        isMoving = False

        # ----- Internal flags ----- #
        isPrintFrameRate = False  # For debug
        isPrintData = False  # For debug

        self.arm.set_tgpio_modbus_baudrate(2000000)
        self.init_loadcell_val = self.arm.get_cgpio_analog(1)[1]
        try:
            while True:
                print(time.perf_counter() - taskStartTime)
                # 60秒で強制終了
                if time.perf_counter() - taskStartTime > 20:
                    isMoving = False
                if time.perf_counter() - taskStartTime > executionTime:
                    # ----- Exit processing after task time elapses ----- #
                    isMoving = False

                    self.taskTime.append(time.perf_counter() - taskStartTime)
                    self.PrintProcessInfo()

                    # ----- Export recorded data ----- #
                    if isExportData:
                        dataRecordManager.ExportSelf()

                    # ----- Disconnect ----- #
                    if isEnablexArm:
                        self.arm.disconnect()

                    windll.winmm.timeEndPeriod(1)

                    print("----- Finish task -----")
                    break

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
                    # print(localPosition["participant1"], localPosition["participant2"])

                    # print(localPosition["participant1"], "a")

                    with open("xyz0227.csv", "a", newline="") as file:
                        writer = csv.writer(file)
                        writer.writerow(
                            [
                                time.perf_counter() - taskStartTime,
                                localPosition["participant1"],
                                localPosition["participant2"],
                            ]
                        )

                    weightSlider = [0.5, 0.5]

                    position, rotation = caBehaviour.GetSharedTransformWithCustomWeight(
                        localPosition, localRotation, weightSlider
                    )

                    position = position * 1000

                    # ----- Set xArm transform ----- #
                    transform.x, transform.y, transform.z = (
                        position[2],
                        position[1],
                        -position[0],
                    )
                    # print(position)
                    # transform.roll, transform.pitch, transform.yaw = (
                    #     rotation[0],
                    #     rotation[1],
                    #     -rotation[2],
                    # )

                    transform.q = rotation

                    # ----- Safety check (Position) ---- #
                    diffX = transform.x - beforeX
                    diffY = transform.y - beforeY
                    diffZ = transform.z - beforeZ
                    beforeX, beforeY, beforeZ = transform.x, transform.y, transform.z

                    if diffX == 0 and diffY == 0 and diffZ == 0 and isFixedFrameRate:
                        print(
                            "[WARNING] >> Rigid body is not captured by the mocap camera."
                        )
                    elif (
                        abs(diffX) > movingDifferenceLimit
                        or abs(diffY) > movingDifferenceLimit
                        or abs(diffZ) > movingDifferenceLimit
                    ):
                        isMoving = False
                        print(
                            '[ERROR] >> A rapid movement has occurred. Please enter "r" to reset xArm, or "q" to quit'
                        )
                    else:
                        if isEnablexArm:
                            # ----- Send to xArm ----- #
                            self.arm.set_servo_cartesian(
                                transform.Transform(isOnlyPosition=False)
                            )

                    # ----- Bending sensor ----- #
                    dictBendingValue = participantMotionManager.GripperControlValue(
                        loopCount=self.loopCount
                    )
                    gripperValue = dictBendingValue

                    # ----- Gripper control ----- #
                    if isEnablexArm:
                        code, ret = self.arm.getset_tgpio_modbus_data(
                            self.ConvertToModbusData(gripperValue)
                        )
                    RP.num_gripper_pos = self.arm.get_gripper_position()
                    # print(self.arm.get_gripper_position())
                    self.num = (
                        float(self.arm.get_cgpio_analog(1)[1])
                        - float(self.init_loadcell_val)
                    ) * 1000
                    if self.num > 100:
                        self.num = 100
                    elif self.num < 0:
                        self.num = 0
                    RC.num_int = int(self.num / (100 - 0) * (255 - 127) + 127)
                    # RC.num_int = 127

                    # print(
                    #     (
                    #         float(self.arm.get_cgpio_analog(1)[1])
                    #         - float(self.init_loadcell_val)
                    #     )
                    #     * 1000
                    # )

                    # ----- If xArm error has occured ----- #
                    if isEnablexArm and self.arm.has_err_warn:
                        isMoving = False
                        self.errorCount += 1
                        self.taskTime.append(time.perf_counter() - taskStartTime)
                        print(
                            '[ERROR] >> xArm Error has occured. Please enter "r" to reset xArm, or "q" to quit'
                        )

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
                            + str(np.round(transform.Transform(), 1))
                            + "   Bending sensor > "
                            + str(dictBendingValue)
                        )

                    self.loopCount += 1

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

                else:
                    keycode = input(
                        'Input > "q": quit, "r": Clean error and init arm, "s": start control \n'
                    )
                    # ----- Start streaming ----- #
                    if keycode == "s":
                        caBehaviour.SetOriginPosition(
                            participantMotionManager.LocalPosition()
                        )
                        caBehaviour.SetInversedMatrix(
                            participantMotionManager.LocalRotation()
                        )

                        position, rotation = (
                            caBehaviour.GetSharedTransformWithCustomWeight(
                                participantMotionManager.LocalPosition(),
                                participantMotionManager.LocalRotation(),
                                [0.5, 0.5],
                            )
                        )
                        # (
                        #     position,
                        #     rotation,
                        # ) = caBehaviour.GetSharedTransform(
                        #     participantMotionManager.LocalPosition(),
                        #     participantMotionManager.LocalRotation(),
                        #     sharedMethod,
                        #     0.5,
                        # )
                        beforeX, beforeY, beforeZ = (
                            position[2],
                            position[0],
                            position[1],
                        )

                        isMoving = True
                        taskStartTime = time.perf_counter()

        except KeyboardInterrupt:
            print("\nKeyboardInterrupt >> Stop: RobotControlManager.SendDataToRobot()")

            self.taskTime.append(time.perf_counter() - taskStartTime)
            self.PrintProcessInfo()

            if isExportData:
                dataRecordManager.ExportSelf()

            # ----- Disconnect ----- #
            if isEnablexArm:
                self.arm.disconnect()

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
        robotArm.set_gripper_position(
            850, speed=1500
        )  # デバイスの可動域チェックした？可動域変化したら最大値変換を変更！
        robotArm.getset_tgpio_modbus_data(self.ConvertToModbusData(400))
        print("Initialized > xArm gripper")

        robotArm.set_mode(1)
        robotArm.set_state(state=0)
