import time
import io
from PIL import Image
import numpy as np

FPR = "c7a1beebb9400375bb187daa33de9659"

def get_time_now() -> str:
    t = time.time()
    ms = str(int((t % 1) * 1000)).zfill(3)[:2]
    return time.strftime("%Y%m%d%H%M%S", time.localtime(t)) + ms

def generate_device_id() -> str:
    return "s1rmi184-mbib-0000-0000-" + get_time_now()

DEFAULT_HEADERS = {
    'Cache-Control': 'max-age=0',
    'Accept': 'application/json, text/plain, */*',
    'Authorization': 'Basic RU1CUkVUQUlMV0VCOlNEMjM0ZGZnMzQlI0BGR0AzNHNmc2RmNDU4NDNm',
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Origin": "https://online.mbbank.com.vn",
    "Referer": "https://online.mbbank.com.vn/pl/login?returnUrl=%2F",
    "Content-Type": "application/json; charset=UTF-8",
    "app": "MB_WEB",
    "elastic-apm-traceparent": "00-55b950e3fcabc785fa6db4d7deb5ef73-8dbd60b04eda2f34-01",
    "Sec-Ch-Ua": '"Not.A/Brand";v="8", "Chromium";v="134", "Google Chrome";v="134"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}

def replace_color(image_data: bytes, target_hex: str, replace_hex: str, tolerance: int = 0) -> bytes:
    target_hex = target_hex.lstrip('#')
    replace_hex = replace_hex.lstrip('#')
    target_rgb = tuple(int(target_hex[i:i+2], 16) for i in (0, 2, 4))
    replace_rgb = tuple(int(replace_hex[i:i+2], 16) for i in (0, 2, 4))
    
    img = Image.open(io.BytesIO(image_data)).convert('RGBA')
    data = np.array(img)
    
    rgb = data[:,:,:3]
    color_diff = np.sqrt(np.sum((rgb - target_rgb)**2, axis=-1))
    
    max_diff = 255 * min(tolerance / 100.0, 1.0)
    mask = color_diff <= max_diff
    
    data[mask, :3] = replace_rgb
    
    out_img = Image.fromarray(data)
    out_bytes = io.BytesIO()
    out_img.save(out_bytes, format='PNG')
    return out_bytes.getvalue()

def cut_border(image_data: bytes, border_width: int = 5) -> bytes:
    img = Image.open(io.BytesIO(image_data))
    w, h = img.size
    if w <= 2*border_width or h <= 2*border_width:
        raise ValueError("Image is too small to cut border")
    cropped = img.crop((border_width, border_width, w - border_width, h - border_width))
    out_bytes = io.BytesIO()
    cropped.save(out_bytes, format='PNG')
    return out_bytes.getvalue()
