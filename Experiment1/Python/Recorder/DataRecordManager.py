# -----------------------------------------------------------------------
# Author:   Takayoshi Hagiwara (KMD)
# Created:  2021/8/25
# Summary:  Data Recording Manager
# -----------------------------------------------------------------------

import numpy as np
import tqdm

from FileIO.FileIO import FileIO

class DataRecordManager:
    dictPosition = {}
    dictRotation = {}
    dictGripperValue = {}


    def __init__(self, participantNum: int = 2, otherRigidBodyNum: int = 1, otherRigidBodyNames: list = ['endEffector'], bendingSensorNum: int = 1) -> None:
        """
        Initialize class: DataRecordManager

        Parameters
        ----------
        participantNum: (Optional) int
            Number of participants
        otherRigidBodyNum: (Optional) int
            Number of rigid body objects except participants' rigid body
        otherRigidBodyNames: (Optional) list(str)
            Name list of rigid body objects except participants' rigid body
        bendingSensorNum: (Optional) int
            Number of bending sensors
        """
        
        self.participantNum         = participantNum
        self.otherRigidBodyNum      = otherRigidBodyNum
        self.otherRigidBodyNames    = otherRigidBodyNames
        self.bendingSensorNum       = bendingSensorNum

        for i in range(self.participantNum):
            self.dictPosition['participant'+str(i+1)] = []
            self.dictRotation['participant'+str(i+1)] = []
        
        for i in range(self.otherRigidBodyNum):
            self.dictPosition[self.otherRigidBodyNames[i]] = []
            self.dictRotation[self.otherRigidBodyNames[i]] = []
        
        for i in range(self.bendingSensorNum):
            self.dictGripperValue['gripperValue'+str(i+1)] = []


    def Record(self, position, rotation, bendingSensor):
        """
        Record the data.

        Parameters
        ----------
        position: dict
            Position
        rotation: dict
            Rotation
        bendingSensor: dict
            Bending sensor values
        """

        for i in range(self.participantNum):
            self.dictPosition['participant'+str(i+1)].append(position['participant'+str(i+1)])
            self.dictRotation['participant'+str(i+1)].append(rotation['participant'+str(i+1)])
        
        for i in range(self.otherRigidBodyNum):
            self.dictPosition[self.otherRigidBodyNames[i]].append(position[self.otherRigidBodyNames[i]])
            self.dictRotation[self.otherRigidBodyNames[i]].append(rotation[self.otherRigidBodyNames[i]])
        
        for i in range(self.bendingSensorNum):
            self.dictGripperValue['gripperValue'+str(i+1)].append([bendingSensor['gripperValue'+str(i+1)]])
    

    def ExportSelf(self, dirPath: str = 'ExportData'):
        """
        Export the data recorded in DataRecordManager as CSV format.

        Parameters
        ----------
        dirPath: (Optional) str
            Directory path (not include the file name).
        """

        fileIO = FileIO()

        transformHeader = ['x','y','z','qx','qy','qz','qw']
        bendingSensorHeader = ['bendingValue']

        print('\n---------- DataRecordManager.ExportSelf ----------')
        print('Writing: Participant transform...')
        for i in tqdm.tqdm(range(self.participantNum), ncols=150):
            npPosition = np.array(self.dictPosition['participant'+str(i+1)])
            npRotation = np.array(self.dictRotation['participant'+str(i+1)])
            npParticipantTransform = np.concatenate([npPosition, npRotation], axis=1)

            fileIO.ExportAsCSV(npParticipantTransform, dirPath, 'Transform_Participant_'+str(i+1), transformHeader)

        
        print('Writing: Other rigid body transform...')
        for i in tqdm.tqdm(range(self.otherRigidBodyNum), ncols=150):
            npPosition = np.array(self.dictPosition[self.otherRigidBodyNames[i]])
            npRotation = np.array(self.dictRotation[self.otherRigidBodyNames[i]])
            npRigidBodyTransform = np.concatenate([npPosition, npRotation], axis=1)

            fileIO.ExportAsCSV(npRigidBodyTransform, dirPath, 'Transform_'+self.otherRigidBodyNames[i], transformHeader)
        
        print('Writing: Gripper value...')
        for i in tqdm.tqdm(range(self.bendingSensorNum), ncols=150):
            npBendingSensorValue = np.array(self.dictGripperValue['gripperValue'+str(i+1)])
            fileIO.ExportAsCSV(npBendingSensorValue, dirPath, 'GripperValue_'+str(i+1), bendingSensorHeader)
        
        print('---------- Export completed ----------\n')