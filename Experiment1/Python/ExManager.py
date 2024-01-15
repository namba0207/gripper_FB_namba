# -----------------------------------------------------------------------
# Author:   Takayoshi Hagiwara (KMD)
# Created:  2021/8/25
# Summary:  Experiment manager
# -----------------------------------------------------------------------

from ctypes import windll

from RobotArmController.RobotControlManager import RobotControlManager

if __name__ == "__main__":
    robotControlManager = RobotControlManager()
    # ----- Debug mode ----- #
    robotControlManager.SendDataToRobot(
        participantNum=2,
        executionTime=9999,
        frameRate=150,
        isFixedFrameRate=False,
        isChangeOSTimer=False,
        isExportData=False,
        isEnablexArm=True,
    )

    print("\n----- End program: ExManager.py -----")
