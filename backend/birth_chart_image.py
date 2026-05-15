from fastapi import APIRouter, Depends
from PIL import Image, ImageDraw, ImageFont
import os
from dotenv import load_dotenv

load_dotenv('/root/secrets/all-keys.env')

router = APIRouter(prefix='/birth-chart', tags=['Visuals'])

def get_image_font():
    font_path = os.getenv('BIRTH_CHART_FONT_PATH', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
    return ImageFont.truetype(font_path, 16)

@router.post('/generate-image')
def generate_birth_chart_image(chart_data: dict, font: ImageFont.FreeTypeFont = Depends(get_image_font)):
    # Create base image (1200x1200 px for shareable social media)
    image = Image.new('RGB', (1200, 1200), color='#1a1a2e')
    draw = ImageDraw.Draw(image)

    # Add chart title
    draw.text((600, 50), 'Your Gab44 Birth Chart', font=font, fill='#e94560', anchor='mm')

    # Add core chart data (simplified for initial implementation)
    y_offset = 150
    for key, value in chart_data.items():
        draw.text((200, y_offset), f'{key}: {value}', font=font, fill='#ffffff')
        y_offset += 40

    # Save image to temporary path (to be converted to base64 for frontend)
    temp_path = '/tmp/birth_chart.png'
    image.save(temp_path)

    return {'image_path': temp_path, 'shareable': True}
