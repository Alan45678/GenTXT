
# GenTXT - Utilitaire de Concaténation de Fichiers

GenTXT est un outil simple avec une interface graphique (GUI) développé en Python (utilisant Tkinter) qui permet de scanner un répertoire, d'en générer une représentation textuelle de l'arborescence, et de concaténer le contenu des fichiers texte sélectionnés dans un unique fichier de sortie. Il offre une configuration flexible pour exclure certains fichiers, dossiers ou extensions.

## Fonctionnalités

*   **Interface Graphique Simple:** Facile à utiliser grâce à une interface construite avec Tkinter.
*   **Sélection de Répertoire Source:** Permet de choisir le dossier à analyser.
*   **Sélection de Fichier de Sortie:** Permet de choisir où enregistrer le résultat concaténé.
*   **Génération d'Arborescence:** Crée une vue textuelle de la structure du répertoire choisi au début du fichier de sortie.
*   **Concaténation de Contenu:** Ajoute le contenu des fichiers texte trouvés (et non exclus) au fichier de sortie.
*   **Configuration d'Exclusions:** Utilise un fichier `.concat_config.json` dans le répertoire source pour définir finement :
    *   Les fichiers, dossiers et extensions à exclure de l'**arborescence**.
    *   Les fichiers, dossiers et extensions dont le **contenu** ne doit pas être inclus.
*   **Configuration par Défaut:** Applique des exclusions par défaut raisonnables si aucun fichier `.concat_config.json` n'est trouvé.
*   **Éditeur de Configuration Intégré:** Permet de créer ou modifier le fichier `.concat_config.json` directement depuis l'application pour le dossier sélectionné.
*   **Gestion des Erreurs:** Gère les fichiers potentiellement binaires (en ignorant leur contenu) et les erreurs d'encodage (UTF-8 est privilégié).
*   **Packagé en Exécutable:** Peut être facilement compilé en un exécutable autonome (`.exe` sous Windows) grâce à PyInstaller.

## Prérequis (pour exécuter depuis les sources)

*   Python 3.x
*   Tkinter (généralement inclus avec Python)

## Utilisation

### Option 1: Utiliser l'exécutable (recommandé)

1.  Téléchargez (si disponible) ou générez le fichier `GenTXT.exe`.
2.  Double-cliquez sur `GenTXT.exe` pour lancer l'application.
3.  Cliquez sur "**Démarrer la Concaténation**".
4.  Sélectionnez le **dossier source** que vous souhaitez analyser et concaténer.
5.  Choisissez l'emplacement et le nom du **fichier de sortie** (par exemple, `rapport_projet.txt`).
6.  L'application va traiter les fichiers et afficher un message de succès une fois terminé. Le fichier de sortie contiendra l'arborescence suivie du contenu des fichiers inclus.

### Option 2: Exécuter depuis les sources

1.  Assurez-vous d'avoir Python 3 installé.
2.  Clonez ou téléchargez le contenu de ce répertoire.
3.  Ouvrez un terminal ou une invite de commande dans le répertoire `gentxt`.
4.  Exécutez la commande : `python main.py`
5.  Suivez les étapes 3 à 6 de l'Option 1.

## Configuration (`.concat_config.json`)

Pour personnaliser les éléments exclus lors de la génération, vous pouvez placer un fichier nommé `.concat_config.json` à la racine du **dossier source** que vous analysez.

*   **Création/Édition Facile:** Utilisez le bouton "**Créer / Modifier Configuration**" dans l'application. Sélectionnez le dossier pour lequel vous voulez gérer la configuration, et l'éditeur s'ouvrira.
*   **Structure du Fichier:** Le fichier est au format JSON et contient les clés suivantes (toutes attendent une liste de chaînes de caractères) :
    *   `exclude_tree_files`: Noms de fichiers exacts à exclure de l'arborescence.
    *   `exclude_tree_extensions`: Extensions (avec le point, ex: `.log`) à exclure de l'arborescence.
    *   `exclude_tree_dirs`: Noms de dossiers exacts à exclure de l'arborescence (et de leur contenu récursif dans l'arbre).
    *   `exclude_content_files`: Noms de fichiers exacts dont le contenu ne doit pas être inclus.
    *   `exclude_content_extensions`: Extensions (avec le point, ex: `.png`) dont le contenu ne doit pas être inclus.
    *   `exclude_content_dirs`: Noms de dossiers exacts dont le contenu (et celui de leurs sous-dossiers) ne doit pas être inclus.

*   **Exemple `.concat_config.json`:**
    ```json
    {
        "exclude_tree_files": [
            "secret.txt",
            "temp_notes.md"
        ],
        "exclude_tree_extensions": [
            ".log",
            ".tmp"
        ],
        "exclude_tree_dirs": [
            ".git",
            "node_modules",
            "__pycache__",
            "build",
            "dist"
        ],
        "exclude_content_files": [
            "large_data.bin",
            "config.json"
        ],
        "exclude_content_extensions": [
            ".exe", ".dll", ".so", ".o", ".a", ".lib",
            ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".ico",
            ".pdf", ".zip", ".gz", ".tar", ".rar", ".7z",
            ".mp3", ".wav", ".mp4", ".avi", ".mkv",
            ".pyc", ".class", ".jar", ".war", ".ear",
            ".csv", ".xls", ".xlsx", ".ods", ".odt"
        ],
        "exclude_content_dirs": [
            ".git",
            "node_modules",
            "__pycache__",
            "assets",
            "docs",
            "build",
            "dist"
        ]
    }
    ```

*   **Comportement par Défaut:** Si `.concat_config.json` est absent, invalide ou manque certaines clés, des valeurs par défaut sont utilisées (voir `DEFAULT_EXCLUDE_*` dans `main.py`).

## Génération de l'exécutable

Si vous souhaitez créer un fichier `GenTXT.exe` autonome à partir des sources :

1.  **Installez PyInstaller:**
    ```bash
    pip install pyinstaller
    ```
2.  **Naviguez vers le répertoire `gentxt`** dans votre terminal.
3.  **Exécutez la commande** (fournie dans `memo commande.txt` et définie dans `GenTXT.spec`):
    ```bash
    pyinstaller --onefile --noconsole --name GenTXT main.py
    ```
    *   `--onefile`: Crée un seul fichier exécutable.
    *   `--noconsole`: N'ouvre pas de fenêtre de console lors de l'exécution de l'application GUI.
    *   `--name GenTXT`: Définit le nom de l'exécutable.

4.  L'exécutable `GenTXT.exe` sera généré dans le sous-dossier `dist`.

## Structure du Projet

```
gentxt/
├── GenTXT.spec         # Fichier de configuration pour PyInstaller
├── main.py             # Script principal contenant la logique et l'interface graphique
└── memo commande.txt   # Mémo avec la commande de build PyInstaller
```

(Le fichier `.concat_config.json` n'est pas dans le code source mais est généré/utilisé dans les répertoires cibles).
```




