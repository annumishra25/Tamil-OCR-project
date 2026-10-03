"""
Modular Preprocessing Filters for Degraded Tamil Palm-Leaf Manuscripts
Stage 4 Filter Bank
"""

import sys
import math
import numpy as np
import cv2

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def to_grayscale(img: np.ndarray) -> np.ndarray:
    """Convert input BGR/RGB or Grayscale image to single-channel Grayscale."""
    if len(img.shape) == 2:
        return img.copy()
    elif img.shape[2] == 4:
        return cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
    else:
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def denoise_bilateral(img: np.ndarray, d: int = 9, sigma_color: float = 75, sigma_space: float = 75) -> np.ndarray:
    """Edge-preserving bilateral filter to smooth fibrous leaf texture while retaining incised stroke boundaries."""
    return cv2.bilateralFilter(img, d, sigma_color, sigma_space)

def denoise_nlm(img: np.ndarray, h: float = 10, template_size: int = 7, search_size: int = 21) -> np.ndarray:
    """Non-Local Means Denoising for degraded textures."""
    gray = to_grayscale(img)
    return cv2.fastNlMeansDenoising(gray, None, h, template_size, search_size)

def enhance_contrast_linear(img: np.ndarray, low_pct: float = 2.0, high_pct: float = 98.0) -> np.ndarray:
    """Percentile-based linear min-max contrast stretching."""
    gray = to_grayscale(img)
    p_low, p_high = np.percentile(gray, (low_pct, high_pct))
    if p_high == p_low:
        return gray
    stretched = np.clip((gray - p_low) * 255.0 / (p_high - p_low), 0, 255).astype(np.uint8)
    return stretched

def enhance_contrast_clahe(img: np.ndarray, clip_limit: float = 2.0, tile_grid_size: tuple = (8, 8)) -> np.ndarray:
    """Contrast Limited Adaptive Histogram Equalization (CLAHE)."""
    gray = to_grayscale(img)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    return clahe.apply(gray)

def correct_illumination(img: np.ndarray, kernel_size: int = 51) -> np.ndarray:
    """
    Rolling background subtraction / division to normalize illumination gradients across long palm leaves.
    Uses large morphological closing to estimate background envelope.
    """
    gray = to_grayscale(img)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    # Morphological closing estimates the ambient background brightness
    background = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
    # Divide original by background to flatten illumination
    normalized = np.clip((gray.astype(np.float32) / (background.astype(np.float32) + 1e-5)) * 255.0, 0, 255).astype(np.uint8)
    return normalized

def threshold_sauvola(img: np.ndarray, window_size: int = 25, k: float = 0.2, R: float = 128.0) -> np.ndarray:
    """
    Sauvola adaptive local binarization designed for historical document manuscripts.
    Threshold T(x, y) = m(x, y) * (1 + k * ((s(x, y) / R) - 1))
    """
    gray = to_grayscale(img).astype(np.float32)
    # Mean filter
    mean = cv2.blur(gray, (window_size, window_size))
    # Mean of squares
    mean_sq = cv2.blur(gray ** 2, (window_size, window_size))
    # Standard deviation
    std = np.sqrt(np.maximum(mean_sq - mean ** 2, 0))
    # Sauvola threshold map
    threshold = mean * (1.0 + k * ((std / R) - 1.0))
    # Binarize (dark text on white background)
    binary = np.where(gray > threshold, 255, 0).astype(np.uint8)
    return binary

def threshold_otsu(img: np.ndarray) -> np.ndarray:
    """Global Otsu binarization."""
    gray = to_grayscale(img)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary

def unsharp_mask(img: np.ndarray, sigma: float = 1.0, strength: float = 1.5) -> np.ndarray:
    """Unsharp masking to accentuate fine incisions without introducing halo noise."""
    gray = to_grayscale(img)
    blurred = cv2.GaussianBlur(gray, (0, 0), sigma)
    sharpened = cv2.addWeighted(gray, 1.0 + strength, blurred, -strength, 0)
    return np.clip(sharpened, 0, 255).astype(np.uint8)

def deskew_image(img: np.ndarray, max_angle: float = 15.0) -> tuple[np.ndarray, float]:
    """
    Detect dominant text line angle and rotate image to restore horizontal baselines.
    Returns (deskewed_image, angle_applied).
    """
    gray = to_grayscale(img)
    h, w = gray.shape

    # Fast angle detection
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    coords = np.column_stack(np.where(bw > 0))
    if len(coords) < 100:
        return img.copy(), 0.0

    rect = cv2.minAreaRect(coords)
    angle = rect[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    # Limit maximum rotation to avoid vertical flipping
    if abs(angle) > max_angle or abs(angle) < 0.1:
        return img.copy(), 0.0

    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    deskewed = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return deskewed, float(angle)

def morphological_cleanup(binary_img: np.ndarray, min_component_area: int = 10) -> np.ndarray:
    """Remove small isolated salt-and-pepper noise speckles from binarized images."""
    gray = to_grayscale(binary_img)
    # Ensure binary format (0 or 255)
    _, bw = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(bw, connectivity=8)
    
    cleaned_bw = np.zeros_like(bw)
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area >= min_component_area:
            cleaned_bw[labels == i] = 255

    # Invert back to black text on white background
    cleaned = cv2.bitwise_not(cleaned_bw)
    return cleaned
