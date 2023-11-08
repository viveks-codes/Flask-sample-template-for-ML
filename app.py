from flask import Flask, request, jsonify, render_template
from medisearch_client import MediSearchClient
from PIL import Image
import pytesseract
import uuid

# api_key = "API"

conversation_id = str(uuid.uuid4())
client = MediSearchClient(api_key=api_key)

app = Flask(__name__)

def extract_text_from_image(image_path):
    """
    Extract text from an image using pytesseract.

    Args:
        image_path (str): The path to the image file.

    Returns:
        str: The extracted text from the image.
    """
    try:
        # Open the image using Pillow (PIL)
        img = Image.open(image_path)

        # Use pytesseract to extract text from the image
        text = pytesseract.image_to_string(img)

        return text
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return f"An error occurred: {str(e)}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    # Get the uploaded image
    image = request.files['image']

    if image:
        # Save the image temporarily
        image_path = "temp_image.png"
        image.save(image_path)

        # Extract text from the image
        extracted_text = extract_text_from_image(image_path)

        # Send the extracted text as a question to MediSearch
        responses = client.send_user_message(conversation=[extracted_text],
                                             conversation_id=conversation_id,
                                             language="English",
                                             should_stream_response=True)
        output = ""
        for response in responses:
            if response["event"] == "llm_response":
                output = response["text"]
        return render_template('index.html', prediction_text='According to the model, the answer is: {}'.format(output))
    else:
        return render_template('index.html', prediction_text='Please upload an image first')

@app.route('/search', methods=['GET', 'POST'])
def search():
    search_query = request.form.get('search_query')

    if search_query:
        # Send the search query to MediSearch
        responses = client.send_user_message(conversation=[search_query],
                                             conversation_id=conversation_id,
                                             language="English",
                                             should_stream_response=True)
        output = ""
        for response in responses:
            if response["event"] == "llm_response":
                output = response["text"]
        return render_template('index.html', prediction_text='According to the model, the answer is: {}'.format(output))
    else:
        return render_template('index.html', prediction_text='Please enter a search query')


if __name__ == "__main__":
    app.run(debug=True)
