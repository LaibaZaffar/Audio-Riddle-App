import streamlit as st
import whisper
from streamlit_mic_recorder import mic_recorder
import time
import base64
st.markdown(
    """
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    """,
    unsafe_allow_html=True
)

def load_css():
    with open("./main.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

load_css()

# Initialize session state variables
if 'transcribed_text' not in st.session_state:
    st.session_state.transcribed_text = None

if 'scores' not in st.session_state:
    st.session_state.scores = {
        'Easy': 0,
        'Medium': 0,
        'Hard': 0
    }

if 'question_index' not in st.session_state:
    st.session_state.question_index = 0

if 'audio_file' not in st.session_state:
    st.session_state.audio_file = None

if 'show_result' not in st.session_state:
    st.session_state.show_result = False

if 'show_clue' not in st.session_state:
    st.session_state.show_clue = False
    
# sidebar component
with st.sidebar:
    all_img = get_image_base64("./all.png")

    st.markdown("<h1> ~ A Ridiculous App ~</h1>", unsafe_allow_html=True)
    st.markdown("<h3> Choose Difficulty Level </h3>", unsafe_allow_html=True)
    selected_difficulty = st.selectbox(
        label="Difficulty Level",
        options=["Easy", "Medium", "Hard"],
        label_visibility="collapsed",      
    )   
    if selected_difficulty != st.session_state.get('difficulty'): # on difficulty changes
        st.session_state.difficulty = selected_difficulty
        st.session_state.question_index = 0
        st.session_state.transcribed_text = None
        st.session_state.audio_file = None
        st.session_state.show_result = False
        # st.rerun()
        
    st.markdown("<h2> Make sure your microphone is working before starting! </h2>", unsafe_allow_html=True)
    st.markdown(f"""
        <p>
            <img src='data:image/png;base64,{all_img}' 
            class="sidebar-image" 
            >
        </p>
    """, unsafe_allow_html=True)

# Load Whisper model with error handling
@st.cache_resource
def load_model():
    try:
        return whisper.load_model("base")
    except Exception as e:
        st.error(f"Error loading Whisper model: {e}")
        return None

model = load_model()

if model is None:
    st.error("Model failed to load. Please check your installation.")
    
# Initialize quiz questions
quiz_questions = {
    "Easy": [
        {"question": "What is the least spoken language?", "answer": "sign language", "clue": "You use your hands for this"},
        {"question": "What is so unbelievably fragile that just by speaking it's name will break it?", "answer": "silence", "clue": "It's golden when you keep it"},
        {"question": "What goes up and never ever comes down?", "answer": "Age", "clue": "Numbers that only increase as time passes"}
    ],
    "Medium": [
        {"question": "What word becomes shorter when you add two more letters to it?", "answer": "Short", "clue": "The answer is the opposite of long"},
        {"question": "Johnny's mother had three children. The first child was named April The second child was named May. What was the third child's name?", "answer": "Johnny", "clue": "The answer is in the question itself"},
        {"question": "What do you lose the moment you share it?", "answer": "secret", "clue": "Something you keep to yourself"}
    ],
    "Hard": [
        {"question": "What has a port but no ship?", "answer": "network", "clue": "Think about your computer"},
        {"question": "What has 3 letters and start with gas?", "answer": "Car", "clue": "You drive this every day"},
        {"question": "What has hands but cannot clap?", "answer": "clock", "clue": "It helps you tell time"}
    ]
}

hehe_img = get_image_base64("./hehe.png")
sad_img = get_image_base64("./sad.png")

# container
sigaar_img = get_image_base64("./sideeye.png")
st.markdown(f"""
            <h1 class='title'>
            <img src='data:image/png;base64,{sigaar_img}' 
            style='height: 100px;
            vertical-align: middle;
            margin-right: 10px;'>
            Guess Poka? 
            </h1>
            """,
            unsafe_allow_html=True)

difficulty = st.session_state.get('difficulty', 'Easy')
current_questions = quiz_questions[difficulty]
question_index = st.session_state.get("question_index", 0)
st.markdown(
              f"""
              <div class="question-card">
              <h3 class="question"> Q.  {current_questions[question_index]['question']}</h3>
              </div>
               """,
              unsafe_allow_html=True
             )

speak_img = get_image_base64("./pngwing.com.png")

# Create two columns for clue and recording
col_record, col_clue = st.columns([4, 1])
with col_record:
    
    st.markdown(
        f"""
        <h4 class='subtitle'>
            <img src='data:image/png;base64,{speak_img}' 
            style='height: 30px;
            vertical-align: middle;
            margin-right: 2px;'>
            Record your answer here 
        </h4>
        """, 
        unsafe_allow_html=True
    )
    # Record Audio
    audio_file = mic_recorder(start_prompt=" Bello ▶️", stop_prompt="Stupa ⏹️  ", key=f"recorder_{question_index}")

with col_clue:
    if st.button("💡", key="clue_btn"):
        st.session_state.show_clue = not st.session_state.show_clue
    
    if st.session_state.show_clue:
        st.markdown(
            f"""
            <div class="clue-popup">
                {current_questions[question_index]['clue']}
            </div>
            """,
            unsafe_allow_html=True
        )


# Process audio file and transcribe
if audio_file and "bytes" in audio_file:
    file_path = "temp_audio.wav"
    with open(file_path, "wb") as f:
        f.write(audio_file["bytes"])
    
    try:
        result = model.transcribe(file_path)
        st.session_state.transcribed_text = result["text"].strip().lower()
        st.session_state.show_result = True
    except Exception as e:
        st.error(f"Error in transcription: {e}")
        
  # Display transcription and result
    if st.session_state.show_result:
      st.markdown(
          f"""
          <div class="transcription-box">
              <h4> Your Answer:</h4>
              <p>{st.session_state.transcribed_text}</p>
          </div>
          """, 
          unsafe_allow_html=True
      )

      correct_answer = quiz_questions[difficulty][question_index]["answer"].lower()
      user_answer = st.session_state.transcribed_text.lower().strip()
    
      # Check if the answer is correct using more flexible matching
      is_correct = (
          user_answer == correct_answer or  # Exact match
          correct_answer in user_answer or  # Answer is part of user's response
          user_answer in correct_answer     # User's response is part of answer
      )

      if is_correct:
          if not st.session_state.get(f'q_{difficulty}_{question_index}_answered', False):
              st.session_state.scores[difficulty] += 10
              st.session_state[f'q_{difficulty}_{question_index}_answered'] = True
          st.markdown(
              f'''
              <div class="result-message" 
              style="background-color: #d4edda; 
              color: #155724;"> Correct!</div>
              <img src='data:image/png;base64,{hehe_img}' class='slide-in-left'>
              ''', 
              unsafe_allow_html=True
          )
      else:
          st.markdown(
              f'''
              <div class="result-message" 
              style="background-color: #f8d7da;
              color: #721c24;"> Incorrect. Try again!</div>
              <img src='data:image/png;base64,{sad_img}' class='slide-in-left'>
              ''',
              unsafe_allow_html=True
          )
    # Reset transcription and audio file after showing the result
    st.session_state.transcribed_text = None
    st.session_state.audio_file = None
    st.session_state.show_result = False  # Reset the flag
    st.session_state.show_clue = False
    st.rerun()
# Navigation buttons with custom styling
col1, col2 = st.columns([1, 1])

if col1.button("Previous Question", key="prev_btn", 
    use_container_width=True):
    if question_index > 0:
        st.session_state["question_index"] = question_index - 1
    else:
        st.session_state["question_index"] = len(current_questions) - 1
    st.session_state.transcribed_text = None
    st.session_state.audio_file = None
    st.session_state.show_result = False
    st.session_state.show_clue = False
    st.rerun()

if col2.button("Next Question", key="next_btn", 
    use_container_width=True):
    if question_index < len(current_questions) - 1:
        st.session_state["question_index"] = question_index + 1
    else:
        st.session_state["question_index"] = 0
    st.session_state.transcribed_text = None
    st.session_state.audio_file = None
    st.session_state.show_result = False
    st.session_state.show_clue = False
    st.rerun()

#Scorebar 
total_score = sum(st.session_state.scores.values())
score_img = get_image_base64("./eyes .png")  # Replace with your corner image path
st.markdown(
    f"""
    <div class="score-container">
        <img src='data:image/png;base64,{score_img}' class="score-icon" alt="Eyes Icon">
        <p>Score: {total_score}</p>
    </div>
    """,
    unsafe_allow_html=True
)

# corner_img = get_image_base64("./assets/corner.png")  # Replace with your corner image path
# st.markdown(
#     f"""
#     <img src='data:image/png;base64,{corner_img}' 
#     class='corner-image'>
#     """,
#     unsafe_allow_html=True
# )

