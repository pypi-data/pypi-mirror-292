# forfiles

forfiles has useful tools for files and images.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install forfiles.

```bash
pip install --upgrade forfiles
```

## Usage

```python
from forfiles import file, image

# file tools
file.filter_type("C:/Users/example/Downloads/directory-to-filter/", [".png", ".txt", "md"])
file.dir_create("C:/Users/example/Downloads/directory-to-create/")
file.dir_delete("C:/Users/example/Downloads/directory-to-delete/")

# image tools
image.scale("C:/Users/example/Downloads/boat.png", 1, 1.5)
image.resize("C:/Users/example/Downloads/car.jpg", 1000, 1000)
image.to_png("C:/Users/example/Downloads/plane.jpg")

# you can also operate whole directories
dir_action("C:/Users/example/Downloads/cats/", True, image.scale, 2, 2)
dir_action("C:/Users/example/Downloads/giraffes/", True, image.resize, 1000, 1000)
dir_action("C:/Users/example/Downloads/tortoises/", True, image.to_png)
```
