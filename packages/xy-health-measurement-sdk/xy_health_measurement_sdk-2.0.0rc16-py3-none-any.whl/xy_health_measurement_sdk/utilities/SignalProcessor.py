import cv2
import numpy as np
import mediapipe as mp
from importlib.resources import path as resources_path
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import FaceLandmarkerOptions, FaceLandmarker
from enum import Enum
from .Utility import Utility as util
from ..protos.Validation_pb2 import TooSmallImage, FaceLost, FaceOutOfBoundary


class FacialPosition(Enum):
    """
    人脸位置枚举
    """
    LEFT_FACE = 0
    RIGHT_FACE = 1
    NOSE = 2


class SignalProcessor(object):
    # 初始化mediapipe
    with resources_path('xy_health_measurement_sdk.resources', 'face_landmarker.task') as task:
        __options = FaceLandmarkerOptions(base_options=BaseOptions(model_asset_path=task),
                                          output_face_blendshapes=True, num_faces=1)

    @classmethod
    def detect(cls, frame):
        """
        特征提取
        """
        # 图像数据转换
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
        return cls.__detect_image(mp_image)

    @classmethod
    def detect_file(cls, file):
        mp_image = mp.Image.create_from_file(file)
        return cls.__detect_image(mp_image)

    @classmethod
    def __detect_image(cls, image):
        # 图像特征提取
        with FaceLandmarker.create_from_options(cls.__options) as landmarker:
            detection = landmarker.detect(image)
            return detection.face_landmarks[0] if len(
                detection.face_landmarks) > 0 else None, list(
                map(lambda b: b.score, detection.face_blendshapes[0])) if len(
                detection.face_blendshapes) > 0 else None, image.width, image.height

    @classmethod
    def validate(cls, verify_requirements_only=False, *args):
        """
        数据校验(error)
        """
        landmarks, width, height = args
        errors = []

        # 校验图像尺寸
        image_size_validation = util.get_validation(TooSmallImage)
        if image_size_validation:
            longer_side = width if width > height else height
            shorter_side = width + height - longer_side
            if longer_side < image_size_validation['min_height'] or shorter_side < image_size_validation['min_width']:
                errors.append(util.generate_error(TooSmallImage, not verify_requirements_only))

        # 校验是否存在人脸
        if not landmarks:
            errors.append(util.generate_error(FaceLost, not verify_requirements_only))

        # 查找人脸区域坐标，需要特别注意的是，mediapipe提取landmarks中x/y为相对于图像尺寸的比例，x*width、y*height 之后得到的才是绝对坐标
        min_x, min_y, max_x, max_y = width, height, 0, 0
        for landmark in landmarks:
            if landmark.x < min_x:
                min_x = landmark.x
            if landmark.x > max_x:
                max_x = landmark.x
            if landmark.y < min_y:
                min_y = landmark.y
            if landmark.y > max_y:
                max_y = landmark.y

        # 校验人脸边界
        if util.get_validation(FaceOutOfBoundary):
            if len(landmarks) < 478 or min_x < 0 or min_y < 0 or max_x > width or max_y > height:
                errors.append(util.generate_error(FaceOutOfBoundary, not verify_requirements_only))

        return min_x, min_y, max_x, max_y, errors

    @staticmethod
    def extract(*args):
        frame, landmarks, width, height = args
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        points = SignalProcessor.__get_points(landmarks, width, height)
        left_face_mask = SignalProcessor.__get_face_nose_mask(frame.shape, points, FacialPosition.LEFT_FACE)
        right_face_mask = SignalProcessor.__get_face_nose_mask(frame.shape, points, FacialPosition.RIGHT_FACE)
        nose_mask = SignalProcessor.__get_face_nose_mask(frame.shape, points, FacialPosition.NOSE)
        forehead_mask = SignalProcessor.__get_forehead_mask(frame.shape, points)
        full_face_mask = SignalProcessor.__get_full_face_mask(frame.shape, left_face_mask, right_face_mask,
                                                              forehead_mask)
        return tuple(map(lambda mask: cv2.mean(frame, mask=cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)),
                         (left_face_mask, right_face_mask, forehead_mask, full_face_mask, nose_mask)))

    @staticmethod
    def __get_points(*args):
        landmarks, width, height = args
        points = []
        for landmark in landmarks:
            x, y = int(landmark.x * width), int(landmark.y * height)
            points.append((x, y))
        return points

    @staticmethod
    def __get_face_nose_mask(shape, points, position: FacialPosition):
        left_face = (232, 31, 50, 142)
        match position:
            case FacialPosition.LEFT_FACE:
                roi_points = left_face
            case FacialPosition.RIGHT_FACE:
                roi_points = (452, 261, 280, 371)
            case FacialPosition.NOSE:
                roi_points = (6, 122, 209, 49, 129, 64, 98, 97, 2, 326, 327, 294, 358, 279, 360, 351)
            case _:
                raise TypeError('invalid FacialPosition')

        black = np.zeros(shape, np.uint8)
        _points = []
        for i in range(len(left_face)):
            _points.append(points[roi_points[i]])
        _points = np.array(_points)
        cv2.fillPoly(black, [_points], (255, 255, 255))
        return black

    @staticmethod
    def __get_forehead_mask(shape, points):
        black = np.zeros(shape, np.uint8)
        pnts = [points[63], points[105], points[66], points[107],
                points[336], points[296], points[334], points[293]]
        nose_length = int(0.6 * (points[168][1] - points[2][1]))
        pnts.append((points[334][0], points[334][1] + nose_length))
        pnts.append((points[105][0], points[105][1] + nose_length))
        pnts = np.array(pnts)
        cv2.fillPoly(black, [pnts], (255, 255, 255))
        return black

    @staticmethod
    def __get_full_face_mask(shape, left_face_mask, right_face_mask, forehead_mask):
        black = np.zeros(shape, np.uint8)
        black = cv2.bitwise_or(src1=black, src2=left_face_mask)
        black = cv2.bitwise_or(src1=black, src2=right_face_mask)
        black = cv2.bitwise_or(src1=black, src2=forehead_mask)
        return black
