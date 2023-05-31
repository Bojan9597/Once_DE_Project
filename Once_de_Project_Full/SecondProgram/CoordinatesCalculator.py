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
        x = float(parts[0].split(':')[1].strip())
        y = float(parts[1].split(':')[1].strip())
        return x, y

    def calculate_corresponding_coordinate(self, x, y):
        src_points = np.array(self.coordinates1, dtype=np.float32)
        dst_points = np.array(self.coordinates2, dtype=np.float32)

        # Check if there are enough coordinates for the transformation
        if len(src_points) < 4 or len(dst_points) < 4:
            raise ValueError("Insufficient coordinates for the transformation.")

        # Normalize the coordinates to the range [-1, 1]
        src_points_norm = src_points / np.max(np.abs(src_points))
        dst_points_norm = dst_points / np.max(np.abs(dst_points))

        # Calculate the perspective transformation matrix
        transformation_matrix, _ = cv2.findHomography(src_points_norm, dst_points_norm)

        # Check if the transformation matrix is valid
        if transformation_matrix is None or transformation_matrix.shape != (3, 3):
            raise ValueError("Invalid transformation matrix.")

        # Convert the input coordinates to homogeneous coordinates
        homogeneous_coords = np.array([[x, y, 1]], dtype=np.float32)

        # Apply the perspective transformation to the input coordinates
        transformed_coords = np.dot(transformation_matrix, homogeneous_coords.T)

        # Convert back to Cartesian coordinates
        corresponding_x = transformed_coords[0, 0] / transformed_coords[2, 0]
        corresponding_y = transformed_coords[1, 0] / transformed_coords[2, 0]

        # Clip the coordinates to the range [-1, 1]
        corresponding_x = np.clip(corresponding_x, -1, 1)
        corresponding_y = np.clip(corresponding_y, -1, 1)

        return corresponding_x, corresponding_y


# Usage example:
calculator = CoordinatesCalculator('CoordinatesPTZ.txt', 'CoordinatesWA.txt')
ptz_x, ptz_y = 1481, 403
wa_x, wa_y = calculator.calculate_corresponding_coordinate(ptz_x, ptz_y)
print("Corresponding Coordinates:")
print(f"X: {wa_x}, Y: {wa_y}")
