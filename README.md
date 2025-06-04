# Tekbot Robotics – Architecture et Documentation

Le dossier **`Test_1`** contient trois modules principaux en Python :

      Test_1
      ├── robot.py             # classe de base 'Robot'
      ├── robot_collector.py   # sous-classe 'RobotCollector' (collecte de cubes)
      └── robot_trieur.py      # sous-classe 'RobotTrieur' (tri et dépôt)

---

## 1. Classe de base : `Robot`

- **Fichier** : `robot.py`  
- **Rôle** : définir les attributs et méthodes communs à tous les robots.  
- **Attributs privés** :
  - `__name` : nom du robot (str).  
  - `__position` : tuple (x, y, θ) – position dans l’arène.  
  - `__vitesseLin`, `__vitesseAng` : vitesses linéaire (m/s) et angulaire (rad/s).  
  - `__batteryLevel` : niveau de batterie (0–100 %).  
  - `__etat` : état courant – {"à l'arrêt", "en mouvement", "ramassage", "tri"}.  
  - `__activeSensors` : liste de capteurs actifs (Any).

- **Méthodes publiques** :
  - **Constructeur** `__init__(name)` : initialise les attributs par défaut.  
  - **Getters/Setters** :
    - `get_name()`, `set_name(str)` – contrôle du nom.  
    - `get_position()`, `set_position(x, y, θ)` – mise à jour de la position.  
    - `get_vitesse()`, `set_vitesse(v_lin, v_ang)` – modification des vitesses.  
    - `get_battery_level()`, `set_battery_level(float)` – contrôle du niveau de batterie (0 ≤ niveau ≤ 100).  
    - `get_etat()`, `set_etat(str)` – ne laisse passer que « à l'arrêt », « en mouvement », « ramassage », « tri ».  
    - `get_active_sensors()`, `add_sensor(obj)`, `remove_sensor(obj)` – gestion de la liste des capteurs.

  - **Méthodes de comportement** :
    - `@abstractmethod move()` : vérifie `batteryLevel` > 0 (sinon exception) et passe `etat = "en mouvement"`.  
      Le comportement concret (mobilité ou manipulation) est délégué aux sous-classes.
    - `status()` : affiche un résumé formaté : nom, position, batterie, état et capteurs actifs.

---

## 2. Sous-classe : `RobotCollector`

- **Fichier** : `robot_collector.py`  
- **Hérite de** : `Robot`  
- **Rôle** : gérer la mobilité différentielle (châssis à deux roues) et la collecte de cubes.

- **Attributs propres** :
  - `_ecartementRoues` (float) : distance entre les deux roues (m).  
  - `_pidLin`, `_pidAng` : instances `PIDController` (régulation des vitesses).  
  - `_stockageMax` (int) : capacité maximale de cubes.  
  - `_stockActuel` (int) : nombre actuel de cubes en stock.  
  - `_listeCubes` (List[Any]) : liste des objets `Cube` (simulés en stub par dicts).

- **Méthodes principales** :
  1. **`move()`** :
     - Appelle `super().move()` pour vérifier la batterie et passer en `"en mouvement"`.  
     - Deux modes (commentés) :
       - **Cas 1 (encodeurs)** : lire `wheel_left_speed`, `wheel_right_speed` → calculer `v` et `ω` par cinématique différentielle :
         
         ![Formule](https://github.com/Eudoo/TekBot_Robotics/blob/main/images/code1.svg)

         puis mettre à jour `(x,y,θ)` par intégration Euler sur `dt = 0.1`.  
       - **Cas 2 (sans encodeurs)** : utiliser directement `self._vitesseLin` et `self._vitesseAng`.
     - Tente `detectCube()`. Si un cube est détecté et que `_stockActuel < _stockageMax`, appelle `pickUpCube()`.
     - Simule une consommation d’énergie (`-0.1 %` par appel) et lève une erreur si la batterie est trop faible.

  2. **`detectCube() -> Optional[Tuple[float, float]]`** : 
     - Stub pour la détection OpenCV (renvoie `None` par défaut).  
     - À remplacer par une routine HSV + filtrage.

  3. **`pickUpCube() -> bool`** :
     - Réappelle `detectCube()`.  
     - Si un cube est détecté et que la capacité n’est pas atteinte :
       - Simule la prise (stub), ajoute `{"position": cube_pos}` à `_listeCubes`, incrémente `_stockActuel` et passe `etat = "ramassage"`.  
     - Sinon, renvoie `False`.

  4. **`shouldReturnToSort() -> bool`** :
     - Retourne `True` si `_stockActuel ≥ _stockageMax` ou `battery_level ≤ 20 %`.

  5. **`collectCycle()`** :
     - Boucle : tant que `shouldReturnToSort() == False`
       - Fixe une consigne `set_vitesse(0.5, 0.0)` et appelle `move()`.  
       - Si `pickUpCube()` réussit, affiche “Cube collecté…”.  
       - Remet `etat = "en mouvement"`.  
     - Dès que la condition est vraie, appelle `returnToSort()`.

  6. **`returnToSort()`** :
     - Donne une consigne `set_vitesse(0.5, 0.0)`, appelle `move()`, puis `set_etat("tri")`.  
     - Affiche “Arrivé à la zone de tri…”.

---

## 3. Sous-classe : `RobotTrieur`

- **Fichier** : `robot_trieur.py`  
- **Hérite de** : `Robot`  
- **Rôle** : manipuler un bras articulé pour trier/déposer des cubes dans les corbeilles.

- **Attributs propres** :
  - `_nbArticulations` (int) : nombre de joints du bras.  
  - `_angles` (List[float]) : angles courants de chaque articulation (initialisés à 0).  
  - `_forceMax` (float) : force maximale de préhension.  
  - `_corbeilles` (Dict[str, Tuple[float,float]]) : map couleur → coordonnées (x,y).  
  - `_cameraTri` (Any) : référence à l’objet caméra pour classification / QR.  
  - `_seuilConfiance` (float ∈ [0,1]) : seuil minimal de confiance pour la classification.

- **Méthodes principales** :
  1. **`move()`** :
     - Appelle `super().move()` (vérification batterie + état `"en mouvement"`).  
     - Passe `etat = "manipulation"` et affiche la liste `_angles` (stub de positionnement du bras).

  2. **`classifyCube(cropImage: Any) -> str`** :
     - Stub retournant `"doute"`. À remplacer par un algorithme HSV ou CNN pour renvoyer : `"bleu"`, `"vert"`, `"rouge"` ou `"doute"`.

  3. **`sortNextCube(listeCubes: List[Any]) -> None`** :
     - Si `listeCubes` vide : rien à faire.  
     - Sinon : retire un cube (`pop()`), appelle `classifyCube()`.  
       - Si la couleur n’est pas dans `_corbeilles`, la remplace par `"doute"`.  
       - Récupère `(xC, yC) = _corbeilles[couleur]`.  
       - `navigateArmTo(xC, yC)` pour calculer la cinématique inverse (stub qui fixe `_angles`).  
       - `move()` pour appliquer ces angles.  
       - `release()` pour ouvrir la pince (stub).  
       - `set_etat("à l'arrêt")` (attention à l’apostrophe ASCII).  
       - Affiche la confirmation de dépôt.

  4. **`calibrateSortingZone()`** :
     - Parcourt `_corbeilles` et « simule » la lecture d’un QR Code pour recalibrer leurs positions.  
     - Affiche la confirmation pour chaque corbeille.

  5. **`handleError()`** :
     - En cas d’échec de dépôt (détection manquée), affiche un message, relance `move()` (repositionnement du bras) et retente le dépôt.

  6. **`navigateArmTo(xC: float, yC: float)`** :
     - Stub de cinématique inverse : fixe arbitrairement tous les angles à 0.5 et affiche les nouveaux angles.

  7. **`release()`** :
     - Stub simulant l’ouverture de la pince (affiche “Pince ouverte, cube relâché.”).

---

## 4. Diagramme de Classe UML 

classDiagram
    class Robot {
        - __name: str
        - __position: Tuple[float, float, float]
        - __vitesseLin: float
        - __vitesseAng: float
        - __batteryLevel: float
        - __etat: str
        - __activeSensors: list[Any]
        + Robot(name: str)
        + get_name() : str
        + get_position() : Tuple[float, float, float]
        + get_vitesse() : Tuple[float, float]
        + get_battery_level() : float
        + get_etat() : str
        + get_active_sensors() : list[Any]
        + set_name(name: str) : None
        + set_position(x: float, y: float, theta: float) : None
        + set_vitesse(vitesseLin: float, vitesseAng: float) : None
        + set_battery_level(niveau: float) : None
        + set_etat(etat: str) : None
        + add_sensor(sensor: Any) : None
        + remove_sensor(sensor: Any) : None
        + move() : None <<abstract>>
        + status() : None
    }

    class RobotCollector {
        - _ecartementRoues: float
        - _pidLin: PIDController
        - _pidAng: PIDController
        - _stockageMax: int
        - _stockActuel: int
        - _listeCubes: List[Any]
        + RobotCollector(name: str, ecartementRoues: float, stockageMax: int)
        + get_ecartement_roues() : float
        + set_ecartement_roues(d: float) : None
        + get_stockage_max() : int
        + get_stock_actuel() : int
        + get_liste_cubes() : List[Any]
        + move() : None
        + detectCube() : Optional[Tuple[float, float]]
        + pickUpCube() : bool
        + shouldReturnToSort() : bool
        + collectCycle() : None
        + returnToSort() : None
    }

    class RobotTrieur {
        - _nbArticulations: int
        - _angles: List[float]
        - _forceMax: float
        - _corbeilles: Dict[str, Tuple[float, float]]
        - _cameraTri: Any
        - _seuilConfiance: float
        + RobotTrieur(name: str, nbArticulations: int, corbeilles: Dict[str, Tuple[float, float]], seuilConfiance: float)
        + get_nb_articulations() : int
        + get_angles() : List[float]
        + set_angles(new_angles: List[float]) : None
        + get_force_max() : float
        + set_force_max(f: float) : None
        + get_corbeilles() : Dict[str, Tuple[float, float]]
        + set_corbeilles(mapping: Dict[str, Tuple[float, float]]) : None
        + get_camera_tri() : Any
        + set_camera_tri(cam: Any) : None
        + get_seuil_confiance() : float
        + set_seuil_confiance(seuil: float) : None
        + move() : None
        + classifyCube(cropImage: Any) : str
        + sortNextCube(listeCubes: List[Any]) : None
        + calibrateSortingZone() : None
        + handleError() : None
        + navigateArmTo(xC: float, yC: float) : None
        + release() : None
    }

    Robot <|-- RobotCollector
    Robot <|-- RobotTrieur



