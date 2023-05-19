import cv2
import numpy as np

class CoordinatesCalculator:
    def __init__(self, file1, file2):
        self.coordinates1 = self.read_coordinates(file1)
        self.coordinates2 = self.read_coordinates(file2)

    def read_coordinates(self, file):
        coordinates = []
        with open(file, 'r') as f:
            for line in f:
                x, y = self.extract_coordinates(line)
                coordinates.append((x, y))
        return coordinates

    def extract_coordinates(self, line):
        parts = line.split(',')
        x = int(parts[0].split(':')[1].strip())
        y = int(parts[1].split(':')[1].strip())
        return x, y

    def calculate_corresponding_coordinate(self, x, y):
        src_points = np.array(self.coordinates1, dtype=np.float32)
        dst_points = np.array(self.coordinates2, dtype=np.float32)

        # Check if there are enough coordinates for the transformation
        if len(src_points) < 4 or len(dst_points) < 4:
            raise ValueError("Insufficient coordinates for the transformation.")

        # Calculate the perspective transformation matrix
        transformation_matrix, _ = cv2.findHomography(src_points, dst_points)

        # Check if the transformation matrix is valid
        if transformation_matrix is None or transformation_matrix.shape != (3, 3):
            raise ValueError("Invalid transformation matrix.")
        
        # Convert the input coordinates to homogeneous coordinates
        homogeneous_coords = np.array([[x, y]], dtype=np.float32)

        # Reshape the input coordinates for compatibility with perspectiveTransform
        homogeneous_coords = homogeneous_coords.reshape(1, 1, 2)

        # Apply the perspective transformation to the input coordinates
        transformed_coords = cv2.perspectiveTransform(homogeneous_coords, transformation_matrix)

        # Extract the corresponding coordinates from the transformed result
        corresponding_x, corresponding_y = transformed_coords[0, 0]

        return corresponding_x, corresponding_y
    
# Usage example:
calculator = CoordinatesCalculator('CoordinatesPTZ.txt', 'CoordinatesWA.txt')
ptz_x, ptz_y = 92, 127
wa_x, wa_y = calculator.calculate_corresponding_coordinate(ptz_x, ptz_y)
print("Corresponding Coordinates:")
print(f"X: {wa_x}, Y: {wa_y}")
