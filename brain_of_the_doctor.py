#Step1: Setup GROQ API key
# brain_of_the_doctor.py

import base64
from groq import Groq

#  Step 1: Add your Groq API key directly here
GROQ_API_KEY = "My API_KEY" # Replace with your actual API key


#  Step 2: Convert image to required format
def encode_image(image_path):
    """Encodes an image file to Base64 format."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

#  Step 3: Setup the Groq client and analyze image
def analyze_image_with_query(query, model, encoded_image):
    """Sends the image and query to the Groq model for analysis."""
    client = Groq(api_key=GROQ_API_KEY)

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": query},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}
                },
            ],
        }
    ]

    chat_completion = client.chat.completions.create(
        messages=messages,
        model=model
    )

    return chat_completion.choices[0].message.content

#  Step 4: Main execution
if __name__ == "__main__":
    image_path = "acne.jpg"  # Make sure this image is in the same folder
    query = "Is there something wrong with my face?"
    model = "meta-llama/llama-4-scout-17b-16e-instruct"

    print("Encoding image...")
    encoded_image = encode_image(image_path)

    print("Analyzing image, please wait...\n")
    response = analyze_image_with_query(query, model, encoded_image)

    print("Response from Groq model:\n")
    print(response)

