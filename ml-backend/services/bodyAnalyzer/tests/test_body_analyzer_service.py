import subprocess
import requests
import time
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils import logger
from app import BodyAnalysisResponse


def send_post_request(url: str, image_url: str):
    """
    Sends a POST request to the FastAPI app with a JSON payload containing the image URL.

    Args:
        url (str): The URL of the FastAPI endpoint.
        image_url (str): The URL of the image to be analyzed.

    Returns:
        Response: The response from the FastAPI app.
    """
    headers = {"Content-Type": "application/json"}

    data = {"url": image_url}

    # Send the POST request
    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        logger.info("Request was successful.")
    else:
        logger.info(f"Request failed with status code: {response.status_code}")

    return response


def test_full_service():
    # Define the command to source the virtual environment and run app.py
    command = "python ml-backend/services/bodyAnalyzer/app.py"
    image_url = "https://media.istockphoto.com/id/523150985/photo/full-body-portrait-of-a-handsome-young-man-smiling.jpg?s=612x612&w=0&k=20&c=dWBzZLrPBOkzk3LG7CKMUPCMe40cWclIidOvNg2_mVw="
    url = "http://0.0.0.0:8000/analyze"
    try:
        # Run the subprocess in the background using Popen
        process = subprocess.Popen(
            command,
            text=True,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        logger.info(f"Started process with PID {process.pid}")
        time.sleep(10)
        # Example usage
        response = send_post_request(url, image_url)
        response = BodyAnalysisResponse(**response)
        # Print the response
        logger.info(response.json())
        stdout, stderr = (
            process.communicate()
        )  # This will block until the process finishes
        logger.info("Output:", stdout)
        logger.info("Errors:", stderr)
    except Exception as e:
        logger.info(f"Error starting the subprocess: {e}")


if __name__ == "__main__":
    test_full_service()
