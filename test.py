import streamlit as st
import google.generativeai as genai
import os

# Use environment variables to store API key (replace "..." with actual key)
API_KEY = os.environ['Gemini_key']
genai.configure(api_key=API_KEY)

# Initialize the Generative Model with system instructions
system_instruction = """
You are a self-learning Artificial Chatbot, specialized in the waste management field,
especially in recycling and reusing. You are also an expert in waste sorting and management.
You will be either given a photo or picture (can be a real-time picture as well).

a) You must first greet the user with the proper greeting based on the time of day.

b) You must then ask and prompt the user on how you can help them. After that,
   you must use internet resources with proper citations to answer the questions
   prompted by the user.

You are only able to answer the questions within the limit of the steps as follows:

1) You must give recommendations on whether the item is recyclable or not based on the
   picture or the photo uploaded.

2) You must categorize the waste (give suggestions on how to recycle it for electronic
   devices like second-hand sales).

3) You must give suggestions for nearby recycling centres based on the Google Maps API.
   (Only if the user allows permission).

4) You must mention all of the prices in MYR related to the materials (such as plastics, aluminium,
   or metal), found and detected from the picture or photo uploaded.
"""

# Initialize the generative model globally
model = genai.GenerativeModel("gemini-1.5-flash")

# Create a function to upload an image and generate AI responses
# def generate_response(image_file):
#    # Determine the MIME type based on the file extension
#    if image_file.type == "image/jpeg":
#       mime_type = "image/jpeg"
#    elif image_file.type == "image/png":
#       mime_type = "image/png"
#    else:
#       return "Unsupported file type. Please upload a .jpg, .jpeg, or .png image."

#    # Upload the image file using the File API
#    try:
#       uploaded_file = genai.upload_file(image_file, mime_type=mime_type)
#       file_name = uploaded_file.name
#       st.success(f"Uploaded file name: {file_name}")

#       # Generate content based on the uploaded image and system instruction
#       result = model.generate_content(
#           [uploaded_file, "\n\n", system_instruction])

#       return result.text
#    except Exception as e:
#       return f"An error occurred during the upload or generation process: {str(e)}"


def generate_response(image_file):
    # Determine the MIME type based on the file extension
    if image_file.type == "image/jpeg":
        mime_type = "image/jpeg"
    elif image_file.type == "image/png":
        mime_type = "image/png"
    else:
        return "Unsupported file type. Please upload a .jpg, .jpeg, or .png image."

    # Upload the image file using the File API
    try:
        uploaded_file = genai.upload_file(image_file, mime_type=mime_type)
        file_name = uploaded_file.name
        st.success(f"Uploaded file name: {file_name}")

        # Generate content based on the uploaded image and system instruction
        result = model.generate_content(
            [uploaded_file, "\n\n", system_instruction])

        # Debugging output (optional)
        # st.write("Debugging response:", result)

        # Extract the AI's response text
        if hasattr(result, 'candidates') and len(result.candidates) > 0:
            ai_response = result.candidates[0].content.parts[0].text
            return ai_response.strip(
            )  # Clean up any leading/trailing whitespace
        else:
            return "Unexpected response format. Please check the API documentation."

    except Exception as e:
        return f"An error occurred during the upload or generation process: {str(e)}"


# Create the Streamlit app
def main():
    st.title("Waste Management Chatbot")

    # Allow the user to upload an image
    uploaded_file = st.file_uploader("Upload an image of waste material",
                                     type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Generate AI response
        response = generate_response(
            uploaded_file)  # Call the function to get the response

        # Display the response
        if response:
            st.success("Response from AI:")
            st.write(response)


if __name__ == "__main__":
    main()
