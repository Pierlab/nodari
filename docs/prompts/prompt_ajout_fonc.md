Tu travailles sur le projet Nodari. Aujourd’hui, ta mission est d’ajouter **une nouvelle fonctionnalité** dans le moteur de simulation.

1. Commence par **lire ou relire `project_spec.md`**, en particulier les sections suivantes :
   - L’architecture générale (SimNode, bus d’événements, plugins)
   - Les conventions de développement
   - La structure des fichiers
   - La checklist des tâches

2. Avant de coder, prends le temps de réfléchir à :
   - Où cette nouvelle fonctionnalité s’insère dans l’arbre SimNode
   - Si elle doit être un **nouveau type de nœud** (dans `nodes/`) ou un **système global** (dans `systems/`)
   - Si elle déclenche ou écoute des **événements**
   - Si elle a besoin d’un stockage interne (état, inventaire, relations…)

3. Implémente la fonctionnalité de façon :
   - **Isolée** (un seul nœud = une seule responsabilité)
   - **Compatible** avec le système de plugins (`core/plugins.py`)
   - **Extensible** pour d’autres scénarios à venir
   - **Testée** (ajoute un test unitaire minimal dans `tests/`)
   - **Documentée** (docstring + exemple d’usage si besoin)

4. Mets à jour :
   - La **checklist de `project_spec.md`** pour y inscrire cette nouvelle fonctionnalité
   - Le **README.md** si cette fonctionnalité est visible ou importante

5. Commets les changements avec un message clair, du type :
   - `git commit -m "feat: add nouvelle fonctionnalité"`

