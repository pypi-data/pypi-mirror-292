## About

This module contains a number plate reader, using a YOLO model for number plate extraction and a CNN trained from scratch on an OCR dataset for character recognition.

## How to setup

Assuming you are in the `Number-Plate-Recognition` directory.

1. Create a Python virtual enviroment using `python3 -m venv venv`
2. Install using `pip install NumPlateVision`

## Example run

To detect and read a number plate from an image, here is an example script

![Example notebook](https://raw.githubusercontent.com/elliottcoops/Number-Plate-Recognition/main/docs/test_run.png)

## ML data processing pipeline

The number plate of a car can be obtained by using an object detection model. State of the art currently is YOLO (You Only Look Once) which is a deep CNN. The model used for number plate extraction can be found [here](https://huggingface.co/nickmuchi/yolos-small-finetuned-license-plate-detection) on The Hugging Face.

A number plate can be read by extracting each character from the number plate, passing it into a character recognition CNN model and then stringing together a word.

Each of these stages is explained in more detail below.

### Stage 1 - Plate extraction (YOLO)

The model finds a bounding box of what it thinks is a number plate. With a set confidence level, we can obtain the bounding box predicted by the model, and extract the number plate from the original image.

![Original](https://raw.githubusercontent.com/elliottcoops/Number-Plate-Recognition/main/docs/original.png) 

![Extracted](https://raw.githubusercontent.com/elliottcoops/Number-Plate-Recognition/main/docs/extracted.png)


### Stage 2 - Character segmentation (OpenCV)

One similarity among all number plates is that the letters are black. Therefore, after applying image processing techniques such as edge sharpening using the Laplacian operator and Otsu thresholding, we can create a binary image with the characters as the foreground and everything else as the background.

![Processed](https://raw.githubusercontent.com/elliottcoops/Number-Plate-Recognition/main/docs/processed.png)

### Stage 3 - Character extraction (OpenCV)

To extract a character, we can use the `contours` method from OpenCV, which identifies foreground objects within an image. This method creates a bounding box around each character, allowing us to extract that portion of the image.

![Contours](https://raw.githubusercontent.com/elliottcoops/Number-Plate-Recognition/main/docs/contours.png)

### Stage 4 - Character recognition (CNN from scratch, see below)

Once we have the characters, we can feed each one into the model, obtain the predictions, and concatenate them into a string.

![Prediction](https://raw.githubusercontent.com/elliottcoops/Number-Plate-Recognition/main/docs/prediction.png)

## CNN built from scratch for character recognition (See stage 4 above)

### Training

The neural network is trained on the standard [OCR dataset](https://www.kaggle.com/datasets/preatcher/standard-ocr-dataset) which contains 50k images of characters.

To increase the number of examples, the training data is augmented 5 times per image from a mix of rotation, translation and zooming. This attains a total train set of size 100k.

### Constants

Constants used during training:

- Loss: Categorical crossentropy
- Epochs: 10
- Optimiser: Adam

### Model evaluation

After training, the test set attains an accuracy of 96.7%.

Looking at the loss and accuracy per epoch we see that there are no signs of overfitting:

![eval](https://raw.githubusercontent.com/elliottcoops/Number-Plate-Recognition/main/docs/model_eval.png)

The confusion matrix shows excellent results overall, however classes 0, 4, and 24 had misclassifications with numbers 0, 3, and letter P; adding more training data or augmentation could help improve accuracy.

![cm](https://raw.githubusercontent.com/elliottcoops/Number-Plate-Recognition/main/docs/cm.png)

In addition, looking at a few test examples: 

![example_test](https://raw.githubusercontent.com/elliottcoops/Number-Plate-Recognition/main/docs/character_example.png)
