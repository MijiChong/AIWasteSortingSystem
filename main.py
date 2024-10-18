import streamlit as st
import google.generativeai as genai
import os
import requests
import openai

# Ensure the API key is fetched correctly
API_KEY = os.getenv("Gemini_key")
if API_KEY is None:
    st.error(
        "API Key is not set. Please configure the 'Gemini_API' environment variable."
    )
else:
    genai.configure(api_key=API_KEY)

openai.api_key = os.getenv("OpenAI_Api_Key")

# System instructions
system_instruction = """
You are a self-learning Artificial Chatbot, specialized in the waste management field,
especially in recycling and reusing. You are also an expert in waste sorting and management.

a) You must first greet the user with the proper greeting based on the time of day.

b) You must then ask and prompt the user on how I can help them. After that,
   you must use internet resources with proper citations to answer the questions
   prompted by the user.

You are only able to answer the questions within the limit of the steps as follows:

1) You must give recommendations on whether the item is recyclable or not based on the
   picture or the photo uploaded.

2) You must categorize the waste (give suggestions on how to recycle it for electronic
   devices like second-hand sales).

3) You must mention all of the prices in MYR related to the materials (such as plastics, aluminium,
   or metal), found and detected from the picture or photo uploaded, based on the current market prices.
"""

text_instruction = """You are an expert in the field of environmental protection and sustainability, especially in recycling and reusing. 

When given a question or a prompt from the user:

1. Provide a **direct answer** to the user's question with specific tips and information. For example:
   - If asked about recycling plastic, explain the recycling process for plastics, including types of plastics that are recyclable and how they can be reused.
   - If asked for general recycling tips, provide actionable tips such as sorting waste, cleaning recyclables, and using local recycling programs.
2. Ensure that responses are concise and informative, using reliable sources when necessary. If the question is unrelated to environmental protection and sustainability, respond with: 'Sorry, your question is out of topic ^_^'. """

# Initialize the generative model globally
model = genai.GenerativeModel("gemini-1.5-flash")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Function to generate a response based on text input
def generate_response_text(user_input):
    try:
        result = model.generate_content([user_input, "\n\n", text_instruction])
        return result.text
    except Exception as e:
        return f"Error in generating response: {str(e)}"


# Function to generate a response based on an uploaded image
def generate_response_image(image_file, mime_type):
    try:
        myfile = genai.upload_file(image_file, mime_type=mime_type)
        result = model.generate_content([myfile, "\n\n", system_instruction])
        return result.text
    except Exception as e:
        return f"Error in processing image: {str(e)}"


# Function to handle button suggestions and add response to chat history
def handle_suggestions():
    st.sidebar.write("## Quick Questions")

    if st.sidebar.button("How do I recycle plastics?"):
        question = "How do I recycle plastics?"
        response = generate_response_text(question)

        # Append user question and assistant's response to chat history
        st.session_state.messages.append({"role": "user", "content": question})
        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })

    if st.sidebar.button("How to dispose of electronic waste?"):
        question = "How to dispose of electronic waste?"
        response = generate_response_text(question)

        # Append user question and assistant's response to chat history
        st.session_state.messages.append({"role": "user", "content": question})
        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })

    if st.sidebar.button("How can I reduce food waste at home?"):
        question = "How can I reduce food waste at home?"
        response = generate_response_text(question)

        # Append user question and assistant's response to chat history
        st.session_state.messages.append({"role": "user", "content": question})
        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })


# Streamlit app
def main():
    st.title("Eco-Assistant ♻️")
    st.write(
        "Ask me about waste management or upload an image of waste material for recommendations!"
    )

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input type selection
    input_type = st.radio("Select input type:", ("Text", "Image"))

    if input_type == "Text":
        # Text input for asking questions
        user_input = st.chat_input("Type your message here...")

        if user_input:
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(user_input)

            # Add user message to chat history
            st.session_state.messages.append({
                "role": "user",
                "content": user_input
            })

            # Generate response from AI based on the user input
            with st.spinner("Processing your question..."):
                response = generate_response_text(user_input)

            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(response)

            # Add assistant response to chat history
            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })

    elif input_type == "Image":
        # File uploader for images
        file = st.file_uploader("Upload an image of waste material",
                                type=["png", "jpg", "jpeg"])

        if file is not None:
            # Display the uploaded image
            st.image(file, caption="Uploaded image", use_column_width=True)

            # Get the MIME type based on the uploaded file extension
            mime_type = file.type

            # Generate response based on the uploaded image
            with st.spinner("Processing the image..."):
                response = generate_response_image(file, mime_type)

            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(response)

            # Add assistant response to chat history
            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })

    else:
        st.info("Please select a type of input.")

    # Sidebar section
    st.sidebar.title("📍 Location Services")

    if "show_sidebar" not in st.session_state:
        st.session_state.show_sidebar = False

    if st.sidebar.button("Toggle Location Information"):
        st.session_state.show_sidebar = not st.session_state.show_sidebar

    if st.session_state.show_sidebar:
        # Manual location input
        use_manual_location = st.sidebar.checkbox("Manually Enter Location",
                                                  value=True)

        if use_manual_location:
            city = st.sidebar.text_input("Enter your city")
            state = st.sidebar.text_input("Enter your state")
            postcode = st.sidebar.text_input("Enter your postcode")

        # Use OpenAI to find nearby recycling centers
        if st.sidebar.button("Find Nearby Recycling Centers"):
            if city and state and postcode:
                location_input = f"Please suggest nearby recycling centers in {city}, {state}, {postcode}."

                try:
                    # Call OpenAI's ChatCompletion with GPT-4 or GPT-3.5-turbo
                    responseRecycle = openai.ChatCompletion.create(
                        model="gpt-4",  # Or use "gpt-3.5-turbo"
                        messages=[{
                            "role":
                            "system",
                            "content":
                            """
                                Provide a concise list of recycling centers near a specified location, including details such as contact, services, and address. The information must be accurately retrieved from web.
                                Format should include:
                                - **Recycling Center Name**
                                - **Contact:** [Phone Number]
                                - **Services:** [Service Type]
                                - **Address:** [Full Address]

                                If no centers are found, mention that clearly.
                            """
                        }, {
                            "role": "user",
                            "content": location_input
                        }],
                        max_tokens=500)

                    # Extract and display the response from the AI
                    recycling_centers = responseRecycle['choices'][0][
                        'message']['content']

                    # Display the nearby recycling centers
                    st.sidebar.write(
                        f"Based on your location in {city}, {state}, {postcode}, here are some local recycling centers you might consider:"
                    )
                    st.sidebar.write(recycling_centers)

                except Exception as e:
                    st.sidebar.error(
                        f"Error fetching recycling centers: {str(e)}")
            else:
                st.sidebar.warning(
                    "Please fill in all fields to find nearby recycling centers."
                )

    # Call the handle_suggestions function to display suggestion buttons and add response to chat history
    handle_suggestions()


if __name__ == "__main__":
    main()