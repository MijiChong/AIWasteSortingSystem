import streamlit as st
import google.generativeai as genai
import os
from datetime import datetime

# Use environment variables to store API key
API_KEY = os.environ['Gemini_key']
genai.configure(api_key=API_KEY)
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
# Custom CSS for scrollable chat and improved UI/UX
st.markdown("""
    <style>
        .stApp {
            max-width: 700px;
            margin: 0 auto;
        }
        .chat-container {
            max-height: 500px;
            overflow-y: auto;
            padding: 20px;
            background-color: #f0f0f5;
            border-radius: 10px;
        }
        .user-message {
            color: black;
            background-color: #cce5ff;
            padding: 10px;
            border-radius: 15px;
            margin: 5px 0;
            text-align: right;
            max-width: 75%;
        }
        .assistant-message {
            color: black;
            background-color: #e0ffe0;
            padding: 10px;
            border-radius: 15px;
            margin: 5px 0;
            text-align: left;
            max-width: 75%;
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


# Image Analysis Function
def analyze_image(image_file):
   try:
      mime_type = image_file.type
      if mime_type not in ["image/jpeg", "image/png"]:
         return "Unsupported file type. Please upload a .jpg, .jpeg, or .png image."

      uploaded_file = genai.upload_file(image_file, mime_type=mime_type)
      result = model.generate_content(
          [uploaded_file, "\n\n", system_instruction])

      if hasattr(result, 'candidates') and len(result.candidates) > 0:
      return result.candidates[0].content.parts[0].text.strip()
      return "Unexpected response format. Please check the API documentation."
      except Exception as e:
      return f"An error occurred during the upload or generation process: {str(e)}"



# Prompt Analysis Function
def analyze_prompt(user_input):
   try:
      result = model.generate_content(
          [user_input, "\n\n", system_instruction_2])
   except Exception as e:
      return f"Error processing prompt: {str(e)}"


# Display Chat History in a Scrollable Container
def display_chat():
   st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
   for role, message in st.session_state.chat_history:
      if role == "You":
         st.markdown(f"<div class='user-message'>{message}</div>",
                     unsafe_allow_html=True)
      else:
         st.markdown(f"<div class='assistant-message'>{message}</div>",
                     unsafe_allow_html=True)
   st.markdown("</div>", unsafe_allow_html=True)


# Main App Logic
def main():
   st.title("♻️ Waste Management Chatbot")

   # Initialize chat history if not present
   if "chat_history" not in st.session_state:
      st.session_state.chat_history = []

   # Display the chat history
   st.subheader("Conversation")
   display_chat()

   # Sidebar with options
   st.sidebar.title("Quick Actions")
   if st.sidebar.button("What can I recycle?"):
      st.session_state.chat_history.append(("You", "What can I recycle?"))
      response = analyze_prompt("What can I recycle?")
      st.session_state.chat_history.append(("Assistant", response))

   # User input area for text and image analysis
   st.subheader("Ask a Question or Upload Waste Image:")
   user_input = st.text_input("Type your question here:")

   uploaded_file = st.file_uploader("Upload an image of waste material",
                                    type=["jpg", "jpeg", "png"])

   # Analyze button to trigger the appropriate function
   if st.button("Analyze"):
      if uploaded_file:
         st.session_state.chat_history.append(
             ("You (Image)", "Uploaded an image"))
         response = analyze_image(uploaded_file)
         st.session_state.chat_history.append(("Assistant", response))
      elif user_input:
         st.session_state.chat_history.append(("You", user_input))
         response = analyze_prompt(user_input)
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
