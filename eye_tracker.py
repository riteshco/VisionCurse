import cv2
import dlib
import numpy as np
import time
import math
from constants import WIN_WIDTH, WIN_HEIGHT

def run_eye_tracker(queue):
    """
    Runs eye-tracking logic and puts the gaze ANGLE into the queue.
    """
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            queue.put(("ERROR", "Cannot open webcam."))
            return

        detector = dlib.get_frontal_face_detector()
        # This is the line that needs the .dat file
        predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        
        print("EyeTracker: Running. Look left and right to aim.")

        while True:
            _, frame = cap.read()
            if frame is None:
                time.sleep(0.1)
                continue
                
            frame = cv2.flip(frame, 1) # Flip horizontally
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)
            
            # Default to 0 degrees (straight ahead)
            gaze_angle = 0.0

            if faces:
                landmarks = predictor(gray, faces[0])
                
                # Get pupil centers
                left_pupil = get_pupil_center([36, 37, 38, 39, 40, 41], landmarks, gray, frame)
                right_pupil = get_pupil_center([42, 43, 44, 45, 46, 47], landmarks, gray, frame)
                
                # Get nose (center reference)
                nose_point = (landmarks.part(30).x, landmarks.part(30).y)
                
                if left_pupil and right_pupil:
                    # Calculate a single "gaze point" between the two pupils
                    gaze_x = (left_pupil[0] + right_pupil[0]) / 2
                    gaze_y = (left_pupil[1] + right_pupil[1]) / 2
                    
                    # --- This is the Vector Calculation ---
                    # Get vector from nose to gaze point
                    vec_x = gaze_x - WIN_WIDTH /2
                    vec_y = gaze_y - WIN_HEIGHT /2
                    
                    # Get the angle of that vector
                    # This is the "vector" you asked for
                    gaze_angle = math.atan2(vec_y, vec_x)
                    
                    # --- Debug View (optional) ---
                    # cv2.circle(frame, (int(gaze_x), int(gaze_y)), 5, (0, 255, 0), -1)
                    # cv2.circle(frame, nose_point, 5, (0, 0, 255), -1)
                    # cv2.line(frame, nose_point, (int(gaze_x), int(gaze_y)), (255, 0, 0), 2)
                
            # Put the new gaze angle in the queue
            queue.put(("AIM", gaze_angle))
            
            # --- Debug View (optional) ---
            # cv2.imshow("Eye Tracker", frame)
            # if cv2.waitKey(1) & 0xFF == 27: # ESC
            #     break
            
            time.sleep(0.01) # Small delay to not overwhelm the CPU
                
    except FileNotFoundError:
        queue.put(("ERROR", "Unable to open shape_predictor_68_face_landmarks.dat"))
    except Exception as e:
        queue.put(("ERROR", f"Eye tracking process failed: {e}"))
    finally:
        if 'cap' in locals() and cap.isOpened():
            cap.release()
        cv2.destroyAllWindows()
        queue.put(("STOPPED", None)) # Signal to main process

def get_pupil_center(eye_points, landmarks, gray, frame):
    """ Calculates the center of the pupil for one eye. """
    try:
        eye_region = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in eye_points], np.int32)
        
        min_x = np.min(eye_region[:, 0])
        max_x = np.max(eye_region[:, 0])
        min_y = np.min(eye_region[:, 1])
        max_y = np.max(eye_region[:, 1])
        
        gray_eye = gray[min_y:max_y, min_x:max_x]
        
        # Simple thresholding
        _, threshold = cv2.threshold(gray_eye, 50, 255, cv2.THRESH_BINARY_INV)
        
        # Find the center of the black area (pupil)
        moments = cv2.moments(threshold)
        if moments['m00'] != 0:
            pupil_x = int(moments['m10'] / moments['m00'])
            pupil_y = int(moments['m01'] / moments['m00'])
            
            # Return coordinates relative to the full frame
            return (min_x + pupil_x, min_y + pupil_y)
            
    except Exception:
        return None
    return None

if __name__ == '__main__':
    pass