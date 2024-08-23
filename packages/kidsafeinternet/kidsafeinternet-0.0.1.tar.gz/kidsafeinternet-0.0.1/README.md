# library
 Kid Safe Internet Python Library.

## Installation
```bash
pip install kidsafeinternet
```

## Usage
```python
from kidsafeinternet import is_safe_image

image_path = 'path_to_image.jpg'
if is_safe_image(image_path):
    print("The image is safe.")
else:
    print("The image is not safe.")
```
