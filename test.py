
from PIL import Image
from io import BytesIO
from typing import List, BinaryIO, Dict
import numpy as np

def __to_np_array(image: BinaryIO):
    image_ = Image.open(image)
    (im_width, im_height) = image_.size
    return np.array(image_.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)

image = Image.fromarray(__to_np_array('resources/images/cat.jpg'))
image2bytes = BytesIO()
image.save(image2bytes, format="PNG")
image2bytes.seek(0)
image_as_bytes = image2bytes.read()

# Send the HTTP POST request to TorchServe
import requests

req = requests.post("http://127.0.0.1:8080/predictions/object_count", data=image_as_bytes)
if req.status_code == 200: 
    res = req.json()

print(res)