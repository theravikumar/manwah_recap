import cv2
import numpy as np
from PIL import Image

class TextBubbleDetector:
    """Detects speech bubbles, dialogue boxes, and text regions in comic/manhwa images."""
    def __init__(self, padding: int = 8, min_area: int = 400):
        self.padding = padding
        self.min_area = min_area

    def detect_bubbles(self, img_np: np.ndarray) -> np.ndarray:
        """
        Takes an RGB image numpy array and returns a binary mask (255 where text/bubble is present, 0 elsewhere).
        """
        h, w, _ = img_np.shape
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)

        # Mask 1: Detect bright white/off-white speech bubble regions
        _, white_thresh = cv2.threshold(gray, 235, 255, cv2.THRESH_BINARY)

        # Mask 2: Detect dark text inside bright areas
        # Edges / high gradients
        grad = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))
        _, text_edges = cv2.threshold(grad, 40, 255, cv2.THRESH_BINARY)

        # Find contours of white regions (speech bubbles)
        contours, _ = cv2.findContours(white_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        mask = np.zeros((h, w), dtype=np.uint8)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < self.min_area:
                continue

            x, y, bw, bh = cv2.boundingRect(cnt)
            # Filter out extreme edge margins or entire background
            if bw > 0.95 * w and bh > 0.95 * h:
                continue

            # Check if there is internal edge activity (text) inside this white box
            roi_text = text_edges[y:y+bh, x:x+bw]
            edge_density = np.sum(roi_text > 0) / (bw * bh + 1e-5)

            # If it's a bubble containing text elements
            if edge_density > 0.02 and bw < 0.9 * w and bh < 0.8 * h:
                # Draw filled contour with padding
                cv2.drawContours(mask, [cnt], -1, 255, thickness=cv2.FILLED)
                # Expand bounding rect slightly to cover tails/outlines
                x1 = max(0, x - self.padding)
                y1 = max(0, y - self.padding)
                x2 = min(w, x + bw + self.padding)
                y2 = min(h, y + bh + self.padding)
                mask[y1:y2, x1:x2] = 255

        # Dilation to smooth mask boundaries
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        mask = cv2.dilate(mask, kernel, iterations=2)

        return mask
