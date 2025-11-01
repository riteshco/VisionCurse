import cv2
import dlib
import numpy as np
import time
from constants import WIN_WIDTH, WIN_HEIGHT

def run_eye_tracker(queue):
    """
    Runs the eye-tracking logic and puts (x, y) coordinates into the queue.
    """
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Cannot open webcam.")
            return

        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        
        # Simple calibration: Store the initial gaze ratio
        # A more complex calibration would be needed for perfect mapping.
        calibration_data = []
        print("EyeTracker: Calibrating... Look at the center of your screen for 5 seconds.")
        start_time = time.time()
        while time.time() - start_time < 5:
            _, frame = cap.read()
            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)
            
            if faces:
                landmarks = predictor(gray, faces[0])
                left_ratio = get_gaze_ratio([36, 37, 38, 39, 40, 41], landmarks, gray, frame)
                right_ratio = get_gaze_ratio([42, 43, 44, 45, 46, 47], landmarks, gray, frame)
                
                if left_ratio is not None and right_ratio is not None:
                    avg_ratio = (left_ratio + right_ratio) / 2
                    calibration_data.append(avg_ratio)
                
            
            cv2.imshow("Eye Tracker", frame)
            if cv2.waitKey(1) & 0xFF == 27: # ESC
                break
        
        if not calibration_data:
            print("Error: No face detected during calibration.")
            return
            
        center_gaze_ratio = np.mean(calibration_data)
        print(f"EyeTracker: Calibration complete. Center ratio: {center_gaze_ratio:.2f}")

        # Main tracking loop
        while True:
            _, frame = cap.read()
            frame = cv2.flip(frame, 1) # Flip horizontally
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)
            
            aim_x, aim_y = WIN_WIDTH / 2, WIN_HEIGHT / 2 # Default to center

            if faces:
                landmarks = predictor(gray, faces[0])
                
                left_ratio = get_gaze_ratio([36, 37, 38, 39, 40, 41], landmarks, gray, frame)
                right_ratio = get_gaze_ratio([42, 43, 44, 45, 46, 47], landmarks, gray, frame)
                
                if left_ratio is not None and right_ratio is not None:
                    avg_ratio = (left_ratio + right_ratio) / 2
                    
                    # Map the gaze ratio to screen coordinates
                    # This is a VERY simple mapping and would need real calibration
                    # for good results.
                    
                    # Horizontal mapping
                    gaze_diff = avg_ratio - center_gaze_ratio
                    
                    if gaze_diff > 0.1: # Looking right
                        aim_x = WIN_WIDTH * 0.75
                    elif gaze_diff < -0.1: # Looking left
                        aim_x = WIN_WIDTH * 0.25
                    else:
                        aim_x = WIN_WIDTH / 2
                    
                    # Vertical mapping (less reliable, just an example)
                    # For real vertical gaze, you'd analyze vertical pupil position.
                    # Here, we'll just keep it centered vertically.
                    aim_y = WIN_HEIGHT / 2
                    
                    # Put the new aim position in the queue
                    queue.put((int(aim_x), int(aim_y)))

            # Display the webcam feed (optional, good for debugging)
            cv2.imshow("Eye Tracker", frame)
            if cv2.waitKey(1) & 0xFF == 27: # ESC
                break
                
    except ImportError:
        print("Error: OpenCV or dlib not found.")
    except Exception as e:
        print(f"Eye tracking process failed: {e}")
    finally:
        if 'cap' in locals() and cap.isOpened():
            cap.release()
        cv2.destroyAllWindows()
        queue.put(None) # Signal to main process that it has stopped

def get_gaze_ratio(eye_points, landmarks, gray, frame):
    """
    Calculates the horizontal gaze ratio of one eye.
    """
    try:
        # Get region for one eye
        eye_region = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in eye_points], np.int32)
        
        # Create mask
        height, width = gray.shape
        mask = np.zeros((height, width), np.uint8)
        cv2.polylines(mask, [eye_region], True, 255, 2)
        cv2.fillPoly(mask, [eye_region], 255)
        
        # Apply mask to grayscale image
        eye = cv2.bitwise_and(gray, gray, mask=mask)
        
        # Isolate eye region, find bounds
        min_x = np.min(eye_region[:, 0])
        max_x = np.max(eye_region[:, 0])
        min_y = np.min(eye_region[:, 1])
        max_y = np.max(eye_region[:, 1])
        
        gray_eye = eye[min_y:max_y, min_x:max_x]
        
        # Threshold to find pupil
        _, threshold = cv2.threshold(gray_eye, 70, 255, cv2.THRESH_BINARY_INV)
        
        # Find contours to find pupil
        contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)
        
        if contours:
            # Get bounding rect of largest contour (the pupil)
            (x, y, w, h) = cv2.boundingRect(contours[0])
            pupil_center_x = x + w / 2
            
            # Calculate horizontal gaze ratio
            eye_width = max_x - min_x
            ratio = pupil_center_x / eye_width
            
            # Draw pupil on frame (for debugging)
            cv2.circle(frame, (min_x + int(pupil_center_x), min_y + int(y + h/2)), 3, (0, 255, 0), -1)
            
            return ratio
            
    except Exception:
        return None
    return None

if __name__ == '__main__':
    # This file is not meant to be run directly
    pass