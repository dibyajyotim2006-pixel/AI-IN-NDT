import os
from PIL import Image, ImageDraw, ImageFont

def create_ndt_icon():
    os.makedirs("assets", exist_ok=True)
    icon_path = os.path.join("assets", "ndt_intelligence.ico")
    
    # Base size 256x256
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Outer rounded rectangle background (Navy #0B132B)
    bg_color = (11, 19, 43, 255)
    border_color = (56, 189, 248, 255) # Cyan #38BDF8
    radius = 48
    draw.rounded_rectangle([8, 8, size - 8, size - 8], radius=radius, fill=bg_color, outline=border_color, width=8)
    
    # Inner concrete block / sensor pulse grid motif
    # Horizontal grid lines (ultrasonic waves)
    wave_color = (14, 165, 233, 140)
    for y in [70, 110, 150, 190]:
        draw.line([(40, y), (size - 40, y)], fill=wave_color, width=3)
        
    # Vertical grid lines
    for x in [70, 110, 150, 190]:
        draw.line([(x, 40), (x, size - 40)], fill=wave_color, width=3)
        
    # Central acoustic pulse burst / Diamond sensor target
    center = size // 2
    accent_color = (0, 242, 254, 255) # Vibrant Cyan
    draw.polygon([
        (center, center - 45),
        (center + 45, center),
        (center, center + 45),
        (center - 45, center)
    ], fill=(15, 23, 42, 230), outline=accent_color, width=6)
    
    # Inner core pulse circle
    draw.ellipse([center - 18, center - 18, center + 18, center + 18], fill=accent_color)
    
    # Save as multi-resolution Windows ICO
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (24, 24), (16, 16)]
    img.save(icon_path, format="ICO", sizes=sizes)
    print(f"Icon generated successfully at {icon_path}")

if __name__ == "__main__":
    create_ndt_icon()
