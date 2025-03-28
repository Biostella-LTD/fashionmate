"""
Main FaceAnalyzer class for the face analyzer package.
Orchestrates the analysis process by using specialized modules.
"""

import json
import os
import time
import cv2
import dlib
from imutils import face_utils
from pydantic import HttpUrl
from rembg import remove  
import numpy as np
import warnings  
from urllib3.exceptions import NotOpenSSLWarning  

warnings.simplefilter('ignore', NotOpenSSLWarning)  
# Import specialized modules
from src.eye_shape import analyze_eyes
from src.face_shape import analyze_face_shape
from src.hair_color import analyze_hair_color
from src.skin_tone import analyze_skin_tone
from src.utils import download_image, logger

# Import exceptions
from src.analysis_exceptions import (
    FaceAnalysisResponseError,
    ImageDownloadError,
    ModelError,
    NoFaceDetectedError,
)


class FaceAnalyzer:
    """
    A class for analyzing facial features from images.
    Orchestrates the analysis of face shape, eye shape, skin tone and hair color from an image URL.
    """

    def __init__(self, landmark_predictor_path=None):
        """
        Initialize the FaceAnalyzer with necessary detectors and predictors.

        Args:
            landmark_predictor_path (str, optional): Path to the dlib facial landmark predictor file.
                                                   If None, will look in standard locations.
        """
        # If no path provided, try to find the predictor file in standard locations
        if landmark_predictor_path is None:
            # Try model directory relative to current file (src directory)
            current_dir = os.path.dirname(os.path.abspath(__file__))

            # Check for model directory within src
            model_dir = os.path.join(current_dir, "model")
            landmark_predictor_path = os.path.join(
                model_dir, "shape_predictor_68_face_landmarks.dat"
            )
        self.landmark_predictor_path = landmark_predictor_path
        if os.path.exists(landmark_predictor_path):
            logger.info(
                f"Initializing FaceAnalyzer with predictor: {landmark_predictor_path}"
            )
        else:
            raise FileNotFoundError(f"Not found: {landmark_predictor_path}")

        # Initialize dlib's face detector and facial landmark predictor
        try:
            self.detector = dlib.get_frontal_face_detector()
            self.predictor = dlib.shape_predictor(landmark_predictor_path)
            logger.info("Face detector and predictor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize detector or predictor: {str(e)}")
            raise ModelError(f"Failed to initialize models: {str(e)}")

    def analyze(self, image_url):  
        """  
        Analyze an image and return face attributes.  
        Orchestrates the analysis by calling specialized modules.  
    
        Args:  
            image_url (str): URL of the image to analyze  
    
        Returns:  
            dict: Dictionary containing face_shape, eye_shape, skin_tone, and hair_color  
        """  
        logger.info(f"Starting analysis for image: {image_url}")  
        start_time = time.time()  
    
        # Initialize result with default values  
        result = {  
            "face_shape": "Unknown",  
            "eye_shape": "Unknown",  
            "skin_tone": "Unknown",  
            "hair_color": "Unknown",  
            "face_image_url": image_url  # Removed HttpUrl for simplicity  
        }  
    
        # Download and prepare image  
        try:  
            image = download_image(image_url)  
            # Ensure the image is in RGB format  
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  
            
            # Encode image as PNG in memory  
            is_success, buffer = cv2.imencode(".png", image_rgb)  
            if not is_success:  
                logger.error("Could not encode image to PNG format")  
                raise ImageDownloadError("Failed to encode image to PNG format.")  
    
            # Remove background  
            output_bytes = remove(buffer.tobytes())  
            output_array = np.frombuffer(output_bytes, np.uint8)  
            output_image = cv2.imdecode(output_array, cv2.IMREAD_UNCHANGED)  
            cv2.imwrite("output.png", output_image)  
    
        except Exception as e:  
            logger.exception(f"Error downloading or processing image: {str(e)}")  
            raise ImageDownloadError(f"Failed to process image: {str(e)}")  
    
        # Detect faces  
        logger.info("Detecting faces in image")  
        
        # Check if image has alpha channel  
        if output_image.shape[2] == 4:  
            # Convert RGBA to RGB  
            output_image = cv2.cvtColor(output_image, cv2.COLOR_RGBA2RGB)  
        else:  
            # Ensure image is in RGB format  
            output_image = cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB)  
    
        faces = self.detector(output_image)  
    
        if len(faces) == 0:  
            logger.warning("No faces detected in the image")  
            raise NoFaceDetectedError("No faces detected in the image")  
    
        # Log number of faces detected  
        logger.info(f"Detected {len(faces)} faces, analyzing the first one")  
    
        # Analyze the first face detected  
        face = faces[0]  
        landmarks = self.predictor(output_image, face)  
        landmarks = face_utils.shape_to_np(landmarks)  
    
        # Analyze face shape using specialized module  
        result["face_shape"] = analyze_face_shape(landmarks)  
    
        # Analyze eye shape using specialized module  
        result["eye_shape"] = analyze_eyes(landmarks)  
    
        # Analyze skin tone using specialized module  
        result["skin_tone"] = analyze_skin_tone(image, landmarks)  
    
        # Analyze hair color using the new specialized module  
        result["hair_color"] = analyze_hair_color(image, landmarks)  
    
        # Calculate and log total processing time  
        total_time = time.time() - start_time  
        logger.info(f"Analysis completed in {total_time:.2f} seconds")  
        logger.info(f"{result=}")  
    
        return result  