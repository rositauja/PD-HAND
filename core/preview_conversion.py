# preview_conversion_ENHANCED.py
# More camera photo effects
# Makes images look much more like real phone camera captures

import cv2
import numpy as np
import random
import matplotlib.pyplot as plt
from pathlib import Path
import os

def add_camera_noise(image, noise_level=0.02):
    """Add realistic camera noise (shot noise, read noise)"""
    gaussian = np.random.normal(0, 255 * noise_level, image.shape)
    image = cv2.add(image.astype(float), gaussian)
    image = np.clip(image, 0, 255).astype(np.uint8)
    return image

def add_uneven_lighting(image, strength=0.3):
    """Add STRONG uneven lighting like photos taken under lamps or shadows"""
    height, width = image.shape[:2]
    
    x = np.linspace(-1, 1, width)
    y = np.linspace(-1, 1, height)
    X, Y = np.meshgrid(x, y)
    
    light_x = random.uniform(-0.7, 0.7)
    light_y = random.uniform(-0.7, 0.7)
    
    distance = np.sqrt((X - light_x)**2 + (Y - light_y)**2)
    lighting = 1 - (distance / distance.max()) * strength
    lighting = np.clip(lighting, 0.6, 1.4)  # More extreme
    
    if len(image.shape) == 3:
        lighting = np.stack([lighting] * 3, axis=2)
    
    image = (image.astype(float) * lighting).astype(np.uint8)
    return image

def add_motion_blur(image, kernel_size=5, angle=None):
    """Add motion blur like hand tremor or camera shake"""
    if angle is None:
        angle = random.uniform(0, 360)
    
    kernel = cv2.getRotationMatrix2D((kernel_size/2, kernel_size/2), angle, 1.0)
    kernel = cv2.warpAffine(
        np.eye(kernel_size),
        kernel,
        (kernel_size, kernel_size)
    )
    kernel = kernel / kernel.sum()
    
    image = cv2.filter2D(image, -1, kernel)
    return image

def add_paper_texture(image, texture_strength=0.05):
    """Add STRONG paper texture/grain"""
    texture = np.random.normal(1.0, texture_strength, image.shape)
    image = (image.astype(float) * texture).astype(np.uint8)
    image = np.clip(image, 0, 255).astype(np.uint8)
    return image

def add_perspective_distortion(image, strength=0.02):
    """Add perspective distortion like photo taken at an angle"""
    height, width = image.shape[:2]
    
    pts1 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
    
    offset = int(width * strength)
    pts2 = np.float32([
        [random.randint(-offset, offset), random.randint(-offset, offset)],
        [width + random.randint(-offset, offset), random.randint(-offset, offset)],
        [random.randint(-offset, offset), height + random.randint(-offset, offset)],
        [width + random.randint(-offset, offset), height + random.randint(-offset, offset)]
    ])
    
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    image = cv2.warpPerspective(image, matrix, (width, height))
    
    return image

def add_jpg_compression(image, quality=85):
    """Add JPEG compression artifacts"""
    _, encoded = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, quality])
    decoded = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    return decoded

def add_color_shift(image, strength=0.1):
    """Add subtle color shift like white balance issues in phone cameras"""
    image = image.astype(float)
    
    # Random color shift
    if random.random() > 0.5:
        image[:,:,0] += random.uniform(-20, 10)  # Blue shift
    else:
        image[:,:,1] += random.uniform(-10, 15)  # Green shift
    
    image = np.clip(image, 0, 255).astype(np.uint8)
    return image

def add_vignetting(image, strength=0.3):
    """Add vignetting (darkened edges) like phone camera lenses"""
    height, width = image.shape[:2]
    
    # Create vignette mask
    x = np.linspace(-1, 1, width)
    y = np.linspace(-1, 1, height)
    X, Y = np.meshgrid(x, y)
    
    distance = np.sqrt(X**2 + Y**2)
    vignette = 1 - (distance / distance.max()) * strength
    vignette = np.clip(vignette, 0.7, 1.0)
    
    if len(image.shape) == 3:
        vignette = np.stack([vignette] * 3, axis=2)
    
    image = (image.astype(float) * vignette).astype(np.uint8)
    return image

def add_lens_distortion(image, strength=0.01):
    """Add barrel/pincushion distortion like phone camera lenses"""
    height, width = image.shape[:2]
    
    # Create distortion map
    x = np.linspace(-1, 1, width)
    y = np.linspace(-1, 1, height)
    X, Y = np.meshgrid(x, y)
    
    r = np.sqrt(X**2 + Y**2)
    distortion = 1 + strength * r**2
    
    new_X = (X / distortion).astype(np.float32)
    new_Y = (Y / distortion).astype(np.float32)
    
    # Normalize to image coordinates
    new_X = (new_X + 1) * width / 2
    new_Y = (new_Y + 1) * height / 2
    
    image = cv2.remap(image, new_X, new_Y, cv2.INTER_LINEAR)
    return image

def add_focus_blur(image, strength=0.02):
    """Add subtle focus blur like shallow depth of field"""
    kernel_size = max(3, int(5 * strength))
    if kernel_size % 2 == 0:
        kernel_size += 1
    image = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
    return image

def add_gloss_reflection(image, strength=0.05):
    """Add subtle gloss/reflection like light hitting paper"""
    height, width = image.shape[:2]
    
    # Add a subtle bright spot
    y_pos = random.randint(0, height // 3)
    x_pos = random.randint(0, width // 3)
    
    y = np.linspace(-1, 1, height)
    x = np.linspace(-1, 1, width)
    X, Y = np.meshgrid(x, y)
    
    # Gaussian blob for reflection
    reflection = np.exp(-((X - (2*x_pos/width - 1))**2 + (Y - (2*y_pos/height - 1))**2) / (2 * 0.1**2))
    reflection = (reflection / reflection.max()) * 255 * strength
    
    if len(image.shape) == 3:
        reflection = np.stack([reflection] * 3, axis=2)
    
    image = cv2.add(image.astype(float), reflection).astype(np.uint8)
    image = np.clip(image, 0, 255).astype(np.uint8)
    return image

def convert_with_steps_enhanced(image_path, augmentation_strength='medium'):
    """
    Convert image with ENHANCED camera effects
    
    Returns: original, step1, step2, step3, step4, step5, step6, step7, final
    """
    print(f"Loading image: {image_path}")
    original = cv2.imread(image_path)
    
    if original is None:
        print(f"❌ ERROR: Could not read image!")
        return None
    
    print(f"✓ Image loaded: {original.shape}")
    
    image = original.copy()
    
    print(f"\nApplying ENHANCED augmentations ({augmentation_strength}):")
    
    # Step 1: Add noise
    print("1️⃣ Adding camera noise...")
    if augmentation_strength == 'light':
        image_step1 = add_camera_noise(image, noise_level=0.01)
    elif augmentation_strength == 'medium':
        image_step1 = add_camera_noise(image, noise_level=0.025) 
    else: 
        image_step1 = add_camera_noise(image, noise_level=0.04)  
    
    # Step 2: Add uneven lighting
    print("2️⃣ Adding STRONG uneven lighting...")
    if augmentation_strength == 'light':
        image_step2 = add_uneven_lighting(image_step1, strength=0.15)
    elif augmentation_strength == 'medium':
        image_step2 = add_uneven_lighting(image_step1, strength=0.3)  
    else:  
        image_step2 = add_uneven_lighting(image_step1, strength=0.45)
    
    # Step 3: Add motion blur
    print("3️⃣ Adding motion blur...")
    if augmentation_strength == 'light':
        image_step3 = add_motion_blur(image_step2, kernel_size=3)
    elif augmentation_strength == 'medium':
        image_step3 = add_motion_blur(image_step2, kernel_size=4)  
    else:  
        image_step3 = add_motion_blur(image_step2, kernel_size=6)  
    
    # Step 4: Add paper texture
    print("4️⃣ Adding STRONG paper texture...")
    if augmentation_strength == 'light':
        image_step4 = add_paper_texture(image_step3, texture_strength=0.03)
    elif augmentation_strength == 'medium':
        image_step4 = add_paper_texture(image_step3, texture_strength=0.06)  
    else:  
        image_step4 = add_paper_texture(image_step3, texture_strength=0.10)  
    
    # Step 5: Add vignetting 
    print("5️⃣ Adding vignetting effect...")
    if augmentation_strength == 'light':
        image_step5 = add_vignetting(image_step4, strength=0.15)
    elif augmentation_strength == 'medium':
        image_step5 = add_vignetting(image_step4, strength=0.3)  
    else:  
        image_step5 = add_vignetting(image_step4, strength=0.4)  
    
    # Step 6: Add lens distortion 
    print("6️⃣ Adding lens distortion...")
    if augmentation_strength == 'light':
        image_step6 = add_lens_distortion(image_step5, strength=0.005)
    elif augmentation_strength == 'medium':
        image_step6 = add_lens_distortion(image_step5, strength=0.015)  
    else:  
        image_step6 = add_lens_distortion(image_step5, strength=0.025)  
    
    # Step 7: Add gloss reflection 
    print("7️⃣ Adding gloss reflection...")
    if augmentation_strength == 'light':
        image_step7 = add_gloss_reflection(image_step6, strength=0.02)
    elif augmentation_strength == 'medium':
        image_step7 = add_gloss_reflection(image_step6, strength=0.05) 
    else:  
        image_step7 = add_gloss_reflection(image_step6, strength=0.08) 
    
    # Step 8: JPEG compression
    print("8️⃣ Adding JPEG compression...")
    if augmentation_strength == 'light':
        image_final = add_jpg_compression(image_step7, quality=90)
    elif augmentation_strength == 'medium':
        image_final = add_jpg_compression(image_step7, quality=80)  
    else:  
        image_final = add_jpg_compression(image_step7, quality=70)  
    
    print(f"\n✓ Conversion complete!")
    
    return original, image_step1, image_step2, image_step3, image_step4, image_step5, image_step6, image_step7, image_final

def show_comparison_enhanced(original, step1, step2, step3, step4, step5, step6, step7, final, output_path=None):
    """Display before/after comparison with more steps"""
    fig, axes = plt.subplots(3, 3, figsize=(18, 12))
    fig.suptitle('ENHANCED Image Conversion Preview: Dataset → Realistic Camera Photo Style', fontsize=16, fontweight='bold')
    
    # Convert BGR to RGB for display
    original_rgb = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
    step1_rgb = cv2.cvtColor(step1, cv2.COLOR_BGR2RGB)
    step2_rgb = cv2.cvtColor(step2, cv2.COLOR_BGR2RGB)
    step3_rgb = cv2.cvtColor(step3, cv2.COLOR_BGR2RGB)
    step4_rgb = cv2.cvtColor(step4, cv2.COLOR_BGR2RGB)
    step5_rgb = cv2.cvtColor(step5, cv2.COLOR_BGR2RGB)
    step6_rgb = cv2.cvtColor(step6, cv2.COLOR_BGR2RGB)
    step7_rgb = cv2.cvtColor(step7, cv2.COLOR_BGR2RGB)
    final_rgb = cv2.cvtColor(final, cv2.COLOR_BGR2RGB)
    
    # Row 1
    axes[0, 0].imshow(original_rgb)
    axes[0, 0].set_title('Original (Dataset)', fontweight='bold')
    axes[0, 0].axis('off')
    
    axes[0, 1].imshow(step1_rgb)
    axes[0, 1].set_title('+ Camera Noise', fontweight='bold')
    axes[0, 1].axis('off')
    
    axes[0, 2].imshow(step2_rgb)
    axes[0, 2].set_title('+ Uneven Lighting', fontweight='bold')
    axes[0, 2].axis('off')
    
    # Row 2
    axes[1, 0].imshow(step3_rgb)
    axes[1, 0].set_title('+ Motion Blur', fontweight='bold')
    axes[1, 0].axis('off')
    
    axes[1, 1].imshow(step4_rgb)
    axes[1, 1].set_title('+ Paper Texture', fontweight='bold')
    axes[1, 1].axis('off')
    
    axes[1, 2].imshow(step5_rgb)
    axes[1, 2].set_title('+ Vignetting', fontweight='bold')
    axes[1, 2].axis('off')
    
    # Row 3
    axes[2, 0].imshow(step6_rgb)
    axes[2, 0].set_title('+ Lens Distortion', fontweight='bold')
    axes[2, 0].axis('off')
    
    axes[2, 1].imshow(step7_rgb)
    axes[2, 1].set_title('+ Gloss Reflection', fontweight='bold')
    axes[2, 1].axis('off')
    
    axes[2, 2].imshow(final_rgb)
    axes[2, 2].set_title('Final (Camera-like)', fontweight='bold')
    axes[2, 2].axis('off')
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"\n📊 Comparison saved to: {output_path}")
    
    plt.show()

def save_converted_image(image, output_path):
    """Save the converted image"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, image)
    print(f"💾 Converted image saved to: {output_path}")

if __name__ == "__main__":
    
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    DATA_DIR = PROJECT_ROOT / "dataset"

    INPUT_IMAGE = DATA_DIR / "raw" / "spiral" / "healthy" / "SpiralControl" / "0068-4.jpg"

    PREVIEW_OUTPUT_DIR = PROJECT_ROOT / "preview_output"
    PREVIEW_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    OUTPUT_IMAGE = PREVIEW_OUTPUT_DIR / "pd_spiral_enhanced.png"
    OUTPUT_PLOT = PREVIEW_OUTPUT_DIR / "pd_spiral_enhanced_comparison.png"

    # Choose augmentation strength: 'light', 'medium', 'heavy'
    STRENGTH = 'medium'

    print(f"✓ Preview output folder ready: {PREVIEW_OUTPUT_DIR}\n")
    
    print("=" * 70)
    print("ENHANCED PREVIEW: Single Image Conversion (9 STEPS!)")
    print("=" * 70)
    print(f"Input: {INPUT_IMAGE}")
    print(f"Strength: {STRENGTH}")
    print()
    
    # Convert with enhanced step-by-step progression
    results = convert_with_steps_enhanced(INPUT_IMAGE, STRENGTH)
    
    if results:
        original, step1, step2, step3, step4, step5, step6, step7, final = results
        
        # Show comparison visualization
        show_comparison_enhanced(original, step1, step2, step3, step4, step5, step6, step7, final, OUTPUT_PLOT)
        
        # Save the converted image
        save_converted_image(final, OUTPUT_IMAGE)
        
        print("\n" + "=" * 70)
        print("✅ ENHANCED PREVIEW COMPLETE!")
        print("=" * 70)
        print("\nNew effects added:")
        print("  ✨ Vignetting (darkened edges)")
        print("  ✨ Lens distortion (barrel distortion)")
        print("  ✨ Gloss reflection (light reflections)")
        print("\nIf you like the result, update the full conversion script with these effects!")
    else:
        print("❌ Preview failed - check your image path!")