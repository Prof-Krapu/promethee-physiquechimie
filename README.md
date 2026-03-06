# 🧪 Prométhée — Édition Physique-Chimie

**Assistant IA spécialisé pour l'enseignement de la Physique-Chimie** — Fork du projet Prométhée adapté pour opérer via Telegram. Interagit avec les API Albert (IA souveraine) et OpenRouter (Modèles de vision pour les schémas complexes).

---

## ✨ Fonctionnalités clés

- 💬 **Bot Telegram interactif** : Envoi de messages, correction de copies via photos, génération de scripts et de documents.
- 📸 **Correction par lots (Batching)** : Prenez 4, 5 ou 6 photos d'une même copie, le bot les assemble après un délai de 30 secondes et génère une correction globale avec une note normalisée sur 20.
- 👁️ **Vision Scientifique Avancée** : Intégration de Qwen3-VL-235B (via OpenRouter) pour lire de l'écriture manuscrite et analyser des circuits électriques, des forces, ou des mécanismes réactionnels.
- 📦 **Envoi multi-formats** : Le bot peut générer et vous renvoyer sur Telegram plus de 30 types de fichiers (`.py`, `.pdf`, `.docx`, `.xlsx`, `.html`, etc.).
- 📐 **Conversion LaTeX intégrée** : Génération de PDF esthétiques ou conversion des formules en symboles Unicode lisibles directement dans l'interface Telegram.
- 🛠️ **Outils spécifiques intégrés** :
  - `physics_tools` : Constantes fondamentales (NIST / CODATA)
  - `chemistry_tools` : Base de données moléculaire (PubChem)
  - `curriculum_tools` : Consultations des programmes officiels (BO, Eduscol)
  - `lms_tools` : Export de quiz au format Moodle XML

---

## 🚀 Installation & Déploiement

L'application est conçue pour fonctionner de manière autonome sur un serveur ou un poste local (testé sous **Linux** et **macOS**).

### 1. Prérequis Système

Vous devez avoir Python 3.10 ou supérieur installé sur votre machine.

**Sous Linux (Ubuntu/Debian) :**
```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip texlive-full
```
*(Note : `texlive-full` est lourd, mais garantit que tous les packages LaTeX comme `amsmath` ou `babel` sont présents pour la génération des PDF).*

**Sous macOS (via Homebrew) :**
```bash
brew install python cmake
brew install --cask mactex-no-gui
```
*(Note : Mactex est requis pour compiler les réponses de l'IA en fichiers PDF).*

### 2. Cloner et préparer l'environnement

```bash
# Cloner ce dépôt (Fork Physique-Chimie)
git clone https://github.com/Prof-Krapu/promethee-physiquechimie.git
cd promethee-physiquechimie

# Créer un environnement virtuel isolé
python3 -m venv .venv

# Activer l'environnement
# -> Sous Linux ou macOS :
source .venv/bin/activate

# Installer les dépendances Python
pip install -r requirements.txt
```

### 3. Configuration des Clés API

Le bot nécessite des accès à Telegram, à Albert (ou OpenAI compatible), et à OpenRouter pour la Vision.

```bash
# Copier le modèle de configuration
cp .env.example .env

# Éditer le fichier avec votre éditeur favori (nano, vim, VSCode...)
nano .env
```

Dans ce fichier `.env`, vous devez renseigner :
- `TELEGRAM_TOKEN` : Le jeton fourni par BotFather sur Telegram.
- `OPENAI_API_KEY` : Votre clé API (Albert API de l'État, ou OpenAI).
- `OPENAI_BASE_URL` : L'URL du serveur (ex: `https://albert.api.etalab.gouv.fr/v1`).
- `OPENROUTER_API_KEY` : Clé API OpenRouter pour le modèle de vision (nécessaire pour la correction de copies).

### 4. Lancement du Bot

Assurez-vous que l'environnement virtuel est activé, puis lancez le point d'entrée Telegram :

```bash
python3 main_telegram.py
```

Le terminal affichera `Application started`. Le bot est maintenant à l'écoute de vos messages sur Telegram !

---

## 🛠️ Utilisation courante sur Telegram

*   **Dialogue classique** : Posez des questions de cours ou demandez de générer des exercices.
*   **Correction de copie** : Envoyez une photo de la copie d'un élève. Le bot attendra 30 secondes pour voir si vous envoyez d'autres pages (photos suivantes) à la suite. Il analysera ensuite le lot complet.
*   **Création de fichiers** : Demandez explicitement "Crée un script python qui trace un circuit RC". L'IA écrira le fichier sur le disque de la machine hôte et vous l'enverra en pièce jointe.

---

## 📄 Informations

*Consultez le fichier `README_IMPLEMENTATIONS.md` pour un détail complet de toutes les modifications techniques apportées par rapport au projet Prométhée original.*

Licence : GNU Affero General Public License v3.0 (AGPL-3.0)
Auteur de la surcouche Physique-Chimie : Prof-Krapu (2026)
Auteur original : Pierre Couget
