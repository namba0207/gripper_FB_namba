# -----------------------------------------------------------------------
# Author:   Takayoshi Hagiwara (KMD)
# Created:  2021/8/12
# Summary:  xArm用Transformクラス
# -----------------------------------------------------------------------

import math

# from _typeshed import Self
from math import pi

import numpy as np


class xArmTransform:
    """
    xArmの座標と回転を保持するクラス


    """

    x, y, z = 0, 0, 0
    roll, pitch, yaw = 0, 0, 0

    # ----- ロボットが縦の場合、前にｘ、右にｙ、上にｚそれぞれにｒｐｙ、双腕だと回転 ----- #
    # __initX, __initY, __initZ = 520, -150, 250
    __initX, __initY, __initZ = 500, -150, 250
    __initRoll, __initPitch, __initYaw = 90, 90, 0  # 90, 0, 0

    # ----- Minimum limitation ----- #
    __minX, __minY, __minZ = 200, -200, 0
    # __minX, __minY, __minZ = 490, -80, 220
    __minRoll, __minPitch, __minYaw = -90, 0, -90  # -90, 0, -90

    # ----- Maximum limitation ----- #
    # __maxX, __maxY, __maxZ = 550, -20, 280
    __maxX, __maxY, __maxZ = 720, 300, 500
    __maxRoll, __maxPitch, __maxYaw = 95, 180, 90  # 90, 180, 90

    def __init__(self):
        self.init_q = self.Euler2Quaternion(
            [self.__initRoll, self.__initPitch, self.__initYaw]
        )
        self.q = 0

    def SetInitialTransform(self, initX, initY, initZ, initRoll, initPitch, initYaw):
        """
        Set the initial position and rotation.
        If this function is not called after the class is instantiated, the initial values of the member variables of this class will be used.

        Parameters
        ----------
        initX, initY, initZ: float
            Initial position.
        initRoll, initPitch, initYaw: float
            Initial rotation.
        """

        self.__initX = initX
        self.__initY = initY
        self.__initZ = initZ

        self.__initRoll = initRoll
        self.__initPitch = initPitch
        self.__initYaw = initYaw

    def GetInitialTransform(self):
        """
        Get the initial position and rotation.
        """

        return (
            self.__initX,
            self.__initY,
            self.__initZ,
            self.__initRoll,
            self.__initPitch,
            self.__initYaw,
        )

    def SetMinimumLimitation(self, minX, minY, minZ, minRoll, minPitch, minYaw):
        """
        Set the lower limit of the position and rotation.
        If this function is not called after the class is instantiated, the initial values of the member variables of this class will be used.

        Parameters
        ----------
        minX, minY, minZ: float
            Lower limit of the position.
        minRoll, minPitch, minYaw: float
            Lower limit of the rotation.
        """

        self.__minX = minX
        self.__minY = minY
        self.__minZ = minZ

        self.__minRoll = minRoll
        self.__minPitch = minPitch
        self.__minYaw = minYaw

    def SetMaximumLimitation(self, maxX, maxY, maxZ, maxRoll, maxPitch, maxYaw):
        """
        Set the upper limit of the position and rotation.
        If this function is not called after the class is instantiated, the initial values of the member variables of this class will be used.

        Parameters
        ----------
        maxX, maxY, maxZ: float
            Upper limit of the position.
        maxRoll, maxPitch, maxYaw: float
            Upper limit of the rotation.
        """

        self.__maxX = maxX
        self.__maxY = maxY
        self.__maxZ = maxZ

        self.__maxRoll = maxRoll
        self.__maxPitch = maxPitch
        self.__maxYaw = maxYaw

    def Transform(
        self, posMagnification=1, rotMagnification=1, isLimit=True, isOnlyPosition=True
    ):
        """
        Calculate the position and rotation to be sent to xArm.

        Parameters
        ----------
        posMagnification: int (Default = 1)
            Magnification of the position. Used when you want to move the position less or more.
        rotMagnification: int (Default = 1)
            Magnification of the rotation. Used when you want to move the position less or more.
        isLimit: bool (Default = True)
            Limit the position and rotation.
            Note that if it is False, it may result in dangerous behavior.
        isOnlyPosition: bool (Default = True)
            Reflect only the position.
            If True, the rotations are __initRoll, __initPitch, and __initYaw.
            If False, the rotation is also reflected.
        """

        x, y, z = (
            self.x * posMagnification + self.__initX,
            self.y * posMagnification + self.__initY,
            self.z * posMagnification + self.__initZ,
        )

        # q = self.Euler2Quaternion([self.roll, self.pitch, self.yaw])

        euler = self.Quaternion2Euler(np.dot(self.Convert2Matrix(self.q), self.init_q))

        # roll, pitch, yaw = (
        #     self.roll * rotMagnification + self.__initRoll,
        #     self.pitch * rotMagnification + self.__initPitch,
        #     self.yaw * rotMagnification + self.__initYaw,
        # )

        roll, pitch, yaw = euler[0], euler[1], euler[2]

        if isOnlyPosition:
            roll, pitch, yaw = self.__initRoll, self.__initPitch, self.__initYaw

        if isLimit:
            # pos X
            if x > self.__maxX:
                x = self.__maxX
            elif x < self.__minX:
                x = self.__minX

            # pos Y
            if y > self.__maxY:
                y = self.__maxY
            elif y < self.__minY:
                y = self.__minY

            # pos Z
            if z > self.__maxZ:
                z = self.__maxZ
            elif z < self.__minZ:
                z = self.__minZ

            # # Roll
            # if 0 < roll < self.__maxRoll:
            #     roll = self.__maxRoll
            # elif self.__minRoll < roll < 0:
            #     roll = self.__minRoll

            # # Pitch
            # if pitch > self.__maxPitch:
            #     pitch = self.__maxPitch
            # elif pitch < self.__minPitch:
            #     pitch = self.__minPitch

            # # Yaw
            # if yaw > self.__maxYaw:
            #     yaw = self.__maxYaw
            # elif yaw < self.__minYaw:
            #     yaw = self.__minYaw

        return np.array([x, y, z, roll, pitch, yaw])

    def Quaternion2Euler(self, q, isDeg: bool = True):
        """
        Calculate the Euler angle from the Quaternion.


        Rotation matrix
        |m00 m01 m02 0|
        |m10 m11 m12 0|
        |m20 m21 m22 0|
        | 0   0   0  1|

        Parameters
        ----------
        q: np.ndarray
            Quaternion.
            [x, y, z, w]
        isDeg: (Optional) bool
            Returned angles are in degrees if this flag is True, else they are in radians.
            The default is True.

        Returns
        ----------
        rotEuler: np.ndarray
            Euler angle.
            [x, y, z]
        """

        qx = q[0]
        qy = q[1]
        qz = q[2]
        qw = q[3]

        # 1 - 2y^2 - 2z^2
        m00 = 1 - (2 * qy**2) - (2 * qz**2)
        # 2xy + 2wz
        m01 = (2 * qx * qy) + (2 * qw * qz)
        # 2xz - 2wy
        m02 = (2 * qx * qz) - (2 * qw * qy)
        # 2xy - 2wz
        m10 = (2 * qx * qy) - (2 * qw * qz)
        # 1 - 2x^2 - 2z^2
        m11 = 1 - (2 * qx**2) - (2 * qz**2)
        # 2yz + 2wx
        m12 = (2 * qy * qz) + (2 * qw * qx)
        # 2xz + 2wy
        m20 = (2 * qx * qz) + (2 * qw * qy)
        # 2yz - 2wx
        m21 = (2 * qy * qz) - (2 * qw * qx)
        # 1 - 2x^2 - 2y^2
        m22 = 1 - (2 * qx**2) - (2 * qy**2)

        # 回転軸の順番がX->Y->Zの固定角(Rz*Ry*Rx)
        # if m01 == -1:
        # 	tx = 0
        # 	ty = math.pi/2
        # 	tz = math.atan2(m20, m10)
        # elif m20 == 1:
        # 	tx = 0
        # 	ty = -math.pi/2
        # 	tz = math.atan2(m20, m10)
        # else:
        # 	tx = -math.atan2(m02, m00)
        # 	ty = -math.asin(-m01)
        # 	tz = -math.atan2(m21, m11)

        # 回転軸の順番がX->Y->Zのオイラー角(Rx*Ry*Rz)
        if m02 == 1:
            tx = math.atan2(m10, m11)
            ty = math.pi / 2
            tz = 0
        elif m02 == -1:
            tx = math.atan2(m21, m20)
            ty = -math.pi / 2
            tz = 0
        else:
            tx = -math.atan2(-m12, m22)
            if m02 >= 1:
                m02 = 1
            if m02 <= -1:
                m02 = -1
            ty = -math.asin(m02)
            tz = -math.atan2(-m01, m00)

        if isDeg:
            tx = np.rad2deg(tx)
            ty = np.rad2deg(ty)
            tz = np.rad2deg(tz)

        rotEuler = np.array([tx, ty, tz])
        return rotEuler

    def Euler2Quaternion(self, e):
        """
        Calculate the Quaternion from the Euler angle.

        Parameters
        ----------
        e: np.ndarray
            Euler.
            [x, y, z]

        Returns
        ----------
        rotQuat: np.ndarray
            Quaternion
            [x, y, z, w]
        """

        roll = np.deg2rad(e[0])
        pitch = np.deg2rad(e[1])
        yaw = np.deg2rad(e[2])

        cosRoll = np.cos(roll / 2.0)
        sinRoll = np.sin(roll / 2.0)
        cosPitch = np.cos(pitch / 2.0)
        sinPitch = np.sin(pitch / 2.0)
        cosYaw = np.cos(yaw / 2.0)
        sinYaw = np.sin(yaw / 2.0)

        q0 = cosRoll * cosPitch * cosYaw + sinRoll * sinPitch * sinYaw
        q1 = sinRoll * cosPitch * cosYaw - cosRoll * sinPitch * sinYaw
        q2 = cosRoll * sinPitch * cosYaw + sinRoll * cosPitch * sinYaw
        q3 = cosRoll * cosPitch * sinYaw - sinRoll * sinPitch * cosYaw

        rotQuat = [q1, q2, q3, q0]
        return rotQuat

    def Convert2Matrix(self, quaternion):
        qw, qx, qy, qz = quaternion[3], quaternion[1], quaternion[2], quaternion[0]
        matrix = np.array(
            [
                [qw, -qy, qx, qz],
                [qy, qw, -qz, qx],
                [-qx, qz, qw, qy],
                [-qz, -qx, -qy, qw],
            ]
        )

        return matrix
