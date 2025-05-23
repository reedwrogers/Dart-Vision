import os
os.environ['MPLCONFIGDIR'] = '/tmp/matplotlib'

import matplotlib
matplotlib.use('Agg')

from shapely.geometry import Point, Polygon
import json
import psycopg2
from io import BytesIO
import base64
# import matplotlib.pyplot as plt
from psycopg2 import sql
from scipy.ndimage import rotate
import cv2
import numpy as np
import sqlite3
from scipy.ndimage import rotate
import io
import base64
from PIL import Image
import psycopg2
from io import BytesIO
import matplotlib.patches as patches

# Computes a homography that warps a side image of the board to a front-facing image of the board in a 2000x2000 image
def aruco_homography(img):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Define the ArUco dictionary and parameters. We are using the "classic" dictionary
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
    
    # Define the destination rectangle... where we are warping our intial image to
    width = 2000
    height = 2000  
    dst_rect = np.float32([
        [width - 1, height - 1],  # id 7
        [width - 1, 0],           # id 10
        [0, height - 1],          # id 9
        [0,0]                     # id 8
    ])
    
    # Compute transform and warp
    M = cv2.getPerspectiveTransform(src_rect, dst_rect)
    warped = cv2.warpPerspective(img, M, (width, height))
    warped_rgb = cv2.cvtColor(warped, cv2.COLOR_BGR2RGB)

    return warped

# Takes in our template image without darts, and the homography image. Returns a rotated image that minimizes MSE between the two images
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

# Simply resizes images if needed
def resize_images(img1, img2):
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]), interpolation=cv2.INTER_AREA)
    return img1, img2

# Simply rotates the ArUco based on the best rotation found
def rotate_aruco(original, blank):
    img1 = cv2.imread(blank)

    img2 = original
    img1, img2 = resize_images(img1, img2)
    best_angle, best_rotated_img = find_best_rotation(img1, img2, angle_range=(-10, 10), step=.5)

    return best_rotated_img

# def visualize_results(img1, img2, best_rotated_img, best_angle):
#     # Plot the images
#     plt.figure(figsize=(12, 6))
#     plt.subplot(1, 3, 1)
#     plt.title('Image 1')
#     plt.imshow(cv2.cvtColor(img1, cv2.COLOR_BGR2RGB))
#     plt.axis('off')

#     plt.subplot(1, 3, 2)
#     plt.title('Best Rotated Image (Angle: {})'.format(best_angle))
#     plt.imshow(cv2.cvtColor(best_rotated_img, cv2.COLOR_BGR2RGB))
#     plt.axis('off')

#     plt.subplot(1, 3, 3)
#     plt.title('Original Image 2')
#     plt.imshow(cv2.cvtColor(img2, cv2.COLOR_BGR2RGB))
#     plt.axis('off')

#     plt.tight_layout()
#     plt.show()

# Loads images
def load_images(image_path1, image_path2):
    img1 = cv2.imread(image_path1)
    img2 = cv2.imread(image_path2)

    if img1 is None or img2 is None:
        raise ValueError("One of the images could not be loaded.")

    return img1, img2

# Locate the tips and return a score for each dart
def get_tips_and_compute_score(rotated_aruco):
    img = rotated_aruco

    # Convert to HSV color space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Neon yellow dart color range in HSV
    lower_yellow = np.array([25, 120, 120])
    upper_yellow = np.array([35, 255, 255])
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

    # Operations to clean up the mask
    kernel = np.ones((5, 5), np.uint8)
    mask_clean = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_DILATE, kernel)

    # Find contours
    contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    dart_coords = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 150:
            # Draw the contour
            cv2.drawContours(img, [cnt], -1, (0, 255, 0), 2)

            # Compute the bounding box
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 200, 200), 1)

            # Estimate dart tip
            tip_index = cnt[:, :, 0].argmax()
            tip = tuple(cnt[tip_index][0])
            dart_coords.append(tip)
            cv2.circle(img, tip, 8, (255, 0, 0), -1)

    regions = create_annotations()

    # Classify each detected dart tip
    scores = []
    for x, y in dart_coords:
        label = classify_dart_hit(x, y, regions)
        scores.append(label)

    # Store them in our local database 
    try:
        conn = psycopg2.connect(
            host='localhost',
            dbname='darts',
            user='dart_thrower',
            password='darts',
            port='5432'
        )
        cur = conn.cursor()

        # Get the most recent game_id
        cur.execute("SELECT id FROM games ORDER BY created_at DESC LIMIT 1;")
        game_id = cur.fetchone()[0]

        # Get the last player to shoot
        cur.execute("SELECT player FROM scores WHERE game_id = %s ORDER BY id DESC LIMIT 1;", (game_id,))
        row = cur.fetchone()
        last_player = row[0] if row else "2"
        next_player = "1" if last_player == "2" else "2"
        
        # Convert "missed" to 0, handle doubles/triples/bullseyes
        dart_values = []
        for s in scores:
            if s == "missed":
                dart_values.append(0)
            elif "double" in str(s).lower():
                # Extract the number and multiply by 2
                num = int(''.join(filter(str.isdigit, str(s))))
                dart_values.append(num * 2)
            elif "triple" in str(s).lower():
                # Extract the number and multiply by 3
                num = int(''.join(filter(str.isdigit, str(s))))
                dart_values.append(num * 3)
            elif "bullseye" in str(s).lower():
                if "double" in str(s).lower():
                    dart_values.append(50)  # Double bullseye
                else:
                    dart_values.append(25)  # Single bullseye
            else:
                # Regular number
                dart_values.append(int(s) if isinstance(s, str) and s.isdigit() else s)
        
        # Pad or trim scores list to ensure 3 darts
        dart_values += [None, None, None]
        dart_values = dart_values[:3]

        # Insert back into the database
        insert_query = """
            INSERT INTO scores (game_id, player, dart1, dart2, dart3)
            VALUES (%s, %s, %s, %s, %s)
        """
        cur.execute(insert_query, (game_id, next_player, dart_values[0], dart_values[1], dart_values[2]))

        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        print(f"Database error: {e}")
        return json.dumps({
            "status": "error",
            "message": str(e)
        })

    print(json.dumps({
        "status": "success",
        "scores": dart_values
    }))

    return json.dumps({
        "status": "success",
        "scores": dart_values
    })

# Just classify the dart based off of the manual region mapping we have (which we get from create_annotations())
def classify_dart_hit(x, y, regions):
    point = Point(x, y)
    for region in regions:
        poly = Polygon(region["polygon"])
        if poly.contains(point):
            return region["label"]
    return "missed"

# Create regions based off of our manual region mapping
def create_annotations(): 
    with open("/home/tars/Projects/Dart-Vision/Sample Images/labels_updated_annotations_2025-04-15-07-00-25.json", "r") as f:
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

# Rotates the image
def rotate_image(image, angle):
    (h, w) = image.shape[:2]
    
    # Calculate the center of the image
    center = (w // 2, h // 2)
    
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h))
    return rotated

# Calculate Mean Squared Error between two images
def calculate_mse(img1, img2):
    return np.mean((img1.astype(np.float32) - img2.astype(np.float32)) ** 2)

# def display_coco_regions(image, coco_json_path, image_id=1):
#     # Load COCO JSON
#     with open(coco_json_path, 'r') as f:
#         coco = json.load(f)

#     # Get category map (id → name)
#     cat_map = {cat['id']: cat['name'] for cat in coco['categories']}

#     # Get annotations for the specific image
#     annotations = [ann for ann in coco['annotations'] if ann['image_id'] == image_id]

#     fig, ax = plt.subplots(figsize=(10, 10))
#     ax.imshow(image)
#     ax.set_title("COCO Dartboard Regions")

#     for ann in annotations:
#         category_name = cat_map[ann['category_id']]
#         for seg in ann['segmentation']:
#             # Convert flat list to Nx2 array
#             poly = np.array(seg).reshape((-1, 2))
#             patch = patches.Polygon(poly, closed=True, fill=False, edgecolor='cyan', linewidth=2)
#             ax.add_patch(patch)

#             # Skip labeling bullseye and double bullseye
#             if category_name.lower() in ['bullseye', 'double bullseye']:
#                 continue

#             # Label in the center of the polygon
#             centroid = np.mean(poly, axis=0)
#             ax.text(centroid[0], centroid[1], category_name, color='white', fontsize=9,
#                     ha='center', va='center', weight='bold',
#                     bbox=dict(facecolor='black', alpha=0.5, boxstyle='round'))

#     plt.axis('off')
#     plt.show()

# Run the workflow to perform the whole process
def run_workflow(img_original,img_blank):
    aruco_warped = aruco_homography(img_original)
    rotated_aruco = rotate_aruco(aruco_warped,img_blank)    
    # display_coco_regions(rotated_aruco, '../Sample Images/labels_updated_annotations_2025-04-15-06-40-23.json')
    get_tips_and_compute_score(rotated_aruco)

# Essentially run_workflow, but ensures we use the most recently captured image from the database 
def run_recent():
    hostname = 'localhost'
    username = 'dart_thrower'
    password = 'darts'
    database = 'darts'
    
    try:
        connection = psycopg2.connect(
            host=hostname,
            user=username,
            password=password,
            dbname=database
        )
        
        cursor = connection.cursor()
        
        # Query to retrieve the image data
        cursor.execute("SELECT image_data FROM images ORDER BY id DESC LIMIT 1")
        image_data = cursor.fetchone()
    
        if image_data is not None:    
            # Decode the Base64 string into bytes.. Postgres is storing the image as base64
            image_bytes = base64.b64decode(image_data[0])
    
            image = Image.open(BytesIO(image_bytes))

            # Rotate image
            img_original = rotate(image, angle=270, reshape=True)
            
            img_rgb = np.array(img_original)
            
            # Convert RGB to BGR to match cv2.imread()
            img_original = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)

            # Grab the template image for use in the workflow
            img_blank = "/home/tars/Projects/Dart-Vision/Sample Images/template_aruco_blank.jpg"
            
            run_workflow(img_original,img_blank)

        else:
            print("No image found with the specified ID.")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

run_recent()