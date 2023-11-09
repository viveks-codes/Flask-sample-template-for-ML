# Import necessary libraries
from flask import Flask, request, render_template, jsonify
from medisearch_client import MediSearchClient
from PIL import Image
import pytesseract
import uuid

# Your API key
api_key = "0ab6f32c-90cb-4422-be35-70955adeb426"

app = Flask(__name__)

# Initialize the MediSearch client
conversation_id = str(uuid.uuid4())
client = MediSearchClient(api_key=api_key)
conversation_ids = {}
user_id = 5

# Function to extract text from an image
def extract_text_from_image(image_path):
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return f"An error occurred: {str(e)}"

# Route to render the home page
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/chat')
def chat():
    return render_template('chat.html')

# Route to handle image upload and prediction
@app.route('/predict', methods=['POST'])
def predict():
    if 'image' in request.files:
        # Get the uploaded image
        image = request.files['image']
        
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
        return render_template('index.html', prediction_text=output)
    else:
        return render_template('index.html', prediction_text="Please upload an image")

# Route to handle medicine search
@app.route('/search', methods=['POST'])
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
        return render_template('index.html', prediction_text=output)
    else:
        return render_template('index.html', prediction_text="Please enter a search query")


# Route to handle chatbot interactions
@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_message = request.json.get('user_message')
    conversation_id = conversation_ids.get(user_id, str(uuid.uuid4()))
    bot_response = ""
    responses = client.send_user_message(conversation=[user_message],
                                         conversation_id=conversation_id,
                                         language="English",
                                         should_stream_response=True)
    for response in responses:
        if response["event"] == "llm_response":
            bot_response = response["text"]
    conversation_ids[user_id] = conversation_id
    return jsonify({"bot_response": bot_response})

if __name__ == "__main__":
    app.run(debug=True)
