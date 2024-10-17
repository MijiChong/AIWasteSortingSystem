import streamlit as st
import google.generativeai as genai
import os
from datetime import datetime
import openai
import requests
from PIL import Image
import base64
import io

# Use environment variables to store API key
API_KEY = os.environ['Gemini_key']
genai.configure(api_key=API_KEY)
openai.api_key = os.environ['OpenAI_Api_Key']

# Initialize the Generative Model with system instructions
system_instruction = """
You are a self-learning Artificial Chatbot, specialized in the waste management field,
especially in recycling and reusing. You are also an expert in waste sorting and management.
You will be either given a photo or picture (can be a real-time picture as well).

a) You must first greet the user with the proper greeting based on the time of day only once each time reload.

b) You must then ask and prompt the user on how can you help them. After that,
   you must use internet resources with proper citations to answer the questions
   prompted by the user.

You are only able to answer the questions within the limit of the steps as follows:

1) You must give recommendations on whether the item is recyclable or not based on the
   picture or the photo uploaded.

2) You must categorize the waste (give suggestions on how to recycle it for electronic
   devices like second-hand sales).

3) You must mention all of the prices in MYR related to the materials (such as plastics, aluminium,
   or metal), found and detected from the picture or photo uploaded.
"""

system_instruction_2 = """You are a self-learning Artificial Chatbot, specialized in the waste management field, especially in recycling and reusing. You are also an expert in waste sorting and management. 

When given a question or a prompt from the user:

1. **Greet the user** based on the time of day only once each time reload.
2. Provide a **direct answer** to the user's question with specific tips and information. For example:
   - If asked about recycling plastic, explain the recycling process for plastics, including types of plastics that are recyclable and how they can be reused.
   - If asked for general recycling tips, provide actionable tips such as sorting waste, cleaning recyclables, and using local recycling programs.
3. Ensure that responses are concise and informative, using reliable sources when necessary. If the question is unrelated to recycling or waste management, respond with: "Sorry, your question is out of topic ^_^".
"""

# Initialize the generative model globally
model = genai.GenerativeModel("gemini-1.5-flash")

# Custom CSS for scrollable chat and improved UI/UX
st.markdown("""
    <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        # .chat-container {
        #     max-height: 400px;
        #     overflow-y: auto;
        #     padding: 20px;
        #     border-radius: 10px;
        #     # background-color: white;
        # }
        .user-message {
            color: black;
            background-color: #e3f2fd;
            padding: 10px;
            border-radius: 15px;
            margin: 5px 0;
            max-width: 80%;
            margin-left: auto;
        }
        .assistant-message {
            color: black;
            background-color: #fff3e0;
            padding: 10px;
            border-radius: 15px;
            margin: 5px 0;
            max-width: 80%;
        }

        .send-button {
            width: 100%; /* Make the button full width */
            margin-top: 10px; /* Add some space above the button */
        }
    </style>
""",
            unsafe_allow_html=True)


# Greeting based on time of day
def greet_user():
    current_hour = datetime.now().hour
    if current_hour < 12:
        return "Good morning!"
    elif current_hour < 18:
        return "Good afternoon!"
    else:
        return "Good evening!"


if "greeted" not in st.session_state:
    st.session_state.greeted = False

if not st.session_state.greeted:
    st.write(greet_user())
    st.session_state.greeted = True


def generate_response(content, is_image=False):
    try:
        if is_image:
            # Determine the MIME type based on the file extension
            if content.type == "image/jpeg":
                mime_type = "image/jpeg"
            elif content.type == "image/png":
                mime_type = "image/png"
            else:
                return "Unsupported file type. Please upload a .jpg, .jpeg, or .png image."

            uploaded_file = genai.upload_file(content, mime_type=mime_type)
            result = model.generate_content(
                [uploaded_file, "\n\n", system_instruction])
        else:
            result = model.generate_content(
                [content, "\n\n", system_instruction_2])

        if hasattr(result, 'candidates') and len(result.candidates) > 0:
            return result.candidates[0].content.parts[0].text.strip()
        return "Unexpected response format. Please check the API documentation."
    except Exception as e:
        return f"An error occurred during the upload or generation process: {str(e)}"


def main():
    st.title("🌱 Waste Management Chatbot")

    # Clear chat history on reload
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history in a scrollable container
    st.subheader("Chat History")
    with st.container():
        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
        for role, message in st.session_state.chat_history:
            if role == "You":
                st.markdown(f"<div class='user-message'>{message}</div>",
                            unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='assistant-message'>{message}</div>",
                            unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Sidebar for location information and quick actions
    st.sidebar.title("🔧 Quick Actions")
    quick_queries = [
        "What can I recycle?", "How do I sort my waste?",
        "Nearest recycling center"
    ]
    for query in quick_queries:
        if st.sidebar.button(query):
            st.session_state.chat_history.append(("You", query))
            response = generate_response(query, is_image=False)
            st.session_state.chat_history.append(("Assistant", response))

    st.sidebar.title("📍 Location Services")
    if st.sidebar.button("Toggle Location Information"):
        st.session_state.show_sidebar = not st.session_state.get(
            'show_sidebar', False)

    if st.session_state.get('show_sidebar', False):
        # Manual location input
        use_manual_location = st.sidebar.checkbox("Manually Enter Location",
                                                  value=True)

        if use_manual_location:
            city = st.sidebar.text_input("Enter your city")
            state = st.sidebar.text_input("Enter your state")
            postcode = st.sidebar.text_input("Enter your postcode")
        else:
            # Automatically detect user's location using their IP address
            try:
                response = requests.get('https://ipinfo.io/json')
                location_data = response.json()
                city = location_data.get("city", "Unknown City")
                state = location_data.get("region", "Unknown State")
                postcode = location_data.get("postal", "Unknown Postcode")
                st.sidebar.write(f"Detected Location: {city}, {state}, {postcode}")
            except Exception as e:
                st.sidebar.error(f"Error detecting location: {str(e)}")

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
                recycling_centers = responseRecycle['choices'][0]['message'][
                    'content']

                # Display the nearby recycling centers
                st.sidebar.write(
                    f"Based on your location in {city}, {state}, {postcode}, here are some local recycling centers you might consider:"
                )
                st.sidebar.write(recycling_centers)

            except Exception as e:
                st.sidebar.error(f"Error fetching recycling centers: {str(e)}")
        else:
            st.sidebar.warning(
                "Please fill in all fields to find nearby recycling centers.")

    # Input area with text and file uploader
    st.subheader("Enter your query or upload an image:")
    user_input = st.text_input("Type your question here:")
    uploaded_file = st.file_uploader("Or upload an image of waste material",
                                     type=["jpg", "jpeg", "png"])

    # Analyze button to handle input
    if st.button("Send"):
        if uploaded_file:
            st.session_state.chat_history.append(
                ("You (Image)", "Uploaded an image"))
            response = generate_response(uploaded_file, is_image=True)
            st.session_state.chat_history.append(("Assistant", response))
        elif user_input:
            st.session_state.chat_history.append(("You", user_input))
            response = generate_response(user_input, is_image=False)
            st.session_state.chat_history.append(("Assistant", response))
        else:
            st.warning("Please upload an image or enter a question.")

    # Automatically scroll to the latest message
    st.markdown("""
        <script>
        var chatContainer = document.querySelector('.chat-container');
        chatContainer.scrollTop = chatContainer.scrollHeight;
        </script>
    """,
                unsafe_allow_html=True)


if __name__ == "__main__":
    main()
