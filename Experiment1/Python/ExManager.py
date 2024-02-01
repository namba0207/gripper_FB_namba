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
# AttributeError: module 'numpy' has no attribute 'quaternion'の場合、何も設定いじってなければ一度全部電源切って再起動する！2024/01/23
# numpyでモーキャプ取れてて、ロボ動かない、剛体のID番号が1、2になってない！！キャリブレーション後には１，２にしてやり直す。
# numpy quaetrnionのとき、基本的な剛体座標とれるか見た後に戻ってる。2024/01/31
