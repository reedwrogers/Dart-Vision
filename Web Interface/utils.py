from shapely.geometry import Point, Polygon
import json
import psycopg2
from PIL import Image
from io import BytesIO
import base64
import matplotlib.pyplot as plt
from psycopg2 import sql
from scipy.ndimage import rotate
import cv2
import numpy as np
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import rotate
import io
import base64
from PIL import Image
import psycopg2
from PIL import Image
import matplotlib.pyplot as plt
from io import BytesIO
import matplotlib.patches as patches

def aruco_homography(img):
    # Load image
    # img = cv2.imread(img)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Define the ArUco dictionary and parameters
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_ARUCO_ORIGINAL)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)
    
    # Detect ArUco markers
    markerCorners, markerIds, rejectedCandidates = detector.detectMarkers(img)
    
    # print("Detected marker IDs:", markerIds)
    # print("Detected marker corners:", markerCorners)
    
    # Initialize src_rect
    src_rect = None
    
    # Check if we found any markers
    if markerIds is not None:
        # Create a mapping from marker ID to its corner
        id_to_corner = {8: None, 10: None, 9: None, 7: None}
        
        for i, marker_id in enumerate(markerIds.flatten()):
            if marker_id in id_to_corner:
                id_to_corner[marker_id] = markerCorners[i][0]  # Store the corner for the corresponding ID
    
        # Check if all required markers were found
        if all(corner is not None for corner in id_to_corner.values()):
            # Map corners based on your description
            src_rect = np.float32([
                id_to_corner[7][0],  # Bottom Right (ID 7) -> Top Left
                id_to_corner[10][1], # Top Right (ID 10) -> Bottom Left
                id_to_corner[9][0],  # Bottom Left (ID 9) -> Top Right
                id_to_corner[8][1]   # Top Left (ID 8) -> Bottom Right
            ])
        else:
            raise ValueError("Not all required ArUco markers were found.")
    else:
        raise ValueError("No ArUco markers detected.")
    
    # Define the destination rectangle
    width = 2000
    height = 2000  
    dst_rect = np.float32([
        [width - 1, height - 1],  # id 7
        [width - 1, 0],           # id 10
        [0, height - 1],  # id 9
        [0,0]          # id 8
    ])
    
    # Compute transform and warp
    M = cv2.getPerspectiveTransform(src_rect, dst_rect)
    warped = cv2.warpPerspective(img, M, (width, height))
    warped_rgb = cv2.cvtColor(warped, cv2.COLOR_BGR2RGB)
    
    # Save the resulting warped image
    # output_path = "/home/tars/Projects/Dart-Vision/Sample Images/aruco_result_3.jpg"
    # cv2.imwrite(output_path, warped)
    
    # Plotting the results
    # plt.figure(figsize=(14, 7))
    
    # plt.subplot(1, 2, 1)
    # plt.imshow(img_rgb)
    # if markerIds is not None:
    #     for corner in markerCorners:
    #         plt.scatter(corner[0][:, 0], corner[0][:, 1], c='red', s=30)
    # plt.scatter(src_rect[:, 0], src_rect[:, 1], c='blue', s=30)  # Show the src_rect points
    # plt.title("Original Image with Detected ArUco Markers")
    # plt.axis('off')
    
    # plt.subplot(1, 2, 2)
    # plt.imshow(warped_rgb)
    # plt.title("Warped Frontal View of Dartboard")
    # plt.axis('off')
    
    # plt.tight_layout()
    # plt.show()

    return warped

def find_best_rotation(img1, img2, angle_range=(-10, 10), step=1):
    best_angle = 0
    min_mse = float('inf')
    best_rotated_img = img2

    # Use np.arange for fractional steps
    for angle in np.arange(angle_range[0], angle_range[1] + step, step):
        rotated_img = rotate_image(img2, angle)
        mse = calculate_mse(img1, rotated_img)

        if mse < min_mse:
            min_mse = mse
            best_angle = angle
            best_rotated_img = rotated_img

    return best_angle, best_rotated_img

def resize_images(img1, img2):
    # Resize img2 to match img1 if they are not the same size
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]), interpolation=cv2.INTER_AREA)
    return img1, img2

def rotate_aruco(original, blank):

    img1 = cv2.imread(blank)

    img2 = original
    img1, img2 = resize_images(img1, img2)
    best_angle, best_rotated_img = find_best_rotation(img1, img2, angle_range=(-10, 10), step=.5)

    # Save the rotated image with "_rotated" appended to the filename
    # cv2.imwrite("../Sample Images/best_rotation_image.jpg", best_rotated_img)

    visualize_results(img1, img2, best_rotated_img, best_angle)
    return best_rotated_img

def visualize_results(img1, img2, best_rotated_img, best_angle):
    # Plot the images
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 3, 1)
    plt.title('Image 1')
    plt.imshow(cv2.cvtColor(img1, cv2.COLOR_BGR2RGB))
    plt.axis('off')

    plt.subplot(1, 3, 2)
    plt.title('Best Rotated Image (Angle: {})'.format(best_angle))
    plt.imshow(cv2.cvtColor(best_rotated_img, cv2.COLOR_BGR2RGB))
    plt.axis('off')

    plt.subplot(1, 3, 3)
    plt.title('Original Image 2')
    plt.imshow(cv2.cvtColor(img2, cv2.COLOR_BGR2RGB))
    plt.axis('off')

    plt.tight_layout()
    plt.show()

def load_images(image_path1, image_path2):
    # Load the images
    img1 = cv2.imread(image_path1)
    img2 = cv2.imread(image_path2)

    if img1 is None or img2 is None:
        raise ValueError("One of the images could not be loaded.")

    return img1, img2

def get_tips_and_compute_score(rotated_aruco):
    img = rotated_aruco
    
    # Convert to HSV color space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Neon yellow dart color range in HSV (tweak as needed)
    lower_yellow = np.array([25, 120, 120])
    upper_yellow = np.array([35, 255, 255])
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
    # Morphological operations to clean up the mask
    kernel = np.ones((5, 5), np.uint8)
    mask_clean = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_DILATE, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    dart_coords = []
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 150:  # Adjust area threshold as needed
            # Draw contour
            cv2.drawContours(img, [cnt], -1, (0, 255, 0), 2)
    
            # Compute bounding box
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 200, 200), 1)
    
            # Estimate dart tip as the rightmost point in the contour
            tip_index = cnt[:, :, 0].argmax()  # max x-coordinate
            tip = tuple(cnt[tip_index][0])
            dart_coords.append(tip)
            cv2.circle(img, tip, 8, (255, 0, 0), -1)  # Blue = estimated dart tip

    regions = create_annotations()
    
    # Classify each detected dart tip
    scores = []
    for x, y in dart_coords:
        label = classify_dart_hit(x, y, regions)
        scores.append(label)
        print(f"Dart at ({x}, {y}) hit: {label}")
    
    # Show the cleaned mask and final image
    # plt.figure(figsize=(12, 10))
    
    # plt.subplot(1, 2, 1)
    # plt.imshow(mask_clean, cmap='gray')
    # plt.title("Mask for Neon Yellow Darts")
    # plt.axis('off')
    
    # plt.subplot(1, 2, 2)
    # plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    # plt.title("Detected Darts with Tip Marked")
    # plt.axis('off')
    
    # plt.tight_layout()
    # plt.show()

    return json.dumps({
        "status": "success",
        "scores": scores
    })

def classify_dart_hit(x, y, regions):
    point = Point(x, y)
    for region in regions:
        poly = Polygon(region["polygon"])
        if poly.contains(point):
            return region["label"]
    return "missed"

def create_annotations():
    
    with open("../Sample Images/labels_updated_annotations_2025-04-15-07-00-25.json", "r") as f:
        data = json.load(f)
    
    # Map category_id to category name
    category_lookup = {cat['id']: cat['name'] for cat in data['categories']}
    
    # Extract polygons and their labels
    regions = []
    for ann in data['annotations']:
        category = category_lookup[ann['category_id']]
        segmentation = ann['segmentation'][0]  # 1 polygon per segment
        polygon = [(segmentation[i], segmentation[i+1]) for i in range(0, len(segmentation), 2)]
        regions.append({"label": category, "polygon": polygon})

    return regions

def rotate_image(image, angle):
    # Get the image dimensions
    (h, w) = image.shape[:2]
    # Calculate the center of the image
    center = (w // 2, h // 2)
    # Perform the rotation
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h))
    return rotated

def calculate_mse(img1, img2):
    # Calculate Mean Squared Error between two images
    return np.mean((img1.astype(np.float32) - img2.astype(np.float32)) ** 2)

def display_coco_regions(image, coco_json_path, image_id=1):
    # Load COCO JSON
    with open(coco_json_path, 'r') as f:
        coco = json.load(f)

    # Get category map (id → name)
    cat_map = {cat['id']: cat['name'] for cat in coco['categories']}

    # Get annotations for the specific image
    annotations = [ann for ann in coco['annotations'] if ann['image_id'] == image_id]

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(image)
    ax.set_title("COCO Dartboard Regions")

    for ann in annotations:
        category_name = cat_map[ann['category_id']]
        for seg in ann['segmentation']:
            # Convert flat list to Nx2 array
            poly = np.array(seg).reshape((-1, 2))
            patch = patches.Polygon(poly, closed=True, fill=False, edgecolor='cyan', linewidth=2)
            ax.add_patch(patch)

            # Skip labeling bullseye and double bullseye
            if category_name.lower() in ['bullseye', 'double bullseye']:
                continue

            # Label in the center of the polygon
            centroid = np.mean(poly, axis=0)
            ax.text(centroid[0], centroid[1], category_name, color='white', fontsize=9,
                    ha='center', va='center', weight='bold',
                    bbox=dict(facecolor='black', alpha=0.5, boxstyle='round'))

    plt.axis('off')
    plt.show()

def run_workflow(img_original,img_blank):
    aruco_warped = aruco_homography(img_original)
    rotated_aruco = rotate_aruco(aruco_warped,img_blank)    
    # display_coco_regions(rotated_aruco, '../Sample Images/labels_updated_annotations_2025-04-15-06-40-23.json')
    get_tips_and_compute_score(rotated_aruco)

def run_recent():
    # Database connection parameters
    hostname = 'localhost'
    username = 'dart_thrower'
    password = 'darts'
    database = 'darts'
    
    # Connect to the PostgreSQL server
    try:
        connection = psycopg2.connect(
            host=hostname,
            user=username,
            password=password,
            dbname=database
        )
    
        print("Connection to the database established successfully.")
    
        # Create a cursor object
        cursor = connection.cursor()
        
        # Query to retrieve the image data
        cursor.execute("SELECT image_data FROM images WHERE id = %s", (11,))  # Change the 1 to the ID of your image
        image_data = cursor.fetchone()
    
        if image_data is not None:
            # Print the type of image_data
            print(f"Retrieved data type: {type(image_data[0])}")
    
            # Decode the Base64 string into bytes
            image_bytes = base64.b64decode(image_data[0])
    
            # Create an image from the bytes
            image = Image.open(BytesIO(image_bytes))
            
            # Display the image using matplotlib
            img_original = rotate(image, angle=270, reshape=True)
            # Convert to NumPy array
            img_rgb = np.array(img_original)
            # Convert RGB to BGR to match cv2.imread()
            img_original = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
            plt.imshow(img_original)
            plt.axis('off')  # Hide the axis
            plt.show()
            img_blank = "/home/tars/Projects/Dart-Vision/Sample Images/template_aruco_blank.jpg"
            run_workflow(img_original,img_blank)

        else:
            print("No image found with the specified ID.")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()

run_recent()