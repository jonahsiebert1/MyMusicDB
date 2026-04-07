import streamlit as st
import pandas as pd
import random

# --- CONFIGURATION & DATA LOADING ---
st.set_page_config(page_title="Music Quiz Pro", page_icon="🎵")

@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        # Create a helper column for the 'Artist' (Interpreter or Composer)
        df['primary_artist'] = df['interpreter'].fillna(df['composer']).fillna("Unknown")
        return df
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return None

# Load your specific file
data = load_data('musicDB.csv')

# --- SESSION STATE ---
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'current_q' not in st.session_state:
    st.session_state.current_q = None
if 'answered' not in st.session_state:
    st.session_state.answered = False
if 'options' not in st.session_state:
    st.session_state.options = []

# --- QUIZ LOGIC ---
def get_new_question():
    if data is not None:
        row = data.sample(n=1).iloc[0]
        mode = random.randint(0, 1)
        
        # Check for duplicates to provide hints
        dup_titles = len(data[data['title'] == row['title']]) > 1
        dup_artists = len(data[data['primary_artist'] == row['primary_artist']]) > 1

        if mode == 0: # Title -> Artist
            q_text = f"Who is the artist/composer of the track: **'{row['title']}'**?"
            if dup_titles:
                q_text += f"\n\n*(Clue: This version is from the album '{row['album']}')*"
            
            correct_answer = row['primary_artist']
            # Get 3 other unique random artists as distractors
            distractors = data[data['primary_artist'] != correct_answer]['primary_artist'].unique().tolist()
            wrong_choices = random.sample(distractors, min(3, len(distractors)))
            
        else: # Artist -> Title
            q_text = f"Which of these tracks was created by: **'{row['primary_artist']}'**?"
            if dup_artists:
                q_text += f"\n\n*(Clue: The vibe is {row['feelings']})*"
            
            correct_answer = row['title']
            # Get 3 other unique random titles as distractors
            distractors = data[data['title'] != correct_answer]['title'].unique().tolist()
            wrong_choices = random.sample(distractors, min(3, len(distractors)))

        # Mix the choices
        all_options = wrong_choices + [correct_answer]
        random.shuffle(all_options)

        st.session_state.current_q = {
            "question": q_text,
            "answer": correct_answer,
            "raw_row": row
        }
        st.session_state.options = all_options
        st.session_state.answered = False

# --- UI LAYOUT ---
st.title("🎵 Multiple Choice Music Quiz")

if data is not None:
    if st.session_state.current_q is None:
        get_new_question()

    q = st.session_state.current_q
    
    st.sidebar.metric("Total Score", st.session_state.score)
    if st.sidebar.button("Reset Score"):
        st.session_state.score = 0
        st.rerun()
    
    with st.container(border=True):
        st.markdown(f"### {q['question']}")
        
        # Use a radio or selectbox for "Checking" only
        # We disable the radio once an answer is submitted
        user_choice = st.radio(
            "Select the correct option:",
            options=st.session_state.options,
            index=None,
            disabled=st.session_state.answered
        )
        
        if not st.session_state.answered:
            if st.button("Check Answer"):
                if user_choice is None:
                    st.warning("Please select an option first!")
                else:
                    st.session_state.answered = True
                    if user_choice == q['answer']:
                        st.success(f"✅ Correct! It is {q['answer']}.")
                        st.session_state.score += 1
                    else:
                        st.error(f"❌ Wrong. The correct answer was: {q['answer']}")
                    st.rerun() # Refresh to show results and Next button

    # Navigation
    if st.session_state.answered:
        if st.button("Next Question ➡️"):
            get_new_question()
            st.rerun()
            
    # Metadata Expanders
    with st.expander("Show Track Details"):
        st.write(f"**Album:** {q['raw_row']['album']}")
        st.write(f"**Genre:** {q['raw_row']['all_genres']}")
        st.write(f"**Atmosphere:** {q['raw_row']['atmosphere']}")
        st.write(f"**Feelings:** {q['raw_row']['feelings']}")

else:
    st.warning("Please ensure 'musicDB.csv' is in your repository.")
