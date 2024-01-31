# -----------------------------------------------------------------------
# Author:   Takayoshi Hagiwara (KMD)
# Created:  2021/10/6
# Summary:  操作者の動きマネージャー
# -----------------------------------------------------------------------

import csv
import threading
import time

import numpy as np
from BendingSensor.BendingSensorManager import BendingSensorManager
from OptiTrack.OptiTrackStreamingManager import OptiTrackStreamingManager

# ----- Custom class ----- #
from UDP.UDPManager import UDPManager

# ----- Numeric range remapping ----- #
targetMin = 100
targetMax = 850
originalMin = 0
originalMax = 1
bendingSensorMin = 0
bendingSensorMax = 850

# ----- Settings: Recorded motion data ----- #
recordedMotionPath = "RecordedMotion/"
recordedMotionFileName = "Transform_Participant_"
recordedGripperValueFileName = "GripperValue_"


class ParticipantMotionManager:
    def __init__(
        self,
        defaultParticipantNum: int,
        recordedParticipantNum: int = 0,
        motionInputSystem: str = "optitrack",
        gripperInputSystem: str = "bendingsensor",
        bendingSensorNum: int = 1,
        recordedGripperValueNum: int = 0,
        bendingSensorUdpIpAddress: str = "192.168.80.142",
        bendingSensorUdpPort: list = [9000, 9001],
    ) -> None:
        """
        Initialize

        Parameters
        ----------
        defaultParticipantNum: int
            Number of participants
        recordedParticipantNum: (Optional) int
            Number of recorded motion of participants.
            If 0, only the movements of the actual participants are applied.
            If not 0, load the data from the "recordedMotionPath" + "recordedMotionFileName".
            Recorded motions will be counted after the number of real participants.
            e.g. defaultParticipantNum = 2 => recordedParticipant = ['participant3'], ['participant4']...
        motionInputSystem: (Optional) str
            Source of participant motion data
            Options: optitrack, unity
        gripperInputSystem: (Optional) str
            Source of data for gripper control
            Options: bendingsensor, unity, debug
        bendingSensorNum: (Optional) int
            Number of bendingsensors
        recordedGripperValueNum: (Optional): int
            Number of recorded gripper value.
            If 0, only the gripper value of the real time data are applied.
            If not 0, load the data from the "recordedMotionPath" + "recordedGripperValueFileName".
            Recorded gripper value will be counted after the number of real sensor.
            e.g. bendingSensorNum = 1 => recordedGripperValue = ['gripperValue2'], ['gripperValue3']...
        bendingSensorUdpIpAddress: (Optional) str
            IP address for bending sensor UDP streaming
        bendingSensorUdpPort: (Optional) list[int]
            Port number for bending sensor UDP streaming
        """

        self.defaultParticipantNum = defaultParticipantNum
        self.recordedParticipantNum = recordedParticipantNum
        self.motionInputSystem = motionInputSystem
        self.gripperInputSystem = gripperInputSystem
        self.bendingSensorNum = bendingSensorNum
        self.recordedGripperValueNum = recordedGripperValueNum
        self.udpManager = None
        self.recordedMotion = {}
        self.recordedGripperValue = {}
        self.recordedMotionLength = []
        self.InitBendingSensorValue = 0

        # ----- Initialize participants' motion input system ----- #
        if motionInputSystem == "optitrack":
            self.optiTrackStreamingManager = OptiTrackStreamingManager(
                defaultParticipantNum=defaultParticipantNum
            )

            # ----- Start streaming from OptiTrack ----- #
            streamingThread = threading.Thread(
                target=self.optiTrackStreamingManager.stream_run
            )
            streamingThread.setDaemon(True)
            streamingThread.start()

        elif motionInputSystem == "unity":
            # The number of participants will be adjusted by Unity, so it is assumed that only one participant will be received here.
            self.defaultParticipantNum = 1
            self.udpManager = UDPManager(port=8000, localAddr="127.0.0.1")

            streamingThread = threading.Thread(target=self.udpManager.UpdateData)
            streamingThread.setDaemon(True)
            streamingThread.start()

            # Wait for UDP streaming
            time.sleep(0.1)

        # Recorded motions will be counted after the number of real participants.
        # e.g. defaultParticipantNum = 2 => recordedParticipant = ['participant3'], ['participant4']...
        for i in range(recordedParticipantNum):
            with open(
                recordedMotionPath + recordedMotionFileName + str(i + 1) + ".csv"
            ) as f:
                reader = csv.reader(f)
                data = [row for row in reader][1:]  # Remove header
                data = [[float(v) for v in row] for row in data]  # Convert to float
                self.recordedMotion[
                    "participant" + str(defaultParticipantNum + i + 1)
                ] = data
                self.recordedMotionLength.append(len(data))

        # ----- Initialize gripper control system ----- #
        if gripperInputSystem == "bendingsensor":
            # self.bendingSensors = []
            # bendingSensorSerialCom = "COM8"
            # bendingSensorSerialPort = 115200

            self.bendingSensorManager = BendingSensorManager()

            # ----- Start receiving bending sensor value from UDP socket ----- #
            bendingSensorThread = threading.Thread(
                target=self.bendingSensorManager.StartReceiving
            )
            bendingSensorThread.setDaemon(True)
            bendingSensorThread.start()

            # # ----- Set init value ----- #
            # self.SetInitialBendingValue()

        elif gripperInputSystem == "unity":
            if not self.udpManager:
                self.defaultParticipantNum = 1
                self.udpManager = UDPManager(port=8000, localAddr="127.0.0.1")

                streamingThread = threading.Thread(target=self.udpManager.UpdateData)
                streamingThread.setDaemon(True)
                streamingThread.start()

                # Wait for UDP streaming
                time.sleep(0.1)

        # Recorded motions will be counted after the number of bending sensors.
        # e.g. bendingSensorNum = 1 => recordedGripperValue = ['gripperValue2'], ['gripperValue3']...
        for i in range(recordedGripperValueNum):
            with open(
                recordedMotionPath + recordedGripperValueFileName + str(i + 1) + ".csv"
            ) as f:
                reader = csv.reader(f)
                data = [row for row in reader][1:]  # Remove header
                data = [[float(v) for v in row] for row in data]  # Convert to float
                self.recordedGripperValue[
                    "gripperValue" + str(bendingSensorNum + i + 1)
                ] = data

    def LocalPosition(self, loopCount: int = 0):
        """
        Local position

        Parameters
        ----------
        loopCount: (Optional) int
            For recorded motion.
            Count of loop.

        Returns
        ----------
        participants' local position: dict
        {'participant1': [x, y, z]}
        unit: [m]
        """

        dictPos = {}
        if self.motionInputSystem == "optitrack":
            dictPos = self.optiTrackStreamingManager.position
        return dictPos

    def LocalRotation(self, loopCount: int = 0):
        """
        Local rotation

        Parameters
        ----------
        loopCount: (Optional) int
            For recorded motion.
            Count of loop.

        Returns
        ----------
        participants' local rotation: dict
        {'participant1': [x, y, z, w] or [x, y, z]}
        """

        dictRot = {}
        if self.motionInputSystem == "optitrack":
            dictRot = self.optiTrackStreamingManager.rotation
        return dictRot

    def GripperControlValue(self, loopCount: int = 0):
        """
        Value for control of the xArm gripper

        Parameters
        ----------
        loopCount: (Optional) int
            For recorded motion.
            Count of loop.

        Returns
        ----------
        Value for control of the xArm gripper: dict
        {'gripperValue1': float value}
        """

        if self.gripperInputSystem == "bendingsensor":
            dictGripperValue = self.bendingSensorManager.bendingValue

        return dictGripperValue
