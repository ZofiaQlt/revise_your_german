import streamlit as st
import random
import time
import pandas as pd

# Charger les données depuis un fichier CSV
@st.cache_data
def load_data():
    data = pd.read_csv("vocabulaire.csv", delimiter=';')
    return {row['German']: row['French'] for _, row in data.iterrows()}

# Charger le fichier CSV de vocabulaire
words = load_data()

# Initialisation des scores des mots et autres variables
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
if 'error_mode' not in st.session_state:
    st.session_state.error_mode = False  # Nouveau mode : révision des erreurs

def get_weighted_word(word_scores):
    """Retourne un mot pondéré aléatoire selon son score."""
    weighted_list = []
    for word, score in word_scores.items():
        weighted_list.extend([word] * score)
    return random.choice(weighted_list)

def get_error_words(word_scores, threshold=3):
    """Retourne une liste des mots avec un score supérieur au seuil donné."""
    return [word for word, score in word_scores.items() if score >= threshold]

def revise_words(words_dict, word_scores):
    # Révision des erreurs fréquentes
    if st.session_state.error_mode:
        error_words = get_error_words(word_scores)
        if error_words:
            st.session_state.current_word = random.choice(error_words)
        else:
            st.write("✅ Vous n'avez plus de mots à réviser dans les erreurs fréquentes !")
            st.session_state.error_mode = False
            return

    # Révision mixte : choix aléatoire du sens (français -> allemand ou allemand -> français)
    if st.session_state.revision_direction == 'mixed':
        if random.choice([True, False]):
            st.session_state.revision_direction = 'french_to_german'
        else:
            st.session_state.revision_direction = 'german_to_french'

    # Révision du français vers l'allemand
    if st.session_state.revision_direction == 'french_to_german':
        german_word = st.session_state.current_word
        french_translation = words_dict[german_word]
        st.write(f"Quel est le mot allemand pour _'{french_translation}'_ ?")
        correct_answer = german_word

    # Révision de l'allemand vers le français
    elif st.session_state.revision_direction == 'german_to_french':
        french_translation = words_dict[st.session_state.current_word]
        st.write(f"Quel est le mot français pour _'{st.session_state.current_word}'_ ?")
        correct_answer = french_translation

    # Crée un formulaire pour gérer la soumission via "Enter"
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_input("Votre réponse:", key="answer_input")
        submit_button = st.form_submit_button(label="Valider")

    # Si le formulaire est soumis (par "Enter" ou en appuyant sur le bouton)
    if submit_button:
        if user_input.lower() == correct_answer.lower():
            st.write("✅ Correct !\n")
            st.session_state.correct += 1
            word_scores[st.session_state.current_word] = max(1, word_scores[st.session_state.current_word] - 1)  # Réduit le score pour diminuer la fréquence
            time.sleep(1)  # Pause de 1 seconde pour une réponse correcte
        else:
            st.write(f"❌ Faux ! La bonne réponse est _'{correct_answer}'_.\n")
            st.session_state.incorrect += 1
            word_scores[st.session_state.current_word] += 2  # Augmente le score pour augmenter la fréquence
            time.sleep(2)  # Pause de 2 secondes pour une réponse incorrecte

        # Passer à la question suivante
        st.session_state.current_word = get_weighted_word(word_scores)
        st.rerun()  # Recharge la page pour afficher la nouvelle question

if __name__ == "__main__":
    st.title("🇩🇪 Outil de révision des mots en allemand avec répétition espacée")

    # Ajouter un espace
    st.write("")

    # Ajouter une image
    st.image("img.png", width=400)

    # Ajouter un espace
    st.write("")

    if st.button("Réinitialiser la révision"):
        st.session_state.word_scores = {word: 1 for word in words.keys()}
        st.session_state.start = False
        st.session_state.correct = 0
        st.session_state.incorrect = 0
        st.session_state.revision_direction = None
        st.session_state.error_mode = False
        st.write("Révision réinitialisée!")

    # Utilisation de la méthode get pour éviter l'erreur KeyError
    if not st.session_state.get('start', False):
        if st.button("Commencer la révision"):
            st.session_state.start = True
            st.session_state.current_word = get_weighted_word(st.session_state.word_scores)
            st.rerun()  # Recharge la page pour commencer la révision

    # Bouton pour activer le mode "révision des erreurs"
    elif not st.session_state.error_mode and st.button("___🧠 Réviser uniquement les erreurs fréquentes___"):
        st.session_state.error_mode = True
        st.session_state.revision_direction = 'mixed'  # Révision mixte par défaut
        st.rerun()

    elif st.session_state.revision_direction is None:
        # Utilisation des colonnes pour placer les boutons côte à côte
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("___Français 🇫🇷 -> Allemand 🇩🇪___", key='french_to_german'):
                st.session_state.revision_direction = 'french_to_german'
                st.session_state.current_word = get_weighted_word(st.session_state.word_scores)
                st.rerun()
        with col2:
            if st.button("___Allemand 🇩🇪 -> Français 🇫🇷___", key='german_to_french'):
                st.session_state.revision_direction = 'german_to_french'
                st.session_state.current_word = get_weighted_word(st.session_state.word_scores)
                st.rerun()
        with col3:
            if st.button("___Révision mixte 🇫🇷🇩🇪___", key='mixed'):
                st.session_state.revision_direction = 'mixed'
                st.session_state.current_word = get_weighted_word(st.session_state.word_scores)
                st.rerun()
    else:
        revise_words(words, st.session_state.word_scores)

    st.write(f"Score: {st.session_state.correct} corrects, {st.session_state.incorrect} incorrects")
