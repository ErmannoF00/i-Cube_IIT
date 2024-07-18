import enum

from icube.target_ref.src.data_handlers.base import BaseHandler
import numpy as np

CUBE_POSED_FACE = "1111111111111111"


class GraspState(enum.Enum):
    POSED = 0,
    GRABBED = 1


class GraspDetector(BaseHandler):
    """
    @package GraspDetector
    @brief a module to detect when the participant grasps the iCube or place it on a flat surface
    @author Dario Pasquali
    """
    def __init__(self, grab_tolerance=1):
        """
        @param grab_tolerance: how much being tolerant on classifying an acceleration as grasping
        """
        super().__init__()
        self.init_acc = None

        self.icube_state = GraspState.POSED
        self.grab_tolerance = grab_tolerance
        self.on_grab = None
        self.on_pose = None

    def set_on_grab_callback(self, on_grab):
        """
        What to do on grasp
        @param on_grab:
        @return:
        """
        self.on_grab = on_grab

    def set_on_pose_callback(self, on_pose):
        """
        What to do on pose
        @param on_pose:
        @return:
        """
        self.on_pose = on_pose

    def __icube_posed(self, touches):
        """
        Classify if the iCube is posed based on touches
        If only one face is fully active the cube is posed somewhere
        Otherwise the cube is held
        @param touches: a set of touches form the iCube
        @return: True if touched
        """

        if touches is None:
            return False
        full_covered_faces = touches.count(CUBE_POSED_FACE)
        touched_faces = ["1" in t for t in touches].count(True)
        return full_covered_faces == 1 and touched_faces == 1

    def __icube_moved(self, accelerometer):
        """
        Check if the cube is moving computing the euclidian distance of the accelerations with respect to when the iCube started
        @param accelerometer: set of accelerations
        @return:
        """
        return np.linalg.norm(accelerometer - self.init_acc) > self.grab_tolerance

    def handle(self, quaternions, touches, accelerometer):
        """
        Classifies participants' behavior
        @param quaternions:
        @param touches:
        @param accelerometer:
        @return:
        """
        if accelerometer is None or accelerometer == []:
            return False
        np_acc = np.array(accelerometer)
        if self.init_acc is None:
            self.init_acc = np_acc

        if self.icube_state == GraspState.POSED:
            if self.__icube_moved(accelerometer) and not self.__icube_posed(touches):
                self.icube_state = GraspState.GRABBED
                self.on_grab()

        if self.icube_state == GraspState.GRABBED:
            if self.__icube_posed(touches):
                self.icube_state = GraspState.POSED
                self.on_pose()
