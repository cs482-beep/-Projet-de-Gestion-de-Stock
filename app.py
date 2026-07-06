import os
import pandas as pd
import plotly.express as px
import streamlit as st
import hashlib

# ==========================================
# CONFIGURATION DE LA PAGE & THÈME
# ==========================================
st.set_page_config(
    page_title="G-Stock Pro | Système de Gestion", page_icon="📦", layout="wide"
)

# Style CSS personnalisé (Thème Bleu Nuit & Blanc)
st.markdown(
    """
    <style>
        :root {
            --primary-color: #0A192F;
            --secondary-color: #172A45;
            --accent-color: #3066BE;
            --text-color: #F4F6F9;
        }
        .stButton>button {
            background-color: #3066BE !important;
            color: white !important;
            border-radius: 6px !important;
            border: none !important;
            font-weight: bold;
            width: 100%;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #0A192F !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        h1, h2, h3 {
            color: #0A192F !important;
            font-family: 'Segoe UI', sans-serif;
        }
        .metric-card {
            background-color: #FFFFFF;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            border-left: 5px solid #3066BE;
            margin-bottom: 15px;
        }
    </style>
""",
    unsafe_allow_html=True,
)

CSV_STOCK = "donnees_stock.csv"
CSV_USERS = "utilisateurs.csv"

# ==========================================
# FONCTIONS DE GESTION DES FICHIERS (CSV)
# ==========================================
def hasher_mdp(mdp):
    return hashlib.sha256(mdp.encode()).hexdigest()

def initialiser_fichiers():
    if not os.path.exists(CSV_STOCK):
        data = {
            "ID": [101, 102, 103, 104],
            "Article": ["Capteur Ultrason", "Carte Arduino Uno", "Module GPS GY-NEO6MV2", "Routeur 4G LTE"],
            "Catégorie": ["Électronique", "Microcontrôleurs", "IoT", "Réseau"],
            "Quantité": [50, 30, 15, 10],
            "Prix_Unitaire_DH": [25, 85, 120, 450],
        }
        pd.DataFrame(data).to_csv(CSV_STOCK, index=False)
        
    if not os.path.exists(CSV_USERS):
        users = {
            "Identifiant": ["admin"],
            "Mots_de_passe": [hasher_mdp("ENSA2026")]
        }
        pd.DataFrame(users).to_csv(CSV_USERS, index=False)

initialiser_fichiers()

def charger_stock():
    return pd.read_csv(CSV_STOCK)

def sauvegarder_stock(df):
    df.to_csv(CSV_STOCK, index=False)

def charger_utilisateurs():
    return pd.read_csv(CSV_USERS)

def sauvegarder_utilisateurs(df):
    df.to_csv(CSV_USERS, index=False)

# ==========================================
# GESTION DE L'AUTHENTIFICATION & SESSIONS
# ==========================================
if "connecte" not in st.session_state:
    st.session_state["connecte"] = False
if "user_actuel" not in st.session_state:
    st.session_state["user_actuel"] = None

# ÉCRANS HORS CONNEXION (Connexion / Inscription)
if not st.session_state["connecte"]:
    onglet_auth = st.tabs(["🔐 Connexion", "📝 Inscription"])
    
    # --- ONGLET 1 : CONNEXION ---
    with onglet_auth[0]:
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            st.markdown("<h2 style='text-align: center;'>Espace Connexion</h2>", unsafe_allow_html=True)
            with st.form(key="login_form"):
                identifiant = st.text_input("Identifiant / Login")
                mot_de_passe = st.text_input("Mot de passe", type="password")
                bouton_connexion = st.form_submit_button("Se connecter")

                if bouton_connexion:
                    df_users = charger_utilisateurs()
                    mdp_hash = hasher_mdp(mot_de_passe)
                    
                    user_trouve = df_users[(df_users["Identifiant"] == identifiant) & (df_users["Mots_de_passe"] == mdp_hash)]
                    if not user_trouve.empty:
                        st.session_state["connecte"] = True
                        st.session_state["user_actuel"] = identifiant
                        st.success("Connexion réussie ! Veuillez patienter...")
                        st.button("Accéder au Tableau de Bord") # Évite le rerun forcé qui plante en ligne
                    else:
                        st.error("Identifiant ou mot de passe incorrect.")

    # --- ONGLET 2 : INSCRIPTION ---
    with onglet_auth[1]:
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            st.markdown("<h2 style='text-align: center;'>Créer un compte</h2>", unsafe_allow_html=True)
            with st.form(key="register_form"):
                nouvel_identifiant = st.text_input("Choisissez un Identifiant")
                nouveau_mdp = st.text_input("Choisissez un Mot de passe", type="password")
                confirmer_mdp = st.text_input("Confirmez le Mot de passe", type="password")
                bouton_inscription = st.form_submit_button("S'inscrire")

                if bouton_inscription:
                    if not nouvel_identifiant or not nouveau_mdp:
                        st.error("Tous les champs sont obligatoires.")
                    elif nouveau_mdp != confirmer_mdp:
                        st.error("Les mots de passe ne correspondent pas.")
                    else:
                        df_users = charger_utilisateurs()
                        if nouvel_identifiant in df_users["Identifiant"].values:
                            st.error("Cet identifiant existe déjà. Veuillez en choisir un autre.")
                        else:
                            nouvel_user = {
                                "Identifiant": nouvel_identifiant,
                                "Mots_de_passe": hasher_mdp(nouveau_mdp)
                            }
                            df_users = pd.concat([df_users, pd.DataFrame([nouvel_user])], ignore_index=True)
                            sauvegarder_utilisateurs(df_users)
                            st.success("Compte créé avec succès ! Vous pouvez maintenant vous connecter.")

# ==========================================
# APPLICATION PRINCIPALE (APRÈS CONNEXION)
# ==========================================
else:
    df_stock = charger_stock()

    # Barre latérale (Sidebar) de navigation
    st.sidebar.markdown(
        f"<h3 style='color: white; text-align: center;'>👤 : {st.session_state['user_actuel']}</h3>",
        unsafe_allow_html=True,
    )
    st.sidebar.write("---")
    
    menu = st.sidebar.radio(
        "Sélectionnez une section :",
        ["📊 Tableau de Bord", "📥 Entrées Stock", "📤 Sorties Stock", "⚙️ Mon Compte"],
    )

    st.sidebar.write("---")
    if st.sidebar.button("Se déconnecter"):
        st.session_state["connecte"] = False
        st.session_state["user_actuel"] = None
        st.success("Déconnexion réussie.")
        st.button("Retour à l'accueil")

    # ------------------------------------------
    # SECTION 1 : TABLEAU DE BORD (DASHBOARD)
    # ------------------------------------------
    if menu == "📊 Tableau de Bord":
        st.title("📊 Tableau de Bord des Statistiques")
        st.write("Aperçu en temps réel de l'état de votre stock.")

        total_articles = df_stock["Quantité"].sum()
        valeur_totale = (df_stock["Quantité"] * df_stock["Prix_Unitaire_DH"]).sum()
        references_distinctes = df_stock["Article"].nunique()

        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            st.markdown(f"<div class='metric-card'><h3>📦 Total Articles</h3><h2>{total_articles} unités</h2></div>", unsafe_allow_html=True)
        with kpi2:
            st.markdown(f"<div class='metric-card'><h3>💰 Valeur Stock</h3><h2>{valeur_totale:,.2f} DH</h2></div>", unsafe_allow_html=True)
        with kpi3:
            st.markdown(f"<div class='metric-card'><h3>🔑 Références</h3><h2>{references_distinctes} Réfs</h2></div>", unsafe_allow_html=True)

        st.write("<br>", unsafe_allow_html=True)
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.subheader("Niveau de stock par Article")
            fig_bar = px.bar(df_stock, x="Article", y="Quantité", color="Quantité", color_continuous_scale=["#3066BE", "#0A192F"], template="plotly_white")
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_chart2:
            st.subheader("Répartition par Catégorie")
            fig_pie = px.pie(df_stock, names="Catégorie", values="Quantité", color_discrete_sequence=["#0A192F", "#172A45", "#3066BE"])
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig_pie, use_container_width=True)

        st.subheader("📋 État Actuel du Stock")
        st.dataframe(df_stock, use_container_width=True)

    # ------------------------------------------
    # SECTION 2 : ENTRÉES DE STOCK
    # ------------------------------------------
    elif menu == "📥 Entrées Stock":
        st.title("📥 Réception de Marchandise (Entrées)")
        choix_action = st.radio("Type d'entrée :", ["Réapprovisionner un article existant", "Ajouter une nouvelle référence"])

        if choix_action == "Réapprovisionner un article existant":
            with st.form("form_reelement"):
                article_selectionne = st.selectbox("Choisir l'article", df_stock["Article"].tolist())
                quantite_ajoutee = st.number_input("Quantité reçue", min_value=1, step=1)
                valider_entree = st.form_submit_button("Valider l'entrée")

                if valider_entree:
                    df_stock.loc[df_stock["Article"] == article_selectionne, "Quantité"] += quantite_ajoutee
                    sauvegarder_stock(df_stock)
                    st.success(f"Stock mis à jour ! +{quantite_ajoutee} pour '{article_selectionne}'.")

        else:
            with st.form("form_nouvel_article"):
                nouveau_id = st.number_input("ID de l'article", min_value=int(df_stock["ID"].max() + 1), step=1)
                nouvel_article = st.text_input("Nom de l'article")
                nouvelle_categorie = st.text_input("Catégorie")
                nouvelle_qte = st.number_input("Quantité initiale", min_value=1, step=1)
                nouveau_prix = st.number_input("Prix Unitaire (DH)", min_value=0.0, format="%.2f")
                valider_ajout = st.form_submit_button("Ajouter au catalogue")

                if valider_ajout:
                    if nouvel_article and nouvelle_categorie:
                        nouvel_row = {"ID": nouveau_id, "Article": nouvel_article, "Catégorie": nouvelle_categorie, "Quantité": nouvelle_qte, "Prix_Unitaire_DH": nouveau_prix}
                        df_stock = pd.concat([df_stock, pd.DataFrame([nouvel_row])], ignore_index=True)
                        sauvegarder_stock(df_stock)
                        st.success(f"L'article '{nouvel_article}' a été ajouté avec succès.")
                    else:
                        st.error("Veuillez remplir tous les champs.")

    # ------------------------------------------
    # SECTION 3 : SORTIES DE STOCK
    # ------------------------------------------
    elif menu == "📤 Sorties Stock":
        st.title("📤 Sortie de Matériel / Ventes")
        with st.form("form_sortie"):
            article_sortie = st.selectbox("Sélectionner l'article sortant", df_stock["Article"].tolist())
            quantite_sortie = st.number_input("Quantité à retirer", min_value=1, step=1)
            valider_sortie = st.form_submit_button("Valider la sortie")

            if valider_sortie:
                qte_actuelle = df_stock.loc[df_stock["Article"] == article_sortie, "Quantité"].values[0]
                if quantite_sortie <= qte_actuelle:
                    df_stock.loc[df_stock["Article"] == article_sortie, "Quantité"] -= quantite_sortie
                    sauvegarder_stock(df_stock)
                    st.success(f"Sortie enregistrée ! -{quantite_sortie} unités pour '{article_sortie}'.")
                else:
                    st.error(f"Stock insuffisant. Quantité maximale disponible : {qte_actuelle} unités.")

    # ------------------------------------------
    # SECTION 4 : CHANGEMENT DE MOT DE PASSE
    # ------------------------------------------
    elif menu == "⚙️ Mon Compte":
        st.title("⚙️ Gestion du Compte")
        st.subheader("Changer le mot de passe")
        
        with st.form("form_changement_mdp"):
            ancien_mdp = st.text_input("Mot de passe actuel", type="password")
            nouveau_mdp = st.text_input("Nouveau mot de passe", type="password")
            confirmer_nouveau_mdp = st.text_input("Confirmer le nouveau mot de passe", type="password")
            valider_changement = st.form_submit_button("Mettre à jour le mot de passe")
            
            if valider_changement:
                if not ancien_mdp or not nouveau_mdp or not confirmer_nouveau_mdp:
                    st.error("Veuillez remplir tous les champs.")
                elif nouveau_mdp != confirmer_nouveau_mdp:
                    st.error("Le nouveau mot de passe et sa confirmation ne correspondent pas.")
                else:
                    df_users = charger_utilisateurs()
                    user_actuel = st.session_state["user_actuel"]
                    ancien_hash = hasher_mdp(ancien_mdp)
                    
                    correct_check = df_users[(df_users["Identifiant"] == user_actuel) & (df_users["Mots_de_passe"] == ancien_hash)]
                    if correct_check.empty:
                        st.error("Le mot de passe actuel est incorrect.")
                    else:
                        df_users.loc[df_users["Identifiant"] == user_actuel, "Mots_de_passe"] = hasher_mdp(nouveau_mdp)
                        sauvegarder_utilisateurs(df_users)
                        st.success("Votre mot de passe a été modifié avec succès.")
