import streamlit as st
import pandas as pd
import random

# --- CONFIGURATION & DATA LOADING ---
st.set_page_config(page_title="Music Quiz Pro", page_icon="🎵")

def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        # Create a helper column for the 'Artist'
        df['primary_artist'] = df['interpreter'].fillna(df['composer'])
        return df
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return None

# Assuming your file is named 'music_data.csv' in the same folder
data = load_data('musicDB.csv')

# --- SESSION STATE ---
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'current_q' not in st.session_state:
    st.session_state.current_q = None
if 'answered' not in st.session_state:
    st.session_state.answered = False

# --- QUIZ LOGIC ---
def get_new_question():
    if data is not None:
        row = data.sample(n=1).iloc[0]
        # Randomly flip between Title-to-Artist (0) or Artist-to-Title (1)
        mode = random.randint(0, 1)
        
        # Determine if we need distinguishing clues
        dup_titles = len(data[data['title'] == row['title']]) > 1
        dup_artists = len(data[data['primary_artist'] == row['primary_artist']]) > 1

        if mode == 0: # Title -> Artist
            q_text = f"Who is the artist/composer of the track: **'{row['title']}'**?"
            if dup_titles:
                q_text += f"\n\n*(Clue: This version is from the album '{row['album']}')*"
            answer = row['primary_artist']
        else: # Artist -> Title
            q_text = f"Name a track by: **'{row['primary_artist']}'**"
            if dup_artists:
                q_text += f"\n\n*(Clue: The vibe is {row['feelings']})*"
            answer = row['title']

        st.session_state.current_q = {
            "question": q_text,
            "answer": answer,
            "raw_row": row
        }
        st.session_state.answered = False

# --- UI LAYOUT ---
st.title("🎵 The Endless Music Quiz")

if data is not None:
    if st.session_state.current_q is None:
        get_new_question()

    q = st.session_state.current_q
    
    st.metric("Current Score", st.session_state.score)
    
    with st.container(border=True):
        st.markdown(q['question'])
        
        # Form for answering
        with st.form("quiz_form"):
            user_input = st.text_input("Your answer:").strip()
            submitted = st.form_submit_button("Check Answer")
            
            if submitted:
                st.session_state.answered = True
                if user_input.lower() == str(q['answer']).lower():
                    st.success(f"Correct! It was {q['answer']}.")
                    st.session_state.score += 1
                else:
                    st.error(f"Not quite. The correct answer was: {q['answer']}")

    # Navigation
    if st.session_state.answered:
        if st.button("Next Question ➡️"):
            get_new_question()
            st.rerun()
            
    # Metadata Expanders for the curious
    with st.expander("Track Details (Hints inside)"):
        st.write(f"**Album:** {q['raw_row']['album']}")
        st.write(f"**Genre:** {q['raw_row']['all_genres']}")
        st.write(f"**Atmosphere:** {q['raw_row']['atmosphere']}")

else:
    st.warning("Please ensure 'music_data.csv' is in the script directory.")
