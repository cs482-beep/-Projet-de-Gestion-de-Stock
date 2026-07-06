import os
import pandas as pd
import plotly.express as px
import streamlit as st

# ==========================================
# CONFIGURATION DE LA PAGE & THÈME
# ==========================================
st.set_page_config(
    page_title="G-Stock | Système de Gestion", page_icon="📦", layout="wide"
)

# Style CSS personnalisé (Thème Bleu Nuit & Blanc)
st.markdown(
    """
    <style>
        /* Couleurs principales */
        :root {
            --primary-color: #0A192F;
            --secondary-color: #172A45;
            --accent-color: #3066BE;
            --text-color: #F4F6F9;
        }
        
        /* Personnalisation des boutons */
        .stButton>button {
            background-color: #3066BE !important;
            color: white !important;
            border-radius: 6px !important;
            border: none !important;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #0A192F !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        /* En-têtes de sections */
        h1, h2, h3 {
            color: #0A192F !important;
            font-family: 'Segoe UI', sans-serif;
        }
        
        /* Cartes de statistiques */
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

CSV_FILE = "donnees_stock.csv"


# ==========================================
# FONCTIONS DE GESTION DES DONNÉES (CSV)
# ==========================================
def charger_donnees():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        # Création d'un jeu de données initial si le fichier n'existe pas
        data = {
            "ID": [101, 102, 103, 104],
            "Article": [
                "Capteur Ultrason",
                "Carte Arduino Uno",
                "Module GPS GY-NEO6MV2",
                "Routeur 4G LTE",
            ],
            "Catégorie": [
                "Électronique",
                "Microcontrôleurs",
                "IoT",
                "Réseau",
            ],
            "Quantité": [50, 30, 15, 10],
            "Prix_Unitaire_DH": [25, 85, 120, 450],
        }
        df = pd.DataFrame(data)
        df.to_csv(CSV_FILE, index=False)
        return df


def sauvegarder_donnees(df):
    df.to_csv(CSV_FILE, index=False)


# ==========================================
# GESTION DE L'AUTHENTIFICATION
# ==========================================
if "connecte" not in st.session_state:
    st.session_state["connecte"] = False

# Écran de connexion
if not st.session_state["connecte"]:
    col1, col2, col3 = st.columns([1, 1.5, 1])

    with col2:
        st.write("<br><br>", unsafe_allow_html=True)
        st.markdown(
            "<h2 style='text-align: center; color: #0A192F;'>🔐 Connexion | G-Stock</h2>",
            unsafe_allow_html=True,
        )

        with st.form(key="login_form"):
            identifiant = st.text_input("Identifiant / Login")
            mot_de_passe = st.text_input("Mot de passe", type="password")
            bouton_connexion = st.form_submit_button("Se connecter")

            if bouton_connexion:
                # Identifiants professionnels par défaut
                if identifiant == "admin" and mot_de_passe == "ENSA2026":
                    st.session_state["connecte"] = True
                    st.rerun()
                else:
                    st.error("Identifiant ou mot de passe incorrect.")

# ==========================================
# APPLICATION PRINCIPALE (APRÈS CONNEXION)
# ==========================================
else:
    df_stock = charger_donnees()

    # Barre latérale (Sidebar) de navigation
    st.sidebar.markdown(
        "<h2 style='color: white; text-align: center;'>📦 Navigation</h2>",
        unsafe_allow_html=True,
    )
    menu = st.sidebar.radio(
        "Sélectionnez une section :",
        ["📊 Tableau de Bord", "📥 Entrées Stock", "📤 Sorties Stock"],
    )

    st.sidebar.write("---")
    if st.sidebar.button("Se déconnecter"):
        st.session_state["connecte"] = False
        st.rerun()

    # ------------------------------------------
    # SECTION 1 : TABLEAU DE BORD (DASHBOARD)
    # ------------------------------------------
    if menu == "📊 Tableau de Bord":
        st.title("📊 Tableau de Bord des Statistiques")
        st.write("Aperçu en temps réel de l'état de votre stock.")

        # Calcul des indicateurs clés (KPIs)
        total_articles = df_stock["Quantité"].sum()
        valeur_totale = (
            df_stock["Quantité"] * df_stock["Prix_Unitaire_DH"]
        ).sum()
        references_distinctes = df_stock["Article"].nunique()

        # Affichage des cartes KPI
        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            st.markdown(
                f"<div class='metric-card'><h3>📦 Total Articles</h3><h2>{total_articles} unités</h2></div>",
                unsafe_allow_html=True,
            )
        with kpi2:
            st.markdown(
                f"<div class='metric-card'><h3>💰 Valeur Stock</h3><h2>{valeur_totale:,.2f} DH</h2></div>",
                unsafe_allow_html=True,
            )
        with kpi3:
            st.markdown(
                f"<div class='metric-card'><h3>🔑 Références</h3><h2>{references_distinctes} Réfs</h2></div>",
                unsafe_allow_html=True,
            )

        # Graphiques
        st.write("<br>", unsafe_allow_html=True)
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.subheader("Niveau de stock par Article")
            fig_bar = px.bar(
                df_stock,
                x="Article",
                y="Quantité",
                color="Quantité",
                color_continuous_scale=["#3066BE", "#0A192F"],
                template="plotly_white",
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_chart2:
            st.subheader("Répartition par Catégorie")
            fig_pie = px.pie(
                df_stock,
                names="Catégorie",
                values="Quantité",
                color_discrete_sequence=["#0A192F", "#172A45", "#3066BE"],
            )
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig_pie, use_container_width=True)

        # Vue d'ensemble du tableau de données
        st.subheader("📋 État Actuel du Stock")
        st.dataframe(df_stock, use_container_width=True)

    # ------------------------------------------
    # SECTION 2 : ENTRÉES DE STOCK
    # ------------------------------------------
    elif menu == "📥 Entrées Stock":
        st.title("📥 Réception de Marchandise (Entrées)")
        st.write("Ajoutez un nouvel article ou augmentez la quantité d'un article existant.")

        choix_action = st.radio(
            "Type d'entrée :",
            ["Réapprovisionner un article existant", "Ajouter une nouvelle référence"],
        )

        if choix_action == "Réapprovisionner un article existant":
            with st.form("form_reelement"):
                article_selectionne = st.selectbox(
                    "Choisir l'article", df_stock["Article"].tolist()
                )
                quantite_ajoutee = st.number_input(
                    "Quantité reçue", min_value=1, step=1
                )
                valider_entree = st.form_submit_button("Valider l'entrée")

                if valider_entree:
                    df_stock.loc[
                        df_stock["Article"] == article_selectionne, "Quantité"
                    ] += quantite_ajoutee
                    sauvegarder_donnees(df_stock)
                    st.success(
                        f"Stock mis à jour ! +{quantite_ajoutee} pour '{article_selectionne}'."
                    )

        else:
            with st.form("form_nouvel_article"):
                nouveau_id = st.number_input(
                    "ID de l'article",
                    min_value=int(df_stock["ID"].max() + 1),
                    step=1,
                )
                nouvel_article = st.text_input("Nom de l'article")
                nouvelle_categorie = st.text_input("Catégorie")
                nouvelle_qte = st.number_input(
                    "Quantité initiale", min_value=1, step=1
                )
                nouveau_prix = st.number_input(
                    "Prix Unitaire (DH)", min_value=0.0, format="%.2f"
                )
                valider_ajout = st.form_submit_button("Ajouter au catalogue")

                if valider_ajout:
                    if nouvel_article and nouvelle_categorie:
                        nouvel_row = {
                            "ID": nouveau_id,
                            "Article": nouvel_article,
                            "Catégorie": nouvelle_categorie,
                            "Quantité": nouvelle_qte,
                            "Prix_Unitaire_DH": nouveau_prix,
                        }
                        df_stock = pd.concat(
                            [df_stock, pd.DataFrame([nouvel_row])],
                            ignore_index=True,
                        )
                        sauvegarder_donnees(df_stock)
                        st.success(
                            f"L'article '{nouvel_article}' a été ajouté avec succès."
                        )
                    else:
                        st.error("Veuillez remplir tous les champs.")

    # ------------------------------------------
    # SECTION 3 : SORTIES DE STOCK
    # ------------------------------------------
    elif menu == "📤 Sorties Stock":
        st.title("📤 Sortie de Matériel / Ventes")
        st.write("Enregistrez une sortie ou une livraison de matériel.")

        with st.form("form_sortie"):
            article_sortie = st.selectbox(
                "Sélectionner l'article sortant", df_stock["Article"].tolist()
            )
            quantite_sortie = st.number_input(
                "Quantité à retirer", min_value=1, step=1
            )
            valider_sortie = st.form_submit_button("Valider la sortie")

            if valider_sortie:
                qte_actuelle = df_stock.loc[
                    df_stock["Article"] == article_sortie, "Quantité"
                ].values[0]

                if quantite_sortie <= qte_actuelle:
                    df_stock.loc[
                        df_stock["Article"] == article_sortie, "Quantité"
                    ] -= quantite_sortie
                    sauvegarder_donnees(df_stock)
                    st.success(
                        f"Sortie enregistrée ! -{quantite_sortie} unités pour '{article_sortie}'."
                    )
                else:
                    st.error(
                        f"Stock insuffisant. Quantité maximale disponible : {qte_actuelle} unités."
                    )
