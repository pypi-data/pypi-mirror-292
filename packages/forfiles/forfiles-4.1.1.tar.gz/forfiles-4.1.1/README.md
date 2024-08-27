# forfiles

forfiles has useful tools for files and images.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install forfiles.

```bash
pip install --upgrade forfiles
```

## Usage

```python
from forfiles import file as f, image as i, directory as d

# file tools
f.filter_type("C:/Users/example/Downloads/directory-to-filter/", [".png", ".txt", "md"])
f.dir_create("C:/Users/example/Downloads/directory-to-create/")
f.dir_delete("C:/Users/example/Downloads/directory-to-delete/")

# image tools
i.scale("C:/Users/example/Downloads/boat.png", 1, 1.5)
i.resize("C:/Users/example/Downloads/car.jpg", 1000, 1000)
i.to_png("C:/Users/example/Downloads/plane.jpg")

# you can also operate whole directories
d.dir_action("C:/Users/example/Downloads/cats/", True, image.scale, 2, 2)
d.dir_action("C:/Users/example/Downloads/giraffes/", True, image.resize, 1000, 1000)
d.dir_action("C:/Users/example/Downloads/tortoises/", True, image.to_png)
```
