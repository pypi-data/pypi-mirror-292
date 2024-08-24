from NumPlateVision.number_plate_reader import NumberPlateReader
from PIL import Image

npr = NumberPlateReader()

extracted_number_plate = npr.get_number_plate(Image.open('tests/test_car.jpeg'))
number_plate_reading = npr.read_number_plate(extracted_number_plate)

print(number_plate_reading)



