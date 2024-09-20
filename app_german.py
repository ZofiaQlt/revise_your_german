import streamlit as st
import random
import time
import pandas as pd
import matplotlib.pyplot as plt
import io
from collections import defaultdict
from wordcloud import WordCloud
import numpy as np

# Charger les données depuis un fichier CSV
@st.cache_data
def load_data():
    data = pd.read_csv("vocabulaire.csv", delimiter=';')
    return {row['German']: row['French'] for _, row in data.iterrows()}

# Charger le fichier CSV de vocabulaire
words = load_data()

# Initialisation des variables
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
    st.session_state.sleep_time = 0  # Initialisation de sleep_time

# Dictionnaire pour suivre les erreurs par mot
if 'error_counts' not in st.session_state:
    st.session_state.error_counts = defaultdict(int)

def get_weighted_word(word_scores):
    """Retourne un mot pondéré aléatoire selon son score."""
    weighted_list = []
    for word, score in word_scores.items():
        weighted_list.extend([word] * score)
    return random.choice(weighted_list)

def revise_words(words_dict, word_scores):
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

    # Crée un formulaire pour gérer la soumission via "Enter" du clavier ou en en appuyant sur le bouton de l'application
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_input("Votre réponse:", key="answer_input")
        submit_button = st.form_submit_button(label="Valider")

    # Si le formulaire est soumis
    if submit_button:
        if user_input.strip().lower() == correct_answer.lower():
            st.write("✅ Correct !\n")
            st.session_state.correct += 1
            word_scores[st.session_state.current_word] = max(1, word_scores[st.session_state.current_word] - 1)  # Réduit le score pour diminuer la fréquence
            st.session_state.sleep_time += 1  # Ajoute 1 seconde au temps de pause
            time.sleep(1)  # Pause
        else:
            st.write(f"❌ Faux ! La bonne réponse est _'{correct_answer}'_.\n")
            st.session_state.incorrect += 1
            word_scores[st.session_state.current_word] += 2  # Augmente le score pour augmenter la fréquence
            st.session_state.error_counts[st.session_state.current_word] += 1  # Incrémentation du compteur d'erreurs
            st.session_state.sleep_time += 1.75  # Ajoute des secondes au temps de pause
            time.sleep(1.75)  # Pause

        # Passer à la question suivante
        st.session_state.current_word = get_weighted_word(word_scores)
        st.rerun()  # Recharge la page pour afficher la nouvelle question
        
def show_statistics():
    """Affiche les statistiques de la session."""
    
    # CSS pour ajouter un fond jaune clair à la section des statistiques
    st.markdown("""
        <style>
        .stat-section {
            background-color: #ffffe0;  /* Fond jaune pâle */
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #d3d3d3;
        }
        </style>
    """, unsafe_allow_html=True)

    if st.session_state.session_start_time is None:
        st.write("Les statistiques seront disponibles après avoir commencé la révision.")
        return

    session_duration = time.time() - st.session_state.session_start_time - st.session_state.sleep_time
    avg_time_per_question = session_duration / (st.session_state.correct + st.session_state.incorrect) if (st.session_state.correct + st.session_state.incorrect) > 0 else 0

    # Pourcentage de bonnes réponses
    total_questions = st.session_state.correct + st.session_state.incorrect
    correct_percentage = (st.session_state.correct / total_questions * 100) if total_questions > 0 else 0

    # Encadrer les statistiques dans une div avec la classe stat-section
    st.markdown('<div class="stat-section">', unsafe_allow_html=True)
    
    if st.session_state.correct + st.session_state.incorrect > 0:
        # Afficher les statistiques générales
        st.write(f"__Pourcentage de bonnes réponses :__ {correct_percentage:.1f}%")
        st.write(f"__Temps moyen par question :__ {avg_time_per_question:.1f} secondes")

        # Afficher le top 5 des mots avec le plus grand nombre d'erreurs
        if st.session_state.error_counts:
            sorted_errors = sorted(st.session_state.error_counts.items(), key=lambda x: x[1], reverse=True)
            top_5_errors = sorted_errors[:5]
            st.write("__Top 5 des mots avec le plus grand nombre d'erreurs :__\n")
            for word, count in top_5_errors:
                error_label = "erreur" if count == 1 else "erreurs"
                st.write(f"- {word} : {count} {error_label}")
        else:
            st.write("Aucune erreur enregistrée.")

        st.write("---\n")
        # Créer un donut chart pour les réponses correctes et incorrectes
        labels = 'Correct', 'Incorrect'
        sizes = [st.session_state.correct, st.session_state.incorrect]
        colors = ['#ebd61c', '#eb4528']  # Couleurs viridis '#1F9C92'
        fig, ax = plt.subplots()
        fig.set_size_inches(6, 6)
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, pctdistance=0.85, colors=colors, wedgeprops=dict(width=0.3))
        # Personnaliser la taille de la police
        for text in texts + autotexts:
            text.set_fontsize(10.5)  # Ajuste la taille de la police selon tes besoins
        ax.axis('equal')  # forme circulaire du donut

        # Créer deux colonnes pour le donut et le wordcloud
        col1, col2 = st.columns(2)

        # Afficher le donut chart dans la première colonne
        with col1:
            donut_chart = io.BytesIO()
            plt.savefig(donut_chart, format='png')
            donut_chart.seek(0)
            st.image(donut_chart)

        # Créer un word cloud et l'afficher dans la deuxième colonne
        if st.session_state.error_counts:
            word_freq = {word: count for word, count in sorted_errors[:10]}
            colors_wordcloud = ['black', '#ebd61c', '#eb4528']
            def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
                return random.choice(colors_wordcloud)

            wordcloud = WordCloud(width=800, height=750, background_color='white', color_func=color_func).generate_from_frequencies(word_freq)

            with col2:
                wordcloud_image = io.BytesIO()
                wordcloud.to_image().save(wordcloud_image, format='png')
                wordcloud_image.seek(0)
                st.image(wordcloud_image)
    else:
        st.write("Pas encore de données pour les statistiques.")
    
    # Fermeture de la div contenant le fond jaune
    st.markdown('</div>', unsafe_allow_html=True)



def main():
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
        st.session_state.session_start_time = None
        st.session_state.error_counts = defaultdict(int)  # Réinitialiser les erreurs
        st.write("Révision réinitialisée!")

    # Utilisation de la méthode get pour éviter l'erreur KeyError
    if not st.session_state.get('start', False):
        if st.button("Commencer la révision"):
            st.session_state.start = True
            st.session_state.current_word = get_weighted_word(st.session_state.word_scores)
            st.session_state.session_start_time = time.time()  # Début de la session
            st.rerun()  # Recharge la page pour commencer la révision

    elif st.session_state.revision_direction is None:
        # Utilisation des colonnes pour placer les boutons côte à côte
        col1, col2 = st.columns([3, 5])
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
    else:
        revise_words(words, st.session_state.word_scores)

    st.write(f"Score : {st.session_state.correct} corrects, {st.session_state.incorrect} incorrects")

    with st.form(key='stats_form', clear_on_submit=True):
        # Appliquer la classe CSS
        st.markdown('<div class="stats-form">', unsafe_allow_html=True)

        # Contenu du formulaire
        if st.form_submit_button("Statistiques"):
            show_statistics()

        # Fin de la div pour le formulaire
        st.markdown('</div>', unsafe_allow_html=True)


        
if __name__ == "__main__":
    main()
