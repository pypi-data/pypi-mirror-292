import configparser
import glob
import inspect
import json
import os

import cv2
import numpy as np

from openmmla_vision.utils.input_utils import flush_input, get_function_calibrator
from openmmla_vision.utils.logger_utils import get_logger


class CameraCalibrator:
    logger = get_logger('camera-calibrator')

    def __init__(self, project_dir: str = None, config_path: str = None):
        # Set the project root directory
        if project_dir is None:
            caller_frame = inspect.stack()[1]
            caller_module = inspect.getmodule(caller_frame[0])
            if caller_module is None:
                self.project_dir = os.getcwd()
            else:
                self.project_dir = os.path.dirname(os.path.abspath(caller_module.__file__))
        else:
            self.project_dir = project_dir

        # Determine the configuration path
        if config_path:
            if os.path.isabs(config_path):
                self.config_path = config_path
            else:
                self.config_path = os.path.join(self.project_dir, config_path)
        else:
            self.config_path = os.path.join(self.project_dir, 'conf/video_base.ini')

        # Check if the configuration file exists
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found at {self.config_path}")

        self.cameras_dir = os.path.join(self.project_dir, 'camera_calib/cameras')
        os.makedirs(self.cameras_dir, exist_ok=True)

        self.config = configparser.ConfigParser()
        self.config.read(self.config_path)
        self.res_width = int(self.config['DEFAULT']['res_width'])
        self.res_height = int(self.config['DEFAULT']['res_height'])

        # Checkerboard dimensions
        self.CHECKERBOARD = (6, 9)

        # Termination criteria
        self.subpix_criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # Object points array
        self.objp = np.zeros((1, self.CHECKERBOARD[0] * self.CHECKERBOARD[1], 3), np.float32)
        self.objp[0, :, :2] = np.mgrid[0:self.CHECKERBOARD[0], 0:self.CHECKERBOARD[1]].T.reshape(-1, 2)

        # Lists to store object points and image points
        self.obj_points = []
        self.img_points = []

    def run(self):
        func_map = {1: self._capture_images, 2: self._calibrate_camera}
        while True:
            try:
                select_fun = get_function_calibrator()
                if select_fun == 0:
                    self.logger.info("Exiting video synchronizer...")
                    break
                func_map.get(select_fun, lambda: print("Invalid option."))()
            except (Exception, KeyboardInterrupt) as e:
                self.logger.warning("%s, Come back to the main menu.", e, exc_info=True)

    def _capture_images(self):
        resolution = [self.res_width, self.res_height]
        flush_input()
        camera_name = input("Enter the camera name for capturing images: ")
        saved_directory = os.path.join(self.cameras_dir, camera_name)
        os.makedirs(saved_directory, exist_ok=True)

        available_seeds = self._detect_video_seeds()
        camera_seed = self._choose_camera_seed(available_seeds)
        if camera_seed is None:
            self.logger.warning("No available camera seed found.")
            return

        cam = cv2.VideoCapture(camera_seed)
        cam.set(3, resolution[0])  # Set horizontal resolution
        cam.set(4, resolution[1])  # Set vertical resolution
        # cam.set(cv2.CAP_PROP_AUTOFOCUS, 1)
        # cam.set(cv2.CAP_PROP_SHARPNESS, 100) # 'value' ranges from 0 to the maximum sharpness value supported.

        try:
            self.capture_and_save_image(cam, saved_directory)
        finally:
            cam.release()
            cv2.destroyAllWindows()
            cv2.waitKey(1)

    def _detect_video_seeds(self):
        available_video_seeds = []
        number_of_detected_seeds = 0
        for i in range(4):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                print(f"{number_of_detected_seeds} : Camera seed {i} is available.")
                number_of_detected_seeds += 1
                available_video_seeds.append(i)
            cap.release()

        if 'RTMP' in self.config and 'video_streams' in self.config['RTMP']:
            video_stream_list = self.config['RTMP']['video_streams'].split(',')
            for streams in video_stream_list:
                if streams:
                    print(f"{number_of_detected_seeds} : RTMP stream {streams} is available.")
                    available_video_seeds.append(streams)
                    number_of_detected_seeds += 1

        return available_video_seeds

    def _choose_camera_seed(self, available_video_seeds):
        if not available_video_seeds:
            return None
        while True:
            try:
                seed_id = int(input("Choose your video seed id: "))
                if 0 <= seed_id < len(available_video_seeds):
                    return available_video_seeds[seed_id]
                else:
                    self.logger.warning("Invalid selection. Please choose a valid video seed.")
            except ValueError:
                self.logger.warning("Please enter a valid number.")

    def _calibrate_camera(self):
        camera_name = self._select_camera()
        selected_path = os.path.join(self.cameras_dir, camera_name)
        is_fisheye = input("Is the camera a fisheye lens? (Y/n): ").lower() == 'y'

        try:
            images = glob.glob(os.path.join(selected_path, '*.jpg'))
            for img_file in images:
                img = cv2.imread(img_file)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                ret, corners = cv2.findChessboardCorners(gray, self.CHECKERBOARD,
                                                         cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)
                if ret:
                    self.obj_points.append(self.objp)
                    corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1),
                                                self.subpix_criteria) if not is_fisheye else corners
                    self.img_points.append(corners2)
                    cv2.drawChessboardCorners(img, self.CHECKERBOARD, corners2, ret)
                    cv2.imshow('img', img)
                    cv2.waitKey(0)
            cv2.destroyAllWindows()
            cv2.waitKey(1)

            if is_fisheye:
                ret, K, D, rvecs, tvecs = cv2.fisheye.calibrate(
                    self.obj_points, self.img_points, gray.shape[::-1], None, None,
                    flags=(cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC + cv2.fisheye.CALIB_CHECK_COND +
                           cv2.fisheye.CALIB_FIX_SKEW),
                    criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-6))
            else:
                ret, K, D, rvecs, tvecs = cv2.calibrateCamera(
                    self.obj_points, self.img_points, gray.shape[::-1], None, None)

            self._update_configuration(camera_name, K, D, is_fisheye)
        except Exception as e:
            self.logger.error("Error occurred during calibration: %s", e, exc_info=True)
        finally:
            self._clean_up()

    def _select_camera(self):
        directories = [d for d in os.listdir(self.cameras_dir) if os.path.isdir(os.path.join(self.cameras_dir, d))]
        for index, directory in enumerate(directories):
            print(f"{index}: {directory}")
        flush_input()
        choice = int(input("Enter the index of the camera folder you'd like to use: "))
        return directories[choice]

    def _clean_up(self):
        self.obj_points = []
        self.img_points = []

    def _update_configuration(self, camera_name, K, D, is_fisheye):
        k_list = K.tolist()
        d_list = D.tolist()
        k_str = json.dumps(k_list)
        d_str = json.dumps(d_list)
        params_str = json.dumps([K[0, 0], K[1, 1], K[0, 2], K[1, 2]])

        self.config[camera_name] = {
            'fisheye': str(is_fisheye),
            'params': params_str,
            'K': k_str,
            'D': d_str
        }

        with open(self.config_path, 'w') as configfile:
            self.config.write(configfile)
        print(f"Configuration updated for {camera_name}.")

    @staticmethod
    def capture_and_save_image(cam, directory):
        image_number = 1
        print("Press 'c' to capture the image, or 'q' to quit.")
        while cam.isOpened():
            result, image = cam.read()
            if result:
                cv2.imshow("Real-Time Capture", image)
                key = cv2.waitKey(1) & 0xFF

                if key == ord('c'):
                    filename = f"{directory}/{image_number}.jpg"
                    cv2.imwrite(filename, image)
                    print(f"Image captured as {filename}")
                    cv2.imshow("Captured Image", image)
                    cv2.waitKey(1)
                    flush_input()
                    user_input = input("Are you satisfied with the image? (Y/n): ")
                    if user_input.lower() == 'y':
                        image_number += 1
                        print(f"Image saved as {filename}")
                    else:
                        print("Image discarded. Continue capturing...")
                        os.remove(filename)
                    cv2.destroyWindow("Captured Image")
                elif key == ord('q'):
                    return
            else:
                print("No image detected. Please try again.")
                return
