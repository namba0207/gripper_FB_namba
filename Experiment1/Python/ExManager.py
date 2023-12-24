# -----------------------------------------------------------------------
# Author:   Takayoshi Hagiwara (KMD)
# Created:  2021/8/25
# Summary:  Experiment manager
# -----------------------------------------------------------------------

from ctypes import windll

from RobotArmController.RobotControlManager import RobotControlManager

if __name__ == "__main__":
    robotControlManager = RobotControlManager()
    # robotControlManager.SendDataToRobot(participantNum=2, executionTime=9999, frameRate=96, isFixedFrameRate=False, isChangeOSTimer=False, isExportData=True, isEnablexArm=True)

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

    # robotControlManager.LoadCellTest()
    # robotControlManager.AudioTest()
    # robotControlManager.eRubberTactileFeedbackTest()
    # robotControlManager.CheckGraph()

    # ----- Find audio device indexes ----- #
    # from VibrotactileFeedback.AudioDeviceIndexes import AudioDeviceIndexes
    # audioDeviceIndexes = AudioDeviceIndexes()
    # audioDeviceIndexes.FindWithName('Real')

    # while True:
    #     try:
    #         with open("data.txt", mode="a") as txt_file:
    #             txt_file.write(
    #                 str(text_class.pos)
    #                 + " "
    #                 + str(text_class.num_int)
    #                 + " "
    #                 + str(text_class.data_parts[2])
    #                 + " "
    #                 + str(time.perf_counter())
    #                 + "\n"
    #             )
    #         print(
    #             text_class.pos,
    #             text_class.num_int,
    #             text_class.data_parts[2],
    #             time.perf_counter(),
    #         )
    #         time.sleep(0.005)
    #     except KeyboardInterrupt:
    #         print("KeyboardInterrupt Stop:text")
    #         break
    print("halo")

    print("\n----- End program: ExManager.py -----")
