# convert_dataset.py
# FULL DATASET CONVERSION - Convert ALL images to camera-photo style
# Uses ENHANCED effects with medium strength

import cv2
import numpy as np
import random
import os
from pathlib import Path
from datetime import datetime

def add_camera_noise(image, noise_level=0.02):
    """Add realistic camera noise"""
    gaussian = np.random.normal(0, 255 * noise_level, image.shape)
    image = cv2.add(image.astype(float), gaussian)
    image = np.clip(image, 0, 255).astype(np.uint8)
    return image

def add_uneven_lighting(image, strength=0.3):
    """Add STRONG uneven lighting"""
    height, width = image.shape[:2]
    
    x = np.linspace(-1, 1, width)
    y = np.linspace(-1, 1, height)
    X, Y = np.meshgrid(x, y)
    
    light_x = random.uniform(-0.7, 0.7)
    light_y = random.uniform(-0.7, 0.7)
    
    distance = np.sqrt((X - light_x)**2 + (Y - light_y)**2)
    lighting = 1 - (distance / distance.max()) * strength
    lighting = np.clip(lighting, 0.6, 1.4)
    
    if len(image.shape) == 3:
        lighting = np.stack([lighting] * 3, axis=2)
    
    image = (image.astype(float) * lighting).astype(np.uint8)
    return image

def add_motion_blur(image, kernel_size=5, angle=None):
    """Add motion blur"""
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
    """Add paper texture/grain"""
    texture = np.random.normal(1.0, texture_strength, image.shape)
    image = (image.astype(float) * texture).astype(np.uint8)
    image = np.clip(image, 0, 255).astype(np.uint8)
    return image

def add_vignetting(image, strength=0.3):
    """Add vignetting (darkened edges)"""
    height, width = image.shape[:2]
    
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
    """Add lens distortion"""
    height, width = image.shape[:2]
    
    x = np.linspace(-1, 1, width)
    y = np.linspace(-1, 1, height)
    X, Y = np.meshgrid(x, y)
    
    r = np.sqrt(X**2 + Y**2)
    distortion = 1 + strength * r**2
    
    new_X = (X / distortion).astype(np.float32)
    new_Y = (Y / distortion).astype(np.float32)
    
    new_X = (new_X + 1) * width / 2
    new_Y = (new_Y + 1) * height / 2
    
    image = cv2.remap(image, new_X, new_Y, cv2.INTER_LINEAR)
    return image

def add_gloss_reflection(image, strength=0.05):
    """Add gloss reflection"""
    height, width = image.shape[:2]
    
    y_pos = random.randint(0, height // 3)
    x_pos = random.randint(0, width // 3)
    
    y = np.linspace(-1, 1, height)
    x = np.linspace(-1, 1, width)
    X, Y = np.meshgrid(x, y)
    
    reflection = np.exp(-((X - (2*x_pos/width - 1))**2 + (Y - (2*y_pos/height - 1))**2) / (2 * 0.1**2))
    reflection = (reflection / reflection.max()) * 255 * strength
    
    if len(image.shape) == 3:
        reflection = np.stack([reflection] * 3, axis=2)
    
    image = cv2.add(image.astype(float), reflection).astype(np.uint8)
    image = np.clip(image, 0, 255).astype(np.uint8)
    return image

def add_jpg_compression(image, quality=85):
    """Add JPEG compression"""
    _, encoded = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, quality])
    decoded = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    return decoded

def convert_image_enhanced(image_path, output_path, strength='medium'):
    """
    Convert ONE image with enhanced camera effects
    Returns: True if successful, False otherwise
    """
    try:
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            return False
        
        # Apply enhancements based on strength
        if strength == 'medium':
            image = add_camera_noise(image, noise_level=0.025)
            image = add_uneven_lighting(image, strength=0.3)
            image = add_motion_blur(image, kernel_size=4)
            image = add_paper_texture(image, texture_strength=0.06)
            image = add_vignetting(image, strength=0.3)
            image = add_lens_distortion(image, strength=0.015)
            image = add_gloss_reflection(image, strength=0.05)
            image = add_jpg_compression(image, quality=80)
        
        # Create output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save converted image
        cv2.imwrite(output_path, image)
        return True
    
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        return False

def batch_convert_category(input_dir, output_dir, category_name, strength='medium'):
    """
    Convert all images in a category
    
    Args:
        input_dir: Input directory with original images
        output_dir: Output directory for converted images
        category_name: Name for logging (e.g., "Spiral - Parkinson")
        strength: Augmentation strength ('light', 'medium', 'heavy')
    
    Returns:
        (converted_count, failed_count)
    """
    print(f"\n📁 Converting: {category_name}")
    print(f"   From: {input_dir}")
    print(f"   To:   {output_dir}")
    
    input_path = Path(input_dir)
    converted_count = 0
    failed_count = 0
    
    # Find all image files
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(input_path.glob(f'*{ext}'))
        image_files.extend(input_path.glob(f'*{ext.upper()}'))
    
    if not image_files:
        print(f"   ⚠️  No images found!")
        return 0, 0
    
    print(f"   Found: {len(image_files)} images")
    
    for i, input_file in enumerate(image_files):
        # Create output file with same name
        output_file = Path(output_dir) / input_file.name
        
        if convert_image_enhanced(str(input_file), str(output_file), strength):
            converted_count += 1
        else:
            failed_count += 1
        
        # Progress update every 10 images
        if (i + 1) % max(1, len(image_files) // 10) == 0:
            progress = (i + 1) / len(image_files) * 100
            print(f"   Progress: {i + 1}/{len(image_files)} ({progress:.0f}%)")
    
    print(f"   ✓ Converted: {converted_count}")
    if failed_count > 0:
        print(f"   ❌ Failed: {failed_count}")
    
    return converted_count, failed_count

def main():
    """Main conversion function"""
    
    print("=" * 80)
    print("🔄 FULL DATASET CONVERSION - ENHANCED CAMERA EFFECTS")
    print("=" * 80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Define all categories
    categories = [
        {
            'name': 'Spiral - Parkinson',
            'input': r"C:\Users\User\FYP2\data\raw\spiral\parkinson\SpiralPatients",
            'output': r"C:\Users\User\FYP2\data\raw_camera\spiral_camera\parkinson\SpiralPatients"
        },
        {
            'name': 'Spiral - Healthy',
            'input': r"C:\Users\User\FYP2\data\raw\spiral\healthy\SpiralControl",
            'output': r"C:\Users\User\FYP2\data\raw_camera\spiral_camera\healthy\SpiralControl"
        },
        {
            'name': 'Meander - Parkinson',
            'input': r"C:\Users\User\FYP2\data\raw\meander\parkinson\MeanderPatients",
            'output': r"C:\Users\User\FYP2\data\raw_camera\meander_camera\parkinson\MeanderPatients"
        },
        {
            'name': 'Meander - Healthy',
            'input': r"C:\Users\User\FYP2\data\raw\meander\healthy\MeanderControl",
            'output': r"C:\Users\User\FYP2\data\raw_camera\meander_camera\healthy\MeanderControl"
        }
    ]
    
    # Conversion strength
    STRENGTH = 'medium'
    
    # Track overall statistics
    total_converted = 0
    total_failed = 0
    
    # Convert each category
    for category in categories:
        converted, failed = batch_convert_category(
            category['input'],
            category['output'],
            category['name'],
            STRENGTH
        )
        total_converted += converted
        total_failed += failed
    
    # Summary
    print("\n" + "=" * 80)
    print("✅ CONVERSION COMPLETE!")
    print("=" * 80)
    print(f"Total converted: {total_converted}")
    print(f"Total failed:    {total_failed}")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print("📁 Output folder structure:")
    print("   C:/Users/User/FYP2/data/raw_camera/")
    print("   ├── spiral_camera/")
    print("   │   ├── parkinson/SpiralPatients/")
    print("   │   └── healthy/SpiralControl/")
    print("   └── meander_camera/")
    print("       ├── parkinson/MeanderPatients/")
    print("       └── healthy/MeanderControl/")
    
    print("\n📝 Next steps:")
    print("   1. Check the converted images in the output folders")
    print("   2. Update your training notebooks to use the new camera-style dataset")
    print("   3. Retrain spiral_model.pkl with data/raw_camera/spiral_camera/")
    print("   4. Retrain meander_model.pkl with data/raw_camera/meander_camera/")
    print("   5. Deploy the new camera-trained models!")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()