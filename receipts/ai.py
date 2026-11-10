import base64
import io
import json
import os

from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image

load_dotenv()

SYSTEM_PROMPT = (
    "You are a receipt parser. Read the receipt photo and reply with a JSON object "
    "with these keys: store_name (string), date (YYYY-MM-DD, or null if no date is "
    "clearly visible in the photo), total_amount (number, the final amount paid), "
    "items (list). Each item has: name (string, as printed on the receipt), price "
    "(number, price of ONE unit), quantity (integer, default 1), category (one of: "
    "food, drinks, hygiene, household, health, clothing, electric, other). "
    "Never guess or invent a value that is not visible on the receipt. "
    "Discount, return and deposit lines use category other. Do not include tax "
    "lines as items. Use a dot as the decimal separator. "
    "Copy store and item names exactly as printed, keeping all Lithuanian "
    "letters (ą, č, ę, ė, į, š, ų, ū, ž) and never replacing them with plain "
    "ASCII letters. "
    "Keep the sign of every amount exactly as printed: a minus sign means a "
    "negative price. Include each discount, return, cancelled line and deposit "
    "voucher once, as an item with its printed sign. Do not include summary "
    "lines that only repeat or add up discounts already listed, such as total "
    "savings or benefit received. Payment methods such as card or cash are not "
    "items. The items multiplied by quantity should add up to total_amount; "
    "recheck the receipt if they do not, but never invent or duplicate lines. "
    "Ignore loyalty points and bonus lines."
)

def extract_receipt(content):
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    img = Image.open(io.BytesIO(content))
    img.thumbnail((2048,2048))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    encoded = base64.b64encode(buffer.getvalue()).decode('utf-8')

    response = client.chat.completions.create(
        model='gpt-4o',
        temperature=0,
        response_format={'type': 'json_object'},
        messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': 'Extract receipt data.'},
                    {
                        'type': 'image_url',
                        'image_url': {
                            'url': f'data:image/jpeg;base64,{encoded}',
                            'detail': 'high',
                        },
                    },
                ],
            },
        ],
    )
    return json.loads(response.choices[0].message.content)