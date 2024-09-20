import streamlit as st
import random
import time
import pandas as pd
import matplotlib.pyplot as plt
import io
from collections import defaultdict
from wordcloud import WordCloud
import numpy as np
from enum import Enum
from typing import Dict

# Enum pour la direction de révision
class RevisionDirection(Enum):
    FRENCH_TO_GERMAN = 'french_to_german'
    GERMAN_TO_FRENCH = 'german_to_french'

# Charger les données depuis un fichier CSV
@st.cache_data
def load_data(file_path: str) -> Dict[str, str]:
    """Charge le vocabulaire à partir d'un fichier CSV et renvoie un dictionnaire."""
    data = pd.read_csv(file_path, delimiter=';')
    return {row['German']: row['French'] for _, row in data.iterrows()}

# Initialisation de l'état de session
def initialize_session_state(words: Dict[str, str]) -> None:
    """Initialise toutes les variables de session nécessaires."""
    if 'word_scores' not in st.session_state:
        st.session_state.word_scores = {word: 1 for word in words.keys()}
    if 'current_word' not in st.session_state:
        st.session_state.current_word = random.choice(list(words.keys()))
    if 'start' not in st.session_state:
        st.session_state.start = False
    if 'correct' not in st.session_state:
        st.session_state.correct = 0
    if 'incorrect' not in st.session_state:
        st.session_state.incorrect = 0
    if 'revision_direction' not in st.session_state:
        st.session_state.revision_direction = None
    if 'session_start_time' not in st.session_state:
        st.session_state.session_start_time = time.time()  # Démarre la session
    if 'sleep_time' not in st.session_state:
        st.session_state.sleep_time = 0  # Temps de pause total
    if 'error_counts' not in st.session_state:
        st.session_state.error_counts = defaultdict(int)

def get_weighted_word(word_scores: Dict[str, int]) -> str:
    """Retourne un mot aléatoire pondéré selon son score."""
    weighted_list = [word for word, score in word_scores.items() for _ in range(score)]
    return random.choice(weighted_list)

def revise_words(words_dict: Dict[str, str], word_scores: Dict[str, int]) -> None:
    """Affiche une question pour réviser un mot en fonction de la direction de révision."""
    if st.session_state.revision_direction == RevisionDirection.FRENCH_TO_GERMAN:
        question_word = words_dict[st.session_state.current_word]
        correct_answer = st.session_state.current_word
        st.write(f"Quel est le mot allemand pour _'{question_word}'_ ?")
    elif st.session_state.revision_direction == RevisionDirection.GERMAN_TO_FRENCH:
        question_word = st.session_state.current_word
        correct_answer = words_dict[st.session_state.current_word]
        st.write(f"Quel est le mot français pour _'{question_word}'_ ?")

    # Formulaire pour la réponse
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_input("Votre réponse:", key="answer_input")
        submit_button = st.form_submit_button(label="Valider")

    if submit_button:
        validate_answer(user_input, correct_answer, word_scores)

def validate_answer(user_input: str, correct_answer: str, word_scores: Dict[str, int]) -> None:
    """Valide la réponse de l'utilisateur et met à jour les scores."""
    if user_input.strip().lower() == correct_answer.lower():
        st.write("✅ Correct !\n")
        st.session_state.correct += 1
        word_scores[st.session_state.current_word] = max(1, word_scores[st.session_state.current_word] - 1)
        st.session_state.sleep_time += 1
        time.sleep(1)  # Pause après une réponse correcte
    else:
        st.write(f"❌ Faux ! La bonne réponse est _'{correct_answer}'_.\n")
        st.session_state.incorrect += 1
        word_scores[st.session_state.current_word] += 2
        st.session_state.error_counts[st.session_state.current_word] += 1
        st.session_state.sleep_time += 1.75
        time.sleep(1.75)  # Pause après une réponse incorrecte

    st.session_state.current_word = get_weighted_word(word_scores)
    st.rerun()  # Recharge la page pour afficher la nouvelle question

def show_statistics() -> None:
    """Affiche les statistiques de la session de révision."""
    if st.session_state.session_start_time is None:
        st.write("Les statistiques seront disponibles après avoir commencé la révision.")
        return

    session_duration = time.time() - st.session_state.session_start_time - st.session_state.sleep_time
    total_questions = st.session_state.correct + st.session_state.incorrect
    avg_time_per_question = session_duration / total_questions if total_questions > 0 else 0
    correct_percentage = (st.session_state.correct / total_questions * 100) if total_questions > 0 else 0

    st.write(f"__Pourcentage de bonnes réponses :__ {correct_percentage:.1f}%")
    st.write(f"__Temps moyen par question :__ {avg_time_per_question:.1f} secondes")

    show_most_common_errors()
    show_charts()

def show_most_common_errors() -> None:
    """Affiche les mots les plus souvent mal orthographiés."""
    if st.session_state.error_counts:
        sorted_errors = sorted(st.session_state.error_counts.items(), key=lambda x: x[1], reverse=True)
        top_5_errors = sorted_errors[:5]
        st.write("__Top 5 des mots avec le plus grand nombre d'erreurs :__")
        for word, count in top_5_errors:
            error_label = "erreur" if count == 1 else "erreurs"
            st.write(f"- {word} : {count} {error_label}")
    else:
        st.write("Aucune erreur enregistrée.")

def show_charts() -> None:
    """Affiche les graphiques des réponses correctes et incorrectes."""
    col1, col2 = st.columns(2)
    with col1:
        show_donut_chart()
    with col2:
        show_wordcloud()

def show_donut_chart() -> None:
    """Affiche un graphique en forme de donut pour les réponses correctes/incorrectes."""
    labels = ['Correct', 'Incorrect']
    sizes = [st.session_state.correct, st.session_state.incorrect]
    colors = ['#ebd61c', '#eb4528']
    fig, ax = plt.subplots()
    fig.set_size_inches(6, 6)
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors, wedgeprops=dict(width=0.3))
    ax.axis('equal')
    st.pyplot(fig)

def show_wordcloud() -> None:
    """Affiche un nuage de mots basé sur les erreurs les plus fréquentes."""
    if st.session_state.error_counts:
        word_freq = dict(st.session_state.error_counts)
        wordcloud = WordCloud(width=800, height=750, background_color='white').generate_from_frequencies(word_freq)
        st.image(wordcloud.to_image())

def main():
    st.title("🇩🇪 Outil de révision des mots en allemand avec répétition espacée")
    st.image("img.png", width=400)
    
    # Réinitialiser la session
    if st.button("Réinitialiser la révision"):
        initialize_session_state(words)
        st.session_state.start = False
        st.session_state.revision_direction = None
        st.write("Révision réinitialisée!")

    if not st.session_state.start:
        if st.button("Commencer la révision"):
            st.session_state.start = True
            st.session_state.current_word = get_weighted_word(st.session_state.word_scores)
            st.session_state.session_start_time = time.time()
            st.rerun()
    elif st.session_state.revision_direction is None:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🇫🇷 Français -> 🇩🇪 Allemand"):
                st.session_state.revision_direction = RevisionDirection.FRENCH_TO_GERMAN
                st.rerun()
        with col2:
            if st.button("🇩🇪 Allemand -> 🇫🇷 Français"):
                st.session_state.revision_direction = RevisionDirection.GERMAN_TO_FRENCH
                st.rerun()
    else:
        revise_words(words, st.session_state.word_scores)
        with st.form(key='stats_form'):
            if st.form_submit_button("Statistiques"):
                show_statistics()

if __name__ == "__main__":
    words = load_data("vocabulaire.csv")
    initialize_session_state(words)
    main()
