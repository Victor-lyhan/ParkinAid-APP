import math
import time

import cv2
import numpy as np
import pandas as pd
from pydantic import BaseModel
from tensorflow.keras.models import load_model
from ultralytics import YOLO

# Load the models
model = load_model('model/CV_NN_model_5l_multiValue.h5')
yolo_model = YOLO('yolov8n-pose.pt')


# feature extraction

def resize_image(image, scale_factor):
    # Calculate the new dimensions
    new_width = int(image.shape[1] * scale_factor)
    new_height = int(image.shape[0] * scale_factor)

    # Resize the image
    resized_image = cv2.resize(image, (new_width, new_height))

    return resized_image


class GetKeypoint(BaseModel):
    NOSE: int = 0
    LEFT_EYE: int = 1
    RIGHT_EYE: int = 2
    LEFT_EAR: int = 3
    RIGHT_EAR: int = 4
    LEFT_SHOULDER: int = 5
    RIGHT_SHOULDER: int = 6
    LEFT_ELBOW: int = 7
    RIGHT_ELBOW: int = 8
    LEFT_WRIST: int = 9
    RIGHT_WRIST: int = 10
    LEFT_HIP: int = 11
    RIGHT_HIP: int = 12
    LEFT_KNEE: int = 13
    RIGHT_KNEE: int = 14
    LEFT_ANKLE: int = 15
    RIGHT_ANKLE: int = 16


# Initialize DF
def initialize_df():
    df = pd.DataFrame(columns=['current_time',
                               'frame_time',
                               'index',
                               'right_ankle_x',
                               'right_ankle_y',
                               'right_knee_x',
                               'right_knee_y',
                               'right_hip_x',
                               'right_hip_y',
                               'magnitude1',
                               'magnitude2',
                               'angle_deg',
                               'angular_velocity',
                               'angular_acceleration'])
    return df


def fetch_df(source_path, show_video=False):
    # Previous frame angles, angular velocities, and angular accelerations
    prev_angle = None
    prev_angular_velocity = None
    angular_acceleration = None
    angular_velocity = None
    prev_time = 0
    scale_factor = 0.5
    get_keypoint = GetKeypoint()

    # Open video capture
    cap = cv2.VideoCapture(source_path)
    df = initialize_df()

    while cap.isOpened():
        try:
            ret, frame = cap.read()
            if not ret:
                break

            # Resize the image
            frame = resize_image(frame, scale_factor)
            frame_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000

            # Run YOLOv8 inference on the frame
            results = yolo_model(frame, conf=0.7)
            index = 0

            # Check if keypoints are detected -- issues with not identifying keypoints
            if results[0].keypoints is None:
                print("No Kepypoints detected in this frame. Skipping...")
                continue
            result_keypoint = results[0].keypoints.xyn.cpu().numpy()

            if len(result_keypoint) > 1 and result_keypoint[0][get_keypoint.RIGHT_ANKLE][0] > \
                    result_keypoint[1][get_keypoint.RIGHT_ANKLE][0]:
                index = 1
            # print('index:', index)

            # Extract landmarks for the foot (assuming only one person in the frame)
            right_ankle = result_keypoint[index][get_keypoint.RIGHT_ANKLE]
            right_knee = result_keypoint[index][get_keypoint.RIGHT_KNEE]
            right_hip = result_keypoint[index][get_keypoint.RIGHT_HIP]

            # Calculate the vectors
            vector1 = (right_knee[0] - right_ankle[0], right_knee[1] - right_ankle[1])
            vector2 = (right_hip[0] - right_ankle[0], right_hip[1] - right_ankle[1])

            # Calculate the angle between the vectors
            dot_product = vector1[0] * vector2[0] + vector1[1] * vector2[1]
            magnitude1 = math.sqrt(vector1[0] ** 2 + vector1[1] ** 2)
            magnitude2 = math.sqrt(vector2[0] ** 2 + vector2[1] ** 2)

            # Checking magnitude dot product -- having issues with script stopping
            # print(f"dot_product: {dot_product}, magnitude1: {magnitude1}, magnitude2: {magnitude2}")

            if magnitude1 == 0 or magnitude2 == 0:
                print("One of the magnitudes is zero, skipping frame")
                continue

            cos_angle = dot_product / (magnitude1 * magnitude2)
            cos_angle = max(-1.0, min(1.0, cos_angle))
            angle_rad = math.acos(cos_angle)

            # Convert the angle to degrees
            angle_deg = math.degrees(angle_rad)

            # Calculate time difference
            current_time = time.time()
            time_diff = current_time - prev_time
            # print(time_diff)
            # Calculate angular velocity
            if prev_angle is not None:
                angular_velocity = (angle_deg - prev_angle) / time_diff
                # print('Angular Velocity:', angular_velocity, 'deg/s')

            # Calculate angular acceleration
            if prev_angular_velocity is not None:
                angular_acceleration = (angular_velocity - prev_angular_velocity) / time_diff
                # print("Angular Acceleration (ML):", angular_acceleration, )

            # Update previous angle, angular velocity, angular acceleration, and time
            prev_angle = angle_deg
            prev_angular_velocity = angular_velocity
            prev_time = current_time

            # Create a dictionary for data at this current frame of video
            data = {
                'current_time': current_time,
                'frame_time': frame_time,
                'index': index,
                'right_ankle_x': right_ankle[0],
                'right_ankle_y': right_ankle[1],
                'right_knee_x': right_knee[0],
                'right_knee_y': right_knee[1],
                'right_hip_x': right_hip[0],
                'right_hip_y': right_hip[1],
                'magnitude1': magnitude1,
                'magnitude2': magnitude2,
                'angle_deg': angle_deg,
                'angular_velocity': angular_velocity,
                'angular_acceleration': angular_acceleration
            }

            # Append the data as a new row into the DF
            df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)

            if show_video:
                # Display the image with keypoints
                cv2.imshow('YOLOv8 Keypoints', results[0].plot())

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except Exception as e:
            print(e)

    return df


def predict_motion(video_path):
    var_predict = ['FoG Ratio', 'UPDRS-II', 'UPDRS-III', 'PIGD Score', 'Dyskinesia Score', 'MiniBestTest Score',
                   'TUG time', 'TUG dual-task time']
    # Fetch the dataframe
    df = fetch_df(video_path)
    # Get rid of outliers
    df = df[df <= 1000]

    ang_acc_std_df = df['angular_acceleration'].std()
    std_array = np.array([ang_acc_std_df])

    prediction = model.predict([std_array])
    prediction = {var_predict[i]: f"{prediction[0][i]:.2f}" for i in range(len(var_predict))}
    return prediction


if __name__ == "__main__":
    video_path = 'sample_video/PDFE01_1_short.mp4'
    prediction = predict_motion(video_path)
    print(prediction)
