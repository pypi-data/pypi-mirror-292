from fastai.vision.all import load_learner, PILImage

# Load the pre-trained model
model = load_learner('medium_set_model.pkl')

def preprocess_image(image_path):
    """
    Preprocess the image to the format required by the model.
    """
    image = PILImage.create(image_path)
    return image

def is_safe_image(image_path):
    """
    Predict if the image is safe using the pre-trained model.
    """
    image = preprocess_image(image_path)
    prediction, _, probs = model.predict(image)
    return prediction == True if prediction == 'sfw' else False
