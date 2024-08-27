import base64
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt

# Base64 string
base64_string = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABmJLR0QA/wD/AP+gvaeTAAABc0lEQVRIie3Vv0pcQRTH8Y9GxFbMkpAiikIgTbA0igRTxBfQWMTC0ioQ8AHs8xIptJEUopJSsLBK4R9IoYUmlUUaxUJiNDfFnMtuLnvXja6F4A+Gc4Z7Zr7DnHPucEf0A/2t3nQYneFnOEDfVYvWIzgfZxgviV3CckAyvMchntQGtRcWjRTmXXhdApiuAcEYtvGzEeA07EPMht9TAjjH25p5G6bwuxHge9hn2Ar/eQmgKRUB38IO4Sj8QTyos7ZT9XpIeVhSTXxdwEbYCayFv1dyuIWw+TVt4IV0vaV6LN1hXkW7qJTE1ivT3kab51qNBfsNNi/qUBM9kOtVAE4UarqV+hKQxdsCDEg9kXforWg6ABeYLInpQPdNIPMBucRc4VtF+jX8wQ4+4SPeXBeS4bOU+IpUwlmdcfa/AHinmpNjqYSzOPlTvIyYHHIt9UvdXXvaTXwIQM9NAblGseLfji+OlugRZqTkfpXegV/So3Wv5vUX01JgGDZ1jS0AAAAASUVORK5CYII="

# Decode the base64 string
image_data = base64.b64decode(base64_string)

# Create an image from the decoded data
image = Image.open(BytesIO(image_data))

# Display the image
plt.imshow(image)
plt.axis('off') # Hide the axis
plt.show()
