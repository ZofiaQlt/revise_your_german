import streamlit as st
import random
import time

# Exemple de dictionnaire de mots (tu peux remplacer par ta liste de 3000 mots)
words = {
    "Das Haus": "La maison",
    "Der Baum": "L'arbre",
    "Der Freund": "L'ami",
    "Das Buch": "Le livre",
    "Der Hund": "Le chien",
    "Der Beruf": "La profession",
    "Das Werk": "L'usine",
    "Die Stelle": "Le poste",
    "Schmutzig": "Sale",
    "Anstrengend": "Fatigant",
    "Der Lohn": "Le salaire",
    "Geld verdienen": "Gagner de l'argent",
    "Sein Brot verdienen": "Gagner sa vie",
    "Seinen Lebensunterhalt verdienen": "Gagner sa vie",
    "Die Fähigkeit": "La capacité",
    "Der Betrieb": "L'entreprise",
    "Das Unternehmen": "L'entreprise",
    "Gründen": "Fonder",
    "Die Arbeitslosigkeit": "Le chômage",
    "Der Arbeitgeber": "L'employeur",
    "Der Arbeitnehmer": "Le salarié",
    "Die Arbeitskräfte": "La main d'oeuvre",
    "Einen Beruf ausüben": "Exercer un métier",
    "Jdn beschäftigen": "Employer qn",
    "Einstellen": "Embaucher",
    "Der Mitarbeiter": "L'employé",
    "Der Angestellte": "L'employé",
    "Jdn entlassen": "Licencier qn",
    "Vor die Tür setzen": "Mettre à la porte",
    "Der Bereich": "Le domaine, le secteur",
    "Häufig": "Souvent, fréquent",
    "Der Begriff": "Le terme, le concept",
    "Verwenden": "Utiliser",
    "Ergänzen": "Compléter, ajouter",
    "Gering": "Faible, minime",
    "Passende": "Approprié",
    "Äusserst": "Extrêmement",
    "Nützen": "Servir, être utile, profiter à qn",
    "Die Lohnerhöhung": "L'augmentation de salaire"
    # Ajoute ici les autres mots (jusqu'à 3000 mots)
}

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

def get_weighted_word(word_scores):
    """Retourne un mot pondéré aléatoire selon son score."""
    weighted_list = []
    for word, score in word_scores.items():
        weighted_list.extend([word] * score)
    return random.choice(weighted_list)

def revise_words(words_dict, word_scores):
    """Révise les mots selon la direction spécifiée."""
    if st.session_state.revision_direction == 'french_to_german':
        german_word = st.session_state.current_word
        french_translation = words_dict[german_word]
        question = f"Quel est le mot allemand pour _'{french_translation}'_ ?"
        correct_answer = german_word
    elif st.session_state.revision_direction == 'german_to_french':
        german_word = st.session_state.current_word
        french_translation = words_dict[german_word]
        question = f"Quel est le mot français pour _'{german_word}'_ ?"
        correct_answer = french_translation
    elif st.session_state.revision_direction == 'mixed':
        if random.choice([True, False]):
            german_word = st.session_state.current_word
            french_translation = words_dict[german_word]
            question = f"Quel est le mot allemand pour _'{french_translation}'_ ?"
            correct_answer = german_word
        else:
            german_word = st.session_state.current_word
            french_translation = words_dict[german_word]
            question = f"Quel est le mot français pour _'{german_word}'_ ?"
            correct_answer = french_translation

    st.write(question)
    
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

def display_buttons():

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Réviser de français vers allemand", key="french_to_german"):
            st.session_state.revision_direction = 'french_to_german'
            st.session_state.current_word = get_weighted_word(st.session_state.word_scores)
            st.experimental_rerun()  # Recharge la page pour mettre à jour l'état
    with col2:
        if st.button("Réviser d'allemand vers français", key="
