"""
Image Quality and Distortion Analysis for Tamil Palm-Leaf Manuscripts
Stage 4 Quality Assessment Engine
"""

import sys
import math
import numpy as np
import cv2
from pathlib import Path
from PIL import Image

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def analyze_image_quality(image_input) -> dict:
    """
    Perform comprehensive quality, distortion, and noise estimation on a manuscript image.
    Returns a dictionary of measurable physical metrics.
    """
    path_obj = None
    if isinstance(image_input, (str, Path)):
        path_obj = Path(image_input)
        if not path_obj.exists():
            raise FileNotFoundError(f"Image not found at {image_input}")
        img_bgr = cv2.imread(str(path_obj))
        if img_bgr is None:
            raise ValueError(f"Could not decode image at {image_input}")
    elif isinstance(image_input, np.ndarray):
        img_bgr = image_input.copy()
    else:
        raise TypeError("image_input must be a file path, Path object, or numpy ndarray")

    h, w = img_bgr.shape[:2]
    c = img_bgr.shape[2] if img_bgr.ndim == 3 else 1
    aspect_ratio = round(w / h, 3)

    # Convert to grayscale for statistical analysis
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # 1. Brightness and Contrast Statistics
    mean_val = float(np.mean(gray))
    std_val = float(np.std(gray))
    min_val = int(np.min(gray))
    max_val = int(np.max(gray))
    dynamic_range = max_val - min_val

    # 2. Blur / Sharpness Estimation (Variance of Laplacian & Tenengrad)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    blur_score = float(laplacian.var())

    # Tenengrad Gradient Energy
    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    tenengrad = float(np.mean(sobel_x**2 + sobel_y**2))

    # 3. Noise Estimation (Median Absolute Deviation on High-Frequency Residuals)
    # Estimate standard deviation of noise via wavelet-like difference
    sigma_noise = float(np.median(np.abs(laplacian - np.median(laplacian))) / 0.6745)

    # 4. Illumination Variation (Surface standard deviation on low-pass blurred background)
    blurred_bg = cv2.GaussianBlur(gray, (51, 51), 0)
    illumination_std = float(np.std(blurred_bg))
    illumination_gradient = float(np.max(blurred_bg) - np.min(blurred_bg))

    # 5. Foreground / Background Separation Metric (Otsu Between-Class Variance)
    otsu_thresh, otsu_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    w0 = np.sum(gray < otsu_thresh) / (w * h)
    w1 = 1.0 - w0
    if w0 > 0 and w1 > 0:
        mu0 = np.mean(gray[gray < otsu_thresh])
        mu1 = np.mean(gray[gray >= otsu_thresh])
        between_class_var = float(w0 * w1 * ((mu0 - mu1) ** 2))
        separable_ratio = float(between_class_var / (std_val ** 2 + 1e-6))
    else:
        between_class_var = 0.0
        separable_ratio = 0.0

    # 6. Edge Density
    edges = cv2.Canny(gray, 50, 150)
    edge_density = float(np.sum(edges > 0) / (w * h))

    # 7. Skew Angle Estimation (Radon / Hough Transform on horizontal text lines)
    estimated_skew = estimate_skew_angle(gray)

    return {
        "filename": path_obj.name if path_obj is not None else "in_memory_image",
        "width": w,
        "height": h,
        "aspect_ratio": aspect_ratio,
        "mean_brightness": round(mean_val, 2),
        "contrast_std": round(std_val, 2),
        "min_intensity": min_val,
        "max_intensity": max_val,
        "dynamic_range": dynamic_range,
        "laplacian_blur_var": round(blur_score, 2),
        "tenengrad_sharpness": round(tenengrad, 2),
        "estimated_noise_sigma": round(sigma_noise, 2),
        "illumination_variance": round(illumination_std, 2),
        "illumination_gradient": round(illumination_gradient, 2),
        "otsu_threshold": int(otsu_thresh),
        "fg_bg_separability": round(separable_ratio, 4),
        "edge_density": round(edge_density, 4),
        "estimated_skew_deg": round(estimated_skew, 2)
    }

def estimate_skew_angle(gray_img: np.ndarray) -> float:
    """
    Estimate dominant text-line skew angle using horizontal line projection and Hough lines.
    Returns angle in degrees (-45.0 to +45.0).
    """
    try:
        # Resize to manageable height for fast orientation search
        h, w = gray_img.shape
        target_h = min(600, h)
        scale = target_h / h
        resized = cv2.resize(gray_img, (int(w * scale), target_h))

        # Otsu inverse binarization
        _, bw = cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Detect lines via Hough
        edges = cv2.Canny(bw, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80, minLineLength=int(50 * scale), maxLineGap=int(10 * scale))

        if lines is None or len(lines) == 0:
            return 0.0

        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if x2 - x1 == 0:
                continue
            angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
            if -45.0 <= angle <= 45.0:
                angles.append(angle)

        if not angles:
            return 0.0

        median_angle = float(np.median(angles))
        return median_angle
    except Exception:
        return 0.0
