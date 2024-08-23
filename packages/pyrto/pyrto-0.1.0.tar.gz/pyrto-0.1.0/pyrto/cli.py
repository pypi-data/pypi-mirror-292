import argparse
from .pyrto import fetch_vehicle_details, fetch_vehicle_image

def main():
    parser = argparse.ArgumentParser(description="Fetch vehicle details or image based on license plate number")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-lp", "--license_plate", help="Fetch vehicle details for the given license plate")
    group.add_argument("-img", "--image", help="Fetch vehicle image for the given license plate")
    
    args = parser.parse_args()
    
    if args.license_plate:
        details = fetch_vehicle_details(args.license_plate)
        if details:
            for key, value in details.items():
                print(f"{key}: {value}")
        else:
            print("No details found for the given license plate.")
    
    elif args.image:
        image = fetch_vehicle_image(args.image)
        if image:
            image.show()
        else:
            print("No image found for the given license plate.")