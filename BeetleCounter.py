import cv2
import numpy as np
import os

def count_beetles(image_path):

    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"File path not found: {image_path}")

    # Load the image
    image = cv2.imread(image_path)

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Get threshold from half of the average_pixel_value which should ignore background
    threshold = (np.mean(gray)//2) + 10

    # Apply a binary threshold to get a binary image
    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)

    # Lists all connected components in binary and gives certain information like area
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary)

    # Creates blacked image of same size as binary
    filtered_binary = np.zeros_like(binary)

    # Iterate through all connected components but the background num_labels[0]
    for i in range(1, num_labels):
        # Filter out all connected component with an area less than 20
        if stats[i, cv2.CC_STAT_AREA] >= 20:
            filtered_binary[labels == i] = 255

    # Dilate the binary image to slightly enlarge the objects
    kernel = np.ones((3, 3), np.uint8)  # Adjust the kernel size as needed
    filtered_binary = cv2.dilate(filtered_binary, kernel, iterations=2)


    # Get height and width of image
    h, w = filtered_binary.shape[:2]
    # Mask needs to be 2 pixels larger than the image
    mask = np.zeros((h + 2, w + 2), np.uint8)
    # Assuming any dark shape found at the edge is the table turn it into background
    for y in range(h):
        if filtered_binary[y, 0] == 255:  # Left edge
            cv2.floodFill(filtered_binary, mask, (i, y), 0)
        if filtered_binary[y, w - 1] == 255:  # Right edge
            cv2.floodFill(filtered_binary, mask, (w - 1 - i, y), 0)
    for x in range(w):
        if filtered_binary[i, 0] == 255:  # Top edge
            cv2.floodFill(filtered_binary, mask, (x, i), 0)
        if filtered_binary[h - 1, x] == 255:  # Bottom edge
            cv2.floodFill(filtered_binary, mask, (x, h - 1 - i), 0)

    # Repeat Operation from above to remove averagely small Objects
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(filtered_binary, connectivity=8)
    total_area = np.sum(stats[1:, cv2.CC_STAT_AREA])  # Sum of areas of all components except the background
    average_area = total_area / (num_labels - 1)  # Average area excluding the background
    min_area = average_area * .3  # Minimum area to keep (30% of the average area)
    filtered_binary = np.zeros_like(filtered_binary)
    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] >= min_area:
            filtered_binary[labels == i] = 255

    # Final filter to remove large items found
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(filtered_binary, connectivity=8)
    total_area = np.sum(stats[1:, cv2.CC_STAT_AREA])  # Sum of areas of all components except the background
    average_area = total_area / (num_labels - 1)  # Average area excluding the background
    max_area = average_area * 2.5 # Maximum area to keep (250% of the average area)
    filtered_binary = np.zeros_like(filtered_binary)
    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] <= max_area:
            filtered_binary[labels == i] = 255

    # Find contours
    contours, _ = cv2.findContours(filtered_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Get number of contours
    final_beetle_count = len(contours)

    font_scale = min(h, w) / 1000  # Adjust the divisor to change the relative size of the font
    thickness = max(1, int(min(h, w) / 300))

    for idx, contour in enumerate(contours):
        # Draw the contour
        cv2.drawContours(image, [contour], -1, (0, 0, 255), 3)
        
        # Calculate the center of the contour for placing the number
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        else:
            cX, cY = 0, 0
        
        # Ensure the text is within image bounds
        text = str(idx + 1)
        (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
        cX = max(cX, text_width // 2)
        cY = max(cY, text_height // 2)
        cX = min(cX, w - text_width // 2)
        cY = min(cY, h - text_height // 2)
        
        # Add the number on top of the contour
        cv2.putText(image, text, (cX - text_width // 2, cY + text_height // 2), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 255), thickness)




    h, w = filtered_binary.shape[:2]

    # Calculate the size of the new square image
    new_size = max(h, w)

    # Calculate padding for each side
    pad_top = (new_size - h) // 2
    pad_bottom = new_size - h - pad_top
    pad_left = (new_size - w) // 2
    pad_right = new_size - w - pad_left

    square_image = cv2.copyMakeBorder(image, pad_top, pad_bottom, pad_left, pad_right, cv2.BORDER_CONSTANT, value=[0, 0, 0])


    return final_beetle_count, square_image

