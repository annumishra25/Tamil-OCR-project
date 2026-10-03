"""
Physics-Inspired Tamil Palm-Leaf Manuscript Degradation Engine
Stage 7 Synthetic Data Engine

Implements modular, reproducible physical degradation operations:
- Fibrous horizontal leaf striations & ochre grain
- Uneven multi-pole illumination gradients
- Fine scratches, stylus incisions & cracks
- Stroke fading, ink erosion & localized thinning
- Speckles, mold spots & insect damage
- Gaussian/motion blur & sensor noise
- Micro-rotations & perspective skew
"""

import math
import numpy as np
import cv2
from PIL import Image
from typing import Dict, Any, Tuple, Optional


def apply_fibrous_background_texture(
    img_np: np.ndarray,
    strength: float = 0.35,
    bg_color: Tuple[int, int, int] = (215, 195, 160),
    rng: Optional[np.random.RandomState] = None
) -> np.ndarray:
    """
    Simulates horizontal dried palm-leaf fiber striations and natural brownish-ochre hue.
    """
    if rng is None:
        rng = np.random.RandomState()

    h, w, c = img_np.shape

    # 1. Base leaf color tint
    base_tint = np.array(bg_color, dtype=np.float32)
    
    # 2. Generate 1D horizontal fiber pattern (stronger along x-axis rows)
    row_frequencies = rng.uniform(0.85, 1.15, size=(h, 1))
    # Add high-frequency noise for individual striations
    striations = rng.normal(0, 8.0 * strength, size=(h, w)).astype(np.float32)
    fiber_map = (row_frequencies * 255.0 + striations) / 255.0
    fiber_map = np.clip(fiber_map, 0.70, 1.30)
    
    # Expand to 3 channels
    fiber_3d = np.repeat(fiber_map[:, :, np.newaxis], 3, axis=2)
    
    # Create background texture
    bg_textured = base_tint * fiber_3d
    bg_textured = np.clip(bg_textured, 0, 255).astype(np.float32)

    # 3. Blend foreground ink strokes with background texture
    # Clean text has dark ink (< 100 intensity) on white background (> 200 intensity)
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    ink_mask = (1.0 - (gray / 255.0))[:, :, np.newaxis]  # 1.0 for dark ink, 0.0 for white bg

    # Dark incised ink color
    ink_color = np.array([38, 30, 24], dtype=np.float32)
    
    # Composite: where ink exists, blend ink with slight texture; where background, use bg_textured
    blended = (1.0 - ink_mask) * bg_textured + ink_mask * (ink_color * fiber_3d * 0.9)
    return np.clip(blended, 0, 255).astype(np.uint8)


def apply_uneven_illumination(
    img_np: np.ndarray,
    strength: float = 0.25,
    rng: Optional[np.random.RandomState] = None
) -> np.ndarray:
    """
    Simulates non-uniform lighting gradients, shadow falloff, and vignetting across the leaf.
    """
    if rng is None:
        rng = np.random.RandomState()

    h, w, c = img_np.shape
    
    # Linear gradient across width (left-to-right or right-to-left)
    grad_type = rng.choice(["linear_x", "linear_y", "radial", "bilateral"])
    
    if grad_type == "linear_x":
        x_start = rng.uniform(1.0 - strength, 1.0 + strength)
        x_end = rng.uniform(1.0 - strength, 1.0 + strength)
        grad_1d = np.linspace(x_start, x_end, w)
        grad_map = np.tile(grad_1d, (h, 1))
    elif grad_type == "radial":
        cx = rng.uniform(0.2 * w, 0.8 * w)
        cy = rng.uniform(0.2 * h, 0.8 * h)
        y, x = np.ogrid[:h, :w]
        dist = np.sqrt(((x - cx) / w)**2 + ((y - cy) / h)**2)
        grad_map = 1.0 - (dist * strength * 1.5)
    else:
        # Default smooth bilinear gradient
        corners = rng.uniform(1.0 - strength, 1.0 + strength, size=(2, 2))
        grad_map = cv2.resize(corners, (w, h), interpolation=cv2.INTER_CUBIC)

    grad_map = np.clip(grad_map, 0.40, 1.60)[:, :, np.newaxis]
    degraded = img_np.astype(np.float32) * grad_map
    return np.clip(degraded, 0, 255).astype(np.uint8)


def apply_stroke_fading_erosion(
    img_np: np.ndarray,
    erosion_iters: int = 1,
    prob: float = 0.5,
    rng: Optional[np.random.RandomState] = None
) -> np.ndarray:
    """
    Simulates stroke ink erosion, flaking, and thinning from ancient stylus incisions.
    """
    if rng is None:
        rng = np.random.RandomState()

    if rng.uniform(0, 1) > prob:
        return img_np

    # Morphological dilation on inverted image (which erodes dark foreground text)
    kernel_size = rng.choice([2, 3])
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    
    # Lighten ink strokes locally
    eroded = cv2.dilate(img_np, kernel, iterations=erosion_iters)
    
    # Random alpha blend between original and eroded
    alpha = rng.uniform(0.4, 0.85)
    result = cv2.addWeighted(img_np, 1 - alpha, eroded, alpha, 0)
    return result


def apply_scratches_and_cracks(
    img_np: np.ndarray,
    count: int = 5,
    length_range: Tuple[int, int] = (30, 150),
    intensity: float = 0.4,
    rng: Optional[np.random.RandomState] = None
) -> np.ndarray:
    """
    Renders realistic longitudinal and diagonal hairline scratches and palm-leaf splits.
    """
    if rng is None:
        rng = np.random.RandomState()

    h, w, c = img_np.shape
    scratch_layer = img_np.copy()

    for _ in range(count):
        x1 = rng.randint(0, w)
        y1 = rng.randint(0, h)
        length = rng.randint(length_range[0], length_range[1])
        angle = rng.uniform(-15.0, 15.0) * (math.pi / 180.0)  # Mostly horizontal along grain

        x2 = int(x1 + length * math.cos(angle))
        y2 = int(y1 + length * math.sin(angle))
        
        thickness = rng.choice([1, 2], p=[0.8, 0.2])
        scratch_color = rng.choice([20, 50, 180]) # Dark ink crack or light fiber scratch
        color = (int(scratch_color), int(scratch_color * 0.9), int(scratch_color * 0.8))
        
        cv2.line(scratch_layer, (x1, y1), (x2, y2), color, thickness=thickness, lineType=cv2.LINE_AA)

    alpha = np.clip(intensity, 0.1, 0.9)
    result = cv2.addWeighted(img_np, 1 - alpha, scratch_layer, alpha, 0)
    return result


def apply_speckles_and_blotches(
    img_np: np.ndarray,
    count: int = 10,
    radius_range: Tuple[int, int] = (1, 3),
    rng: Optional[np.random.RandomState] = None
) -> np.ndarray:
    """
    Renders speckle stains, ink splatter spots, and age blemishes.
    """
    if rng is None:
        rng = np.random.RandomState()

    h, w, c = img_np.shape
    out = img_np.copy()

    for _ in range(count):
        cx = rng.randint(0, w)
        cy = rng.randint(0, h)
        r = rng.randint(radius_range[0], radius_range[1] + 1)
        
        # Dark spot or faded yellowish stain
        spot_color = rng.choice([30, 60, 160])
        color = (int(spot_color), int(spot_color * 0.9), int(spot_color * 0.8))
        
        cv2.circle(out, (cx, cy), r, color, -1, lineType=cv2.LINE_AA)

    return out


def apply_blur_and_noise(
    img_np: np.ndarray,
    gaussian_sigma: float = 0.8,
    noise_std: float = 8.0,
    motion_blur_len: int = 0,
    rng: Optional[np.random.RandomState] = None
) -> np.ndarray:
    """
    Applies camera optical blur, slight motion blur, and sensor Gaussian noise.
    """
    if rng is None:
        rng = np.random.RandomState()

    out = img_np.astype(np.float32)

    # 1. Motion blur if enabled
    if motion_blur_len > 1:
        kernel = np.zeros((motion_blur_len, motion_blur_len))
        kernel[int((motion_blur_len - 1) / 2), :] = np.ones(motion_blur_len)
        kernel = kernel / motion_blur_len
        out = cv2.filter2D(out, -1, kernel)

    # 2. Gaussian blur
    if gaussian_sigma > 0.1:
        ksize = int(math.ceil(gaussian_sigma * 3)) * 2 + 1
        out = cv2.GaussianBlur(out, (ksize, ksize), gaussian_sigma)

    # 3. Additive Gaussian noise
    if noise_std > 0.5:
        noise = rng.normal(0, noise_std, size=out.shape).astype(np.float32)
        out = out + noise

    return np.clip(out, 0, 255).astype(np.uint8)


def apply_geometric_distortions(
    img_np: np.ndarray,
    rotation_deg: float = 0.5,
    shear_factor: float = 0.01,
    rng: Optional[np.random.RandomState] = None
) -> np.ndarray:
    """
    Applies subtle physical page tilt and affine shear.
    """
    h, w = img_np.shape[:2]
    center = (w // 2, h // 2)

    # Rotation matrix
    rot_mat = cv2.getRotationMatrix2D(center, rotation_deg, 1.0)
    
    # Add affine shear to matrix
    rot_mat[0, 1] += shear_factor
    
    # Apply affine transform with edge replication
    transformed = cv2.warpAffine(
        img_np,
        rot_mat,
        (w, h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REPLICATE
    )
    return transformed


def apply_contrast_and_brightness(
    img_np: np.ndarray,
    contrast: float = 0.85,
    brightness: float = 1.0
) -> np.ndarray:
    """
    Adjusts global contrast and mean luminance.
    """
    out = img_np.astype(np.float32)
    # Scale contrast around 128 midpoint
    out = (out - 128.0) * contrast + 128.0
    # Apply brightness factor
    out = out * brightness
    return np.clip(out, 0, 255).astype(np.uint8)


def degrade_palmleaf_image(
    clean_pil_img: Image.Image,
    preset: str = "MEDIUM",
    preset_cfg: Optional[Dict[str, Any]] = None,
    seed: Optional[int] = None
) -> Tuple[Image.Image, Dict[str, Any]]:
    """
    Master degradation pipeline:
    Applies the full physics-inspired degradation sequence deterministically.
    
    Returns:
        (Degraded PIL Image, degradation_parameters_dict)
    """
    rng = np.random.RandomState(seed if seed is not None else 42)
    img_np = np.array(clean_pil_img.convert("RGB"))

    # Preset defaults if config not supplied
    preset = preset.upper()
    
    # 1. Parameter sampling based on preset
    if preset == "LIGHT":
        tex_strength = rng.uniform(0.15, 0.25)
        illum_strength = rng.uniform(0.08, 0.18)
        contrast = rng.uniform(0.85, 1.05)
        brightness = rng.uniform(0.92, 1.08)
        g_sigma = rng.uniform(0.3, 0.7)
        noise_std = rng.uniform(2.0, 5.0)
        scratch_cnt = rng.randint(1, 4)
        speckle_cnt = rng.randint(2, 6)
        rot_deg = rng.uniform(-0.8, 0.8)
        fading = False
    elif preset == "HEAVY":
        tex_strength = rng.uniform(0.40, 0.65)
        illum_strength = rng.uniform(0.30, 0.55)
        contrast = rng.uniform(0.60, 0.85)
        brightness = rng.uniform(0.75, 1.25)
        g_sigma = rng.uniform(0.8, 1.6)
        noise_std = rng.uniform(10.0, 20.0)
        scratch_cnt = rng.randint(6, 15)
        speckle_cnt = rng.randint(12, 30)
        rot_deg = rng.uniform(-2.0, 2.0)
        fading = True
    elif preset == "EXTREME":
        tex_strength = rng.uniform(0.60, 0.85)
        illum_strength = rng.uniform(0.45, 0.75)
        contrast = rng.uniform(0.45, 0.70)
        brightness = rng.uniform(0.65, 1.35)
        g_sigma = rng.uniform(1.2, 2.0)
        noise_std = rng.uniform(16.0, 28.0)
        scratch_cnt = rng.randint(12, 25)
        speckle_cnt = rng.randint(25, 50)
        rot_deg = rng.uniform(-2.8, 2.8)
        fading = True
    else:  # MEDIUM (Default)
        tex_strength = rng.uniform(0.25, 0.45)
        illum_strength = rng.uniform(0.18, 0.35)
        contrast = rng.uniform(0.70, 0.95)
        brightness = rng.uniform(0.85, 1.15)
        g_sigma = rng.uniform(0.5, 1.1)
        noise_std = rng.uniform(5.0, 12.0)
        scratch_cnt = rng.randint(3, 8)
        speckle_cnt = rng.randint(6, 16)
        rot_deg = rng.uniform(-1.4, 1.4)
        fading = (rng.uniform(0, 1) > 0.5)

    params_record = {
        "preset": preset,
        "seed": seed,
        "texture_strength": round(float(tex_strength), 4),
        "illumination_strength": round(float(illum_strength), 4),
        "contrast_factor": round(float(contrast), 4),
        "brightness_factor": round(float(brightness), 4),
        "gaussian_blur_sigma": round(float(g_sigma), 4),
        "noise_std": round(float(noise_std), 4),
        "scratch_count": int(scratch_cnt),
        "speckle_count": int(speckle_cnt),
        "rotation_deg": round(float(rot_deg), 4),
        "stroke_fading_applied": fading
    }

    # 2. Sequential Application of Physics-Based Operators
    # Step A: Fibrous background texture synthesis
    out = apply_fibrous_background_texture(img_np, strength=tex_strength, rng=rng)

    # Step B: Stroke fading / ink flaking
    if fading:
        out = apply_stroke_fading_erosion(out, erosion_iters=1, prob=1.0, rng=rng)

    # Step C: Stylus scratches and hairline cracks
    out = apply_scratches_and_cracks(out, count=scratch_cnt, intensity=tex_strength, rng=rng)

    # Step D: Speckles & blemishes
    out = apply_speckles_and_blotches(out, count=speckle_cnt, rng=rng)

    # Step E: Uneven illumination gradient
    out = apply_uneven_illumination(out, strength=illum_strength, rng=rng)

    # Step F: Optical blur & noise
    out = apply_blur_and_noise(out, gaussian_sigma=g_sigma, noise_std=noise_std, rng=rng)

    # Step G: Geometric rotation and tilt
    out = apply_geometric_distortions(out, rotation_deg=rot_deg, rng=rng)

    # Step H: Contrast and brightness tuning
    out = apply_contrast_and_brightness(out, contrast=contrast, brightness=brightness)

    degraded_pil = Image.fromarray(out)
    return degraded_pil, params_record
