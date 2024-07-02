# Beetle Counter API

This project provides a Flask-based API for counting beetles in images using computer vision techniques.

## Features

- Upload images via a RESTful API
- Process images to detect and count beetles
- Return the processed image with beetle annotations and the total count

## Requirements

- Python 3.x
- OpenCV (cv2)
- NumPy
- Flask

## Installation

1. Clone this repository
2. Install the required packages

## Usage

1. Start the Flask server (The server will run on `http://0.0.0.0:5000` by default.)

2. Send a POST request to `/upload` with an image file

3. The API will return a JSON response with:
- A message confirming successful processing
- The URL of the processed image
- The number of beetles detected

4. Access the processed image using the provided URL.

## API Endpoints

- `POST /upload`: Upload and process an image file
- `GET /processed/<filename>`: Retrieve a processed image

## How It Works

The beetle counting process involves several steps:

1. Convert the image to grayscale
2. Apply thresholding to create a binary image
3. Filter out small and large objects
4. Detect contours in the filtered image
5. Count and annotate the detected beetles

## Files

- `app.py`: Flask application handling the API endpoints
- `BeetleCounter.py`: Contains the image processing and beetle counting logic

## Notes

- Uploaded images are saved in an `uploads` folder
- Processed images are saved in a `processed` folder
- The API logs all incoming request headers for debugging purposes
