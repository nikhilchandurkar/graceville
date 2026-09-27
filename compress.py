import os
from PIL import Image

media_dir = r'E:\New folder\app\media'

for root, dirs, files in os.walk(media_dir):
    for file in files:
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            filepath = os.path.join(root, file)
            try:
                img = Image.open(filepath)
                # Resize if width is larger than 1920
                if img.width > 1920:
                    ratio = 1920.0 / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((1920, new_height), Image.Resampling.LANCZOS)
                
                # Convert to RGB to save as optimized JPEG
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                img.save(filepath, 'JPEG', quality=75, optimize=True)
                print(f"Compressed {file}")
            except Exception as e:
                print(f"Failed to compress {file}: {e}")
