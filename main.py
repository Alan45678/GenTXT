
import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, Toplevel, Text, Button, Scrollbar, Frame
import json
from pathlib import Path

# --- Configuration par défaut ---
# Utilisées si aucun fichier .concat_config.json n'est trouvé
DEFAULT_EXCLUDE_TREE_EXTENSIONS = {".pyc", ".json", ".pb"}
DEFAULT_EXCLUDE_TREE_DIRS = {".git", "__pycache__", "node_modules"} # node_modules exclu par défaut de l'arbre ET du contenu
DEFAULT_EXCLUDE_TREE_FILES = set()

DEFAULT_EXCLUDE_CONTENT_EXTENSIONS = {".csv", ".xls", ".xlsx", ".ods", ".odt", ".md", ".pyc", ".json", ".pb", ".log", ".svg", ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".ico", ".pdf", ".zip", ".gz", ".tar", ".rar", ".7z", ".exe", ".dll", ".so", ".o", ".a", ".lib", ".class", ".jar", ".war", ".ear", ".mp3", ".wav", ".ogg", ".mp4", ".avi", ".mkv", ".mov"}
DEFAULT_EXCLUDE_CONTENT_DIRS = {".git", "__pycache__", "node_modules"}
DEFAULT_EXCLUDE_CONTENT_FILES = set()

CONFIG_FILENAME = ".concat_config.json"

# --- Fonctions de Configuration ---

def create_default_config():
    """Crée un dictionnaire représentant la configuration par défaut."""
    return {
        "exclude_tree_files": list(DEFAULT_EXCLUDE_TREE_FILES),
        "exclude_tree_extensions": list(DEFAULT_EXCLUDE_TREE_EXTENSIONS),
        "exclude_tree_dirs": list(DEFAULT_EXCLUDE_TREE_DIRS),
        "exclude_content_files": list(DEFAULT_EXCLUDE_CONTENT_FILES),
        "exclude_content_extensions": list(DEFAULT_EXCLUDE_CONTENT_EXTENSIONS),
        "exclude_content_dirs": list(DEFAULT_EXCLUDE_CONTENT_DIRS),
    }

def load_config(directory):
    """Charge la configuration depuis .concat_config.json dans le dossier spécifié."""
    config_path = os.path.join(directory, CONFIG_FILENAME)
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                loaded_cfg = json.load(f)
                # S'assurer que toutes les clés existent, utiliser les valeurs par défaut sinon
                default_cfg = create_default_config()
                config = default_cfg.copy() # Commence avec les défauts
                # Met à jour avec les valeurs chargées, si elles existent et sont des listes
                for key in default_cfg:
                    if key in loaded_cfg and isinstance(loaded_cfg[key], list):
                        config[key] = loaded_cfg[key]
                    elif key in loaded_cfg:
                        print(f"Avertissement: La clé '{key}' dans {CONFIG_FILENAME} n'est pas une liste valide, utilisation de la valeur par défaut.")
                # Convertir les listes en sets pour des recherches rapides
                for key in config:
                    config[key] = set(config[key]) # Utilise des sets pour l'efficacité
                print(f"Configuration chargée depuis {config_path}")
                return config
        except json.JSONDecodeError as e:
            messagebox.showerror("Erreur de Configuration", f"Erreur lors de la lecture de {CONFIG_FILENAME}: {e}\nUtilisation de la configuration par défaut.")
            config = create_default_config()
            for key in config: # Convertir en sets
                config[key] = set(config[key])
            return config
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur inattendue lors du chargement de la configuration: {e}\nUtilisation de la configuration par défaut.")
            config = create_default_config()
            for key in config: # Convertir en sets
                config[key] = set(config[key])
            return config
    else:
        print("Aucun fichier .concat_config.json trouvé. Utilisation de la configuration par défaut.")
        config = create_default_config()
        for key in config: # Convertir en sets
             config[key] = set(config[key])
        return config

def save_config(directory, config_data):
    """Sauvegarde la configuration (dictionnaire) dans .concat_config.json."""
    config_path = os.path.join(directory, CONFIG_FILENAME)
    try:
        # Convertir les sets en listes pour la sérialisation JSON
        config_to_save = {}
        for key, value in config_data.items():
            config_to_save[key] = sorted(list(value)) # Tri pour la lisibilité

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_to_save, f, indent=4)
        return True
    except Exception as e:
        messagebox.showerror("Erreur de Sauvegarde", f"Impossible de sauvegarder {config_path}: {e}")
        return False

# --- Fonctions Logiques Modifiées ---

def is_excluded(name, path, config, exclude_type):
    """Vérifie si un fichier/dossier est exclu selon la configuration."""
    base_name = os.path.basename(name)
    _, ext = os.path.splitext(name)
    ext_lower = ext.lower()

    if exclude_type == "tree":
        if base_name in config.get("exclude_tree_files", set()):
            return True
        if ext_lower in config.get("exclude_tree_extensions", set()):
            return True
        # Pour les dossiers dans l'arbre, on vérifie juste le nom du dossier
        if os.path.isdir(path) and base_name in config.get("exclude_tree_dirs", set()):
             return True
        # Vérifier si un dossier parent est dans exclude_tree_dirs n'est pas standard pour `tree`
        # mais on pourrait l'ajouter si nécessaire. Normalement `tree` n'exclut que par nom direct.

    elif exclude_type == "content":
        if base_name in config.get("exclude_content_files", set()):
            return True
        if ext_lower in config.get("exclude_content_extensions", set()):
            return True
        # Vérifier si le chemin est DANS un dossier exclu (pour le contenu)
        parts = Path(path).parts
        excluded_dirs = config.get("exclude_content_dirs", set())
        for part in parts:
            if part in excluded_dirs:
                return True

    return False

def get_all_files(directory, config):
    """Récupère tous les fichiers dont le contenu doit être inclus."""
    for root, dirs, files in os.walk(directory, topdown=True):
        # Filtrer les dossiers à ne PAS parcourir pour le contenu
        dirs[:] = [d for d in dirs if not is_excluded(d, os.path.join(root, d), config, "content")]

        for name in files:
            full_path = os.path.join(root, name)
            # Vérifier si le fichier lui-même ou son extension est exclu pour le contenu
            if not is_excluded(name, full_path, config, "content"):
                 # Vérification supplémentaire pour s'assurer qu'on n'est pas dans un dossier exclu (double vérification utile)
                if not any(part in config.get("exclude_content_dirs", set()) for part in Path(full_path).parent.parts):
                    yield full_path


def read_file_content(file_path):
    """Lit le contenu d’un fichier texte de façon sécurisée."""
    try:
        # Détecter si c'est probablement un fichier binaire (heuristique simple)
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            if b'\x00' in chunk:
                return f"[Contenu Binaire ignoré pour {os.path.basename(file_path)}]\n"
        # Si ce n'est pas binaire, essayer de lire en UTF-8
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
         return f"[Erreur d'encodage (non-UTF-8) lors de la lecture de {os.path.basename(file_path)}]\n"
    except Exception as e:
        return f"[Erreur lors de la lecture de {os.path.basename(file_path)} : {e}]\n"

def write_directory_tree(directory, output_file, config):
    """Écrit l'arborescence du dossier au format 'tree' dans le fichier de sortie."""
    output_file.write("# === Arborescence du dossier ===\n\n")

    exclude_tree_dirs = config.get("exclude_tree_dirs", set())
    exclude_tree_files = config.get("exclude_tree_files", set())
    exclude_tree_extensions = config.get("exclude_tree_extensions", set())

    def walk_dir(current_path, prefix=""):
        try:
            # Liste les entrées et filtre immédiatement celles à exclure
            entries = []
            for entry in os.listdir(current_path):
                 entry_path = os.path.join(current_path, entry)
                 _, ext = os.path.splitext(entry)

                 is_dir = os.path.isdir(entry_path)

                 # Exclusions spécifiques à l'arbre
                 if entry in exclude_tree_files: continue
                 if ext.lower() in exclude_tree_extensions: continue
                 if is_dir and entry in exclude_tree_dirs: continue
                 if entry == CONFIG_FILENAME: continue # Exclure le fichier config lui-même de l'arbre

                 entries.append(entry)
            entries.sort()

        except Exception as e:
            output_file.write(f"{prefix}└── [Erreur lecture dossier: {e}]\n")
            return

        for index, entry in enumerate(entries):
            full_path = os.path.join(current_path, entry)
            is_dir = os.path.isdir(full_path)
            connector = "└── " if index == len(entries) - 1 else "├── "
            output_file.write(f"{prefix}{connector}{entry}\n")
            if is_dir:
                # Ne pas descendre dans les dossiers exclus de l'arbre
                if entry not in exclude_tree_dirs:
                    extension = "    " if index == len(entries) - 1 else "│   "
                    walk_dir(full_path, prefix + extension)

    base_name = os.path.basename(os.path.abspath(directory))
    output_file.write(f"{base_name}\n")
    walk_dir(directory)
    output_file.write("\n")

def write_file_contents(files, output_file, source_directory):
    """Écrit le contenu de chaque fichier dans le fichier de sortie, précédé de son chemin relatif."""
    output_file.write("\n# === Contenu des fichiers ===\n")
    for file_path in files:
        # Calculer le chemin relatif pour l'affichage
        relative_path = os.path.relpath(file_path, source_directory)
        output_file.write(f"\n--- Fichier : {relative_path} ---\n")
        content = read_file_content(file_path)
        output_file.write(content)
        # Assurer une nouvelle ligne à la fin du contenu du fichier si absent
        if content and not content.endswith('\n'):
            output_file.write("\n")

def concat_files(source_directory, output_path):
    """Point d’entrée principal du script."""
    # Charger la configuration spécifique à ce dossier
    config = load_config(source_directory)

    # Obtenir la liste des fichiers dont le contenu doit être concaténé
    files_to_concat = sorted(list(get_all_files(source_directory, config)))

    with open(output_path, "w", encoding="utf-8") as out_file:
        # Écrire l'arborescence en utilisant les exclusions de l'arbre
        write_directory_tree(source_directory, out_file, config)
        # Écrire le contenu des fichiers sélectionnés (déjà filtrés par get_all_files)
        write_file_contents(files_to_concat, out_file, source_directory)

# --- Fonctions UI ---

def select_directory(title="Sélectionner un dossier"):
    """Ouvre une boîte de dialogue pour sélectionner un dossier."""
    return filedialog.askdirectory(title=title)

def select_output_file():
    """Ouvre une boîte de dialogue pour sélectionner le fichier de sortie."""
    return filedialog.asksaveasfilename(defaultextension=".txt",
                                       filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
                                       title="Sélectionner le fichier de sortie")

def edit_config_ui(directory):
    """Ouvre une fenêtre pour éditer le fichier de configuration."""
    config_path = os.path.join(directory, CONFIG_FILENAME)
    current_config = {}

    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                # Charger tel quel pour l'édition
                current_config = json.load(f)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de lire {CONFIG_FILENAME}: {e}")
            # Proposer de créer un fichier par défaut même en cas d'erreur de lecture
            if messagebox.askyesno("Configuration", f"Le fichier {CONFIG_FILENAME} est illisible ou corrompu.\nVoulez-vous créer une configuration par défaut ?"):
                 current_config = create_default_config()
                 # Convertir en listes pour l'affichage initial
                 for key in current_config: current_config[key] = list(current_config[key])
            else:
                return # Ne rien faire si l'utilisateur refuse
    else:
        # Si le fichier n'existe pas, proposer de le créer
        if messagebox.askyesno("Configuration", f"Le fichier {CONFIG_FILENAME} n'existe pas dans {directory}.\nVoulez-vous le créer avec les valeurs par défaut ?"):
             current_config = create_default_config()
             # Convertir en listes pour l'affichage initial
             for key in current_config: current_config[key] = list(current_config[key])
        else:
            return # Ne rien faire si l'utilisateur refuse

    # Créer la fenêtre d'édition
    editor_window = Toplevel()
    editor_window.title(f"Éditer {CONFIG_FILENAME}")
    editor_window.geometry("600x500")

    text_frame = Frame(editor_window)
    text_frame.pack(pady=10, padx=10, fill="both", expand=True)

    text_widget = Text(text_frame, wrap="word", undo=True)
    # Convertir le dictionnaire en JSON formaté pour l'affichage
    try:
        # S'assurer que c'est un dict avant de dump (cas d'erreur de chargement)
        if isinstance(current_config, dict):
             # Convertir les sets potentiels en listes avant dump
             config_to_display = {}
             for key, value in current_config.items():
                 if isinstance(value, set):
                     config_to_display[key] = sorted(list(value))
                 else:
                     config_to_display[key] = value # Garder tel quel si déjà liste/autre
             text_widget.insert("1.0", json.dumps(config_to_display, indent=4))
        else:
             # Si current_config n'est pas un dict (erreur précédente), afficher un message
             text_widget.insert("1.0", "# Erreur lors du chargement/création de la configuration.\n# Veuillez corriger ou utiliser les valeurs par défaut.")

    except Exception as e:
         text_widget.insert("1.0", f"# Erreur interne lors de la préparation de l'affichage : {e}")


    # Ajouter des barres de défilement
    scrollbar_y = Scrollbar(text_frame, command=text_widget.yview)
    scrollbar_x = Scrollbar(text_frame, command=text_widget.xview, orient="horizontal")
    text_widget.config(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set, wrap="none") # wrap="none" pour X scroll

    scrollbar_y.pack(side="right", fill="y")
    scrollbar_x.pack(side="bottom", fill="x")
    text_widget.pack(side="left", fill="both", expand=True)


    def save_and_close():
        content = text_widget.get("1.0", tk.END)
        try:
            # Valider que le contenu est du JSON valide
            config_data_from_text = json.loads(content)
            if not isinstance(config_data_from_text, dict):
                raise ValueError("Le contenu JSON doit être un objet (dictionnaire).")

            # Convertir les listes en sets pour l'utilisation interne avant sauvegarde
            config_for_saving = {}
            default_keys = create_default_config().keys()
            for key in default_keys:
                # Utilise .get pour éviter KeyError si la clé manque dans le JSON édité
                value = config_data_from_text.get(key, [])
                if not isinstance(value, list):
                     messagebox.showwarning("Format Invalide", f"La clé '{key}' doit contenir une liste. Utilisation d'une liste vide.")
                     value = []
                config_for_saving[key] = set(value) # Convertit en set pour la logique interne

            if save_config(directory, config_for_saving): # save_config reconvertira en listes triées
                messagebox.showinfo("Succès", f"{CONFIG_FILENAME} sauvegardé avec succès.", parent=editor_window)
                editor_window.destroy()
            # else: l'erreur est affichée dans save_config

        except json.JSONDecodeError as e:
            messagebox.showerror("Erreur JSON", f"Le format du texte n'est pas valide JSON: {e}", parent=editor_window)
        except ValueError as e:
             messagebox.showerror("Erreur de Structure", str(e), parent=editor_window)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur inattendue lors de la sauvegarde: {e}", parent=editor_window)

    def cancel_and_close():
        editor_window.destroy()

    button_frame = Frame(editor_window)
    button_frame.pack(pady=10)

    save_button = Button(button_frame, text="Enregistrer et Fermer", command=save_and_close)
    save_button.pack(side="left", padx=10)

    cancel_button = Button(button_frame, text="Annuler", command=cancel_and_close)
    cancel_button.pack(side="left", padx=10)

    editor_window.transient(editor_window.master) # Garde la fenêtre au premier plan
    editor_window.grab_set() # Bloque l'interaction avec la fenêtre principale
    editor_window.wait_window() # Attend que la fenêtre d'édition soit fermée


def create_or_edit_config():
    """Demande à l'utilisateur de choisir un dossier et ouvre l'éditeur de config."""
    directory = select_directory("Sélectionner le dossier pour la configuration")
    if not directory:
        # messagebox.showinfo("Annulé", "Aucun dossier sélectionné.")
        return
    edit_config_ui(directory)

def start_process():
    """Démarre le processus après que l'utilisateur ait sélectionné les fichiers."""
    source_directory = select_directory("Sélectionner un dossier source à scanner")
    if not source_directory:
        # messagebox.showerror("Erreur", "Aucun dossier source sélectionné.") # Optionnel
        return

    output_file = select_output_file()
    if not output_file:
        # messagebox.showerror("Erreur", "Aucun fichier de sortie sélectionné.") # Optionnel
        return

    try:
        concat_files(source_directory, output_file)
        messagebox.showinfo("Succès", f"Le fichier a été généré avec succès à {output_file}")
    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur est survenue lors de la concaténation : {e}")

def create_ui():
    """Crée l'interface utilisateur avec Tkinter."""
    root = tk.Tk()
    root.title("Concaténer les fichiers v2.0")
    root.geometry("300x200") # Taille initiale un peu plus grande

    # Frame pour mieux organiser les boutons
    button_frame = Frame(root)
    button_frame.pack(expand=True) # Centre les boutons verticalement

    start_button = tk.Button(button_frame, text="Démarrer la Concaténation", command=start_process, height=2, width=25)
    start_button.pack(pady=10)

    config_button = tk.Button(button_frame, text="Créer / Modifier Configuration", command=create_or_edit_config, height=2, width=25)
    config_button.pack(pady=10)

    quit_button = tk.Button(button_frame, text="Quitter", command=root.quit, height=2, width=25)
    quit_button.pack(pady=10)

    # Lancer l'interface
    root.mainloop()

if __name__ == "__main__":
    create_ui()



