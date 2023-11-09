# -----------------------------------------------------------------------
# Author:   Takayoshi Hagiwara (KMD)
# Created:  2021/8/25
# Summary:  Experiment manager
# -----------------------------------------------------------------------

from RobotArmController.RobotControlManager import RobotControlManager
from ctypes import windll

if __name__ == '__main__':
    robotControlManager = RobotControlManager()
    #robotControlManager.SendDataToRobot(participantNum=2, executionTime=9999, frameRate=96, isFixedFrameRate=False, isChangeOSTimer=False, isExportData=True, isEnablexArm=True)

    # ----- Debug mode ----- #
    robotControlManager.SendDataToRobot(participantNum=2, executionTime=9999, frameRate=150, isFixedFrameRate=False, isChangeOSTimer=False, isExportData=False, isEnablexArm=True)


    #robotControlManager.LoadCellTest()
    #robotControlManager.AudioTest()
    #robotControlManager.eRubberTactileFeedbackTest()
    #robotControlManager.CheckGraph()

    
    # ----- Find audio device indexes ----- #
    from VibrotactileFeedback.AudioDeviceIndexes import AudioDeviceIndexes
    audioDeviceIndexes = AudioDeviceIndexes()
    #audioDeviceIndexes.FindWithName('Real')

    print('\n----- End program: ExManager.py -----')