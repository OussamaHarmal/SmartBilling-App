# 📊 SmartBilling & Analytics App

Une application de bureau complète pour la gestion des factures et l'analyse de performance des ventes, développée avec **PyQt**, **Pandas**, et **PostgreSQL**.

---

## 🧠 Fonctionnalités principales

- 📋 Gestion des factures (ajout, modification, suppression)
- 🔎 Filtres dynamiques (par date, ville, statut...)
- 📊 Page statistiques avec graphiques interactifs
- 🧾 Export PDF + Envoi par e-mail
- 🗃️ Connexion à une base de données PostgreSQL
- 🖥️ Interface moderne (PyQt)

---

## 🛠️ Technologies utilisées

- Python 🐍
- PyQt5 🎨
- Pandas 📊
- PostgreSQL 🐘
- ReportLab / FPDF 🖨️
- Matplotlib / Seaborn 📉

---

## 🧑‍💻 Installation locale

### 1. Cloner le projet

```bash
git clone https://github.com/OussamaHarmal/SmartBilling.git
cd SmartBilling
```

### 2. Créer un environnement virtuel (optionnel mais recommandé)

```bash
python -m venv env
source env/bin/activate  # sous Windows: env\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer PostgreSQL

1. Assurez-vous que PostgreSQL est installé.
2. Créez une base de données nommée `smartbilling`.
3. Exécutez le script suivant pour générer les tables nécessaires :

```sql
-- database_schema.sql
CREATE TABLE IF NOT EXISTS invoices (
    id SERIAL PRIMARY KEY,
    client_name TEXT NOT NULL,
    city TEXT NOT NULL,
    status TEXT NOT NULL,
    total_amount NUMERIC,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

4. Ajoutez vos identifiants PostgreSQL dans le fichier `config.py` :

```python
# config.py
DB_HOST = "localhost"
DB_NAME = "facturation"
DB_USER = "postgres"
DB_PASSWORD = "admin"
DB_PORT = "5432"
```

### 5. Lancer l'application

```bash
python main.py
```

---

## 📂 Arborescence du projet

```
SmartBilling/
│
├── main.py                  # Script principal PyQt
├── config.py                # Connexion PostgreSQL
├── requirements.txt         # Dépendances
├── database_schema.sql      # Script de création DB
├── ui/                      # Fichiers .ui (PyQt Designer)
├── data/                    # CSV ou autres données
├── assets/                  # Icônes, logos, etc.
├── .gitattributes           # Corrige la langue sur GitHub
└── README.md
```

---

## 📌 Auteurs

Développé par **Oussama Harmal** & **Abdelatif Boufouss** dans le cadre du PFE 2025.

---

## 🪪 Licence

Ce projet est **privé**. Toute utilisation, modification ou distribution est interdite sans l'autorisation des auteurs.

---

## 🤝 Contact

- 📧 Email : oussamaharmal2@gmail.com
- 📍 Ville : Casablanca, Maroc
- 🔗 GitHub : [OussamaHarmal](https://github.com/OussamaHarmal)