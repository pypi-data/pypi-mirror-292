# PyRTO

PyRTO is a Python package that allows you to fetch vehicle details and images based on license plate numbers.

## Installation

You can install the package using pip:

```
pip install pyrto
```

## Usage

You can use PyRTO either as a Python package or via command line.

### As a Python package:

```python
from pyrto import fetch_vehicle_details, fetch_vehicle_image

license_plate = "MH46CE6708"

# Fetch details
details = fetch_vehicle_details(license_plate)
if details:
    print(details)

# Fetch image
image = fetch_vehicle_image(license_plate)
if image:
    image.show()
```

### Via command line:

To fetch vehicle details:
```
pyrto -lp MH46CE6708
```

To fetch and display the vehicle image:
```
pyrto -img MH46CE6708
```

## License

This project is licensed under the MIT License.