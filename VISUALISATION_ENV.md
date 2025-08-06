# Mise en place de l'environnement de visualisation

Ce guide explique comment préparer un environnement Python pour exécuter la simulation avec l'interface Pygame.

## 1. Pré-requis

- Python 3.9 ou plus récent
- `git` pour récupérer le dépôt
- Un affichage graphique (ou `SDL_VIDEODRIVER=dummy` pour un environnement sans écran)

## 2. Installation automatique

Exécutez les commandes suivantes à la racine du projet pour créer un environnement
virtuel et installer les dépendances. La commande d'activation dépend de votre
plateforme :

```bash
python -m venv .venv

# Sous Linux/macOS
source .venv/bin/activate
# Sous Windows PowerShell
.\.venv\Scripts\Activate.ps1
# Sous Windows CMD
.\.venv\Scripts\activate.bat

pip install --upgrade pip
pip install -r requirements.txt
```

Ces commandes peuvent être copiées/collées successivement dans le terminal.

## 3. Vérification des dépendances

Lancer les tests unitaires pour s'assurer que l'installation est correcte :

```bash
pytest
```

## 4. Lancer une visualisation d'exemple

Pour voir la ferme s'animer dans une fenêtre Pygame :

```bash
# Dans le terminal où l'environnement virtuel est activé
unset SDL_VIDEODRIVER  # seulement si vous l'aviez défini précédemment
python run_farm.py
```

Une fenêtre Pygame apparaît avec trois fermiers qui vivent leur journée.

## 5. Pour aller plus loin

Vous pouvez regrouper les commandes d'installation dans un script shell (`setup_env.sh`) et l'exécuter d'un seul coup :

```bash
bash setup_env.sh
```

(adaptez le script à vos besoins pour automatiser la configuration sur vos machines).

