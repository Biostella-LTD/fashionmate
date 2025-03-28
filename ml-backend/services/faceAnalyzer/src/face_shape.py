"""
Face shape analysis module.
Handles the detection and classification of face shapes from facial landmarks.
"""

import numpy as np

from src.utils import logger


def analyze_face_shape(landmarks):
    """
    Determine face shape based on facial landmarks.
    
    Args:
        landmarks (numpy.ndarray): Facial landmarks from dlib's shape predictor
            
    Returns:
        str: Detected face shape ("Oval", "Round", "Square", "Oblong", or "Unknown")
    """
    logger.info("Analyzing face shape")
    try:
        # Extract relevant landmark points
        jawline = landmarks[0:17]  # Jawline (0-16)
        cheekbones = [landmarks[1], landmarks[15]]  # Cheekbones (1, 15)
        forehead = [landmarks[19], landmarks[24]]  # Forehead width (19, 24)
        chin = landmarks[8]  # Chin tip

        # Calculate key measurements
        face_width = np.linalg.norm(jawline[0] - jawline[-1])  # Jaw corner to corner
        face_height = np.linalg.norm(landmarks[27] - chin)  # Forehead to chin
        jaw_width = np.linalg.norm(jawline[4] - jawline[12])  # Jaw width at curve

        # Calculate facial ratios
        ratio_width_height = face_width / face_height
        ratio_jaw_face_width = jaw_width / face_width

        logger.debug(f"Face measurements - Width/Height: {ratio_width_height:.2f}, Jaw/Face: {ratio_jaw_face_width:.2f}")

        if ratio_width_height < 1.15:  
            face_shape = "Oblong"  
          
        elif 0.85 <= ratio_width_height < 1.3 and ratio_jaw_face_width < 0.9:  
            face_shape = "Oval"  
          
        elif 0.85 <= ratio_width_height < 1.15 and ratio_jaw_face_width >= 0.9:  
            face_shape = "Square"  
          
        elif ratio_width_height < 0.85:  
            face_shape = "Round"  
          
        else:  
            face_shape = "Unknown"  
        logger.info(f"Detected face shape: {face_shape}")
        return face_shape
            
    except Exception as e:
        logger.error(f"Error analyzing face shape: {str(e)}")
        return "Unknown"