A Python package to check NSFW content using the FitSnap API.

## Installation

```
pip install fs-nsfw-checker
```

## Usage

```python
from PIL import Image
from fs_nsfw_checker import checkNSFW

garment = Image.open('path_to_garment.png')
model = Image.open('path_to_model.png')
result = Image.open('path_to_result.png')

checkNSFW(garment, model, result, "Description of the image", "Image category")
```

Note: The `checkNSFW` function returns immediately after initiating the check and does not wait for the result.

## License

This project is licensed under the MIT License.
