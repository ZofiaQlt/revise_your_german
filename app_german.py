import streamlit as st
import random
import time

# Dictionnaire de mots
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
    # Choix du type de révision
    if st.session_state.revision_direction == 'french_to_german':
        # Révision du français vers l'allemand
        german_word = st.session_state.current_word
        french_translation = words_dict[german_word]
        st.write(f"Quel est le mot allemand pour _'{french_translation}'_ ?")
        correct_answer = german_word
    elif st.session_state.revision_direction == 'german_to_french':
        # Révision de l'allemand vers le français
        french_translation = words_dict[st.session_state.current_word]
        st.write(f"Quel est le mot français pour _'{st.session_state.current_word}'_ ?")
        correct_answer = french_translation
    elif st.session_state.revision_direction == 'mixed':
        # Révision mixte
        if random.choice([True, False]):
            # Révision du français vers l'allemand
            german_word = st.session_state.current_word
            french_translation = words_dict[german_word]
            st.write(f"Quel est le mot allemand pour _'{french_translation}'_ ?")
            correct_answer = german_word
        else:
            # Révision de l'allemand vers le français
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
        st.experimental_rerun()  # Recharge la page pour afficher la nouvelle question

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
        st.write("Révision réinitialisée!")

    # Utilisation de la méthode get pour éviter l'erreur KeyError
    if not st.session_state.get('start', False):
        if st.button("Commencer la révision"):
            st.session_state.start = True
            st.session_state.current_word = get_weighted_word(st.session_state.word_scores)
            st.experimental_rerun()  # Recharge la page pour commencer la révision
    elif st.session_state.revision_direction is None:
        # Utilisation des colonnes pour placer les boutons côte à côte
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("___Français -> Allemand___", key='french_to_german'):
                st.session_state.revision_direction = 'french_to_german'
                st.session_state.current_word = get_weighted_word(st.session_state.word_scores)
                st.experimental_rerun()
        with col2:
            if st.button("___Allemand -> Français___", key='german_to_french'):
                st.session_state.revision_direction = 'german_to_french'
                st.session_state.current_word = get_weighted_word(st.session_state.word_scores)
                st.experimental_rerun()
        with col3:
            if st.button("___Révision mixte___", key='mixed'):
                st.session_state.revision_direction = 'mixed'
                st.session_state.current_word = get_weighted_word(st.session_state.word_scores)
                st.experimental_rerun()
    else:
        revise_words(words, st.session_state.word_scores)

    st.write(f"Score: {st.session_state.correct} corrects, {st.session_state.incorrect} incorrects")
