import streamlit as st
import io
import chardet
import hashlib
from datetime import datetime
from langdetect import detect, DetectorFactory
from google_gemini import google_gemini_translate
from googletrans import Translator

# Ensure consistency in language detection
DetectorFactory.seed = 0

st.set_page_config(
    page_title="AI Translator",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖  AI Translator")

# Use CSS to position the small subtitle text
st.markdown("""
            
    <style>
    .subtitle {
        position: absolute;
        top: -.65rem; 
        left: 4.55rem; 
        font-size: 1rem;
        color: gray;
    }
    </style>
            
    """, unsafe_allow_html=True)

# Create navigation tabs
tab1, tab2, tab3 = st.tabs(["📑 Documents", "🔤 Text", "🤖 ChatBot"])

# Tab 1: Document translation
with tab1:
    col1, col2 = st.columns(2)

    # Select output language
    with col1:
        output_languages_list = [
            'English',
            'Hindi',
            'Kannada',
            'Malayalam',
            'Tamil',
            'Telugu'
        ]

        output_language_tab1 = st.selectbox(label="Output language", options=output_languages_list, key="output_language_tab1")

    # File uploader
    with col2:
        uploaded_file = st.file_uploader("Supported file types: .txt", type="txt")

    # Add HTML and CSS to change the content
    st.markdown(
        """
        <style>
            .e1b2p2ww11 .e1bju1570::before {
                content: "Please note: We only accept text up to 1000 characters long: .txt";
                font-size: 12px;
                color: white;
                font-family: 'Source Sans Pro', sans-serif;
                letter-spacing: 1px;
            }

            .e1b2p2ww11 .e1bju1570 {
                font-size: 0;
            }
        </style>
        """, unsafe_allow_html=True
    )

    if uploaded_file:
        if st.button("Translate",  key="translate_button_tab1"):
            if uploaded_file.name.endswith('.txt'):
                # Read file as binary
                file_bytes = uploaded_file.read()
                
                # Detect file encoding
                result = chardet.detect(file_bytes)
                encoding = result['encoding']
                
                # Decode file content using detected encoding
                file_contents = file_bytes.decode(encoding)

                # Limit the number of characters
                if len(file_contents) > 1000:
                    st.warning("Limit is 1000 characters.")
                    st.stop()  # Stop the program
                else:        
                    source_language = detect(file_contents)
                    language_mapping = {
                        "English": "en",
                        "Hindi": "hi",
                        "Kannada": "kn",
                        "Malayalam": "ml",
                        "Tamil": "ta",
                        "Telugu": "te"
                    }
                    target_language_code = language_mapping.get(output_language_tab1)

                    if source_language == target_language_code:
                        st.warning(f"The content you provided already in {output_language_tab1}.")
                        st.stop()  # Stop the program
                    else:
                        translated_text = google_gemini_translate(file_contents, None, target_language_code)
                        st.session_state.translated_text_tab1 = translated_text
            else:   
                st.error("Please upload a file with the extension .txt")

    # Display translated result
    if "translated_text_tab1" in st.session_state:
        st.write("Translated content")
        st.success(st.session_state.translated_text_tab1)

        # Create file name based on current time hashed with MD5
        current_time = datetime.now().isoformat()
        md5_hash = hashlib.md5(current_time.encode()).hexdigest()
        file_name = f"{md5_hash}.txt"

        # Create .txt file for translated content and provide download link
        translated_text = st.session_state.translated_text_tab1
        buffer = io.BytesIO()
        buffer.write(translated_text.encode('utf-8'))
        buffer.seek(0)
        
        st.download_button(
            label="Download translation",
            data=buffer,
            file_name=file_name,
            mime="text/plain"
        )

with tab2:
    col_1, col_2 = st.columns(2)

    # Column for selecting output language
    with col_1:
        output_languages_list = [
             'English',
             'Hindi',  'Kannada','Malayalam',
            'Tamil', 'Telugu'
        ]

        output_language_tab2 = st.selectbox(label="Output language", options=output_languages_list, key="output_language_tab2")

    # Column for entering input text
    with col_2:
        input_text_tab2 = st.text_area("Enter text here (up to 1000 characters)", key="input_text_tab2")

    if "input_language_tab2" not in st.session_state:
        st.session_state.input_language_tab2 = "en"

    if st.button("Translate", key="translate_button_tab2"):
        if input_text_tab2.strip():
            if len(input_text_tab2) > 1000:
                st.warning("Limit is 1000 characters.")
                st.stop()  # Stop the program
            else:
                language_mapping = {
                     "English": "en", "Kannada": "kn","Malayalam": "ml", "Tamil": "ta",
                    "Telugu": "te"
                }

                input_language = st.session_state.input_language_tab2 
                output_language = output_language_tab2 

                # Google Translate API
                translator = Translator()
                translated = translator.translate(input_text_tab2, src=input_language, dest=output_language)
                st.session_state.translated_text_tab2 = translated.text
        else:
            st.warning("Please enter the text to be translated.")

    # Display translated result
    if "translated_text_tab2" in st.session_state:
        st.success(st.session_state.translated_text_tab2)

# Tab 3: ChatBot
with tab3:
    # Function to translate roles between Gemini-Pro and Streamlit's terminology
    def translate_role_for_streamlit(user_role):
        if user_role == "model":
            return "assistant"
        else:
            return user_role

    # Initialize chat session in Streamlit if not already present
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = []

    # Display chat history (older messages at the top)
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for message in st.session_state.chat_session:
        role = translate_role_for_streamlit(message['role'])
        with st.chat_message(role):
            st.markdown(f'<div class="chat-message">{message["text"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Input field for user's message (always at the bottom)
    user_prompt = st.chat_input("Enter your question here...")

    if user_prompt:
        # Add user's message to chat and display it
        st.session_state.chat_session.append({"role": "user", "text": user_prompt})
        st.chat_message("user").markdown(user_prompt)

        # Send user's message to Google Gemini API and get response
        gemini_response = google_gemini_translate(user_prompt)
        st.session_state.chat_session.append({"role": "assistant", "text": gemini_response})
        st.chat_message("assistant").markdown(gemini_response)