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

[![](https://mermaid.ink/img/pako:eNqNVk1v2zgQ_SsC9-JilcJ2vLEjBAUMp4cC2e4izV4aFwIljR2iFCmQVNZuNv99h5Qt64Ny4oslzZvhzOO8IV9IKjMgEUk51fqW0a2i-VoE-HNfgnuZSBO8VJ_s7yKIY0FziAJtVPtzITUzTIooeCgLDo8bLqkJg-bfj7bHMzOgNdwx9HF2r3kptl5zQo0Btb-DZ-BeABhqPHnS1LBn-AZCS6WjgDNtHpdi38jt96ruUV3oh6ZtC8ZRMPoQdKJXtiMPzv4eKiq3Q7UDXj34ofqY2_KdU4eBCmY5GEq0IiLWFRMOdSSjCdXHek90IPKrFNBF1ZXvomOt-_rJPGEuh7ehAEcOeo0RBr1mGIrRJkZghbR8w8WRVHeLD0Wz7MDTqPqLAmTJh1SQy5rUt8AWOjoagpsbmuD6uC2fPrVSxMxKPWoHeF2LnlBXknNIjVRNxf4WxJBSZSAHYe5lCbrXKggpWObY_vvL7UoKo2wk1UU48ocR2sj0J93CnxT3nwnTNy5TU1qxdo227WBVJja3u0E91uWdOjEM_LWFQTeZnoRPjrGynn4NaR8yO9NPNvRx7TinOxe2VW8DYyVYHuTrwTha4tTy4iBealo91DRkYJAty6oz_1VYaVL-6BkurYAFS3_-U9R-iZS8xciTLHl2D6ZU4kF-k8p4YWm1Wat9yv3pqW6E8739oBiU3cYWyVIZlpac2tp0v7Go2PK6qbqDFO0bqdKqRfqSSKVKgHHnf8tS8-j67Tx71g17U1FM16m-rQEoGUfxbBgVKXi6rVFps8d9ZYbB-_NDNfhW7p9qSUybCw31ZcXqqSX7J5Q-oQT869uGIe24HamF49XjCbJ5Q4gnily09-5itUzDOadFwezwOx9hMA3XErFRzKXhOV8bCHwcPC_c4LBbickd9nKYpi7QvZ8hbHCQOBWyzd6NhFTJ4kuOw61OsnOzwPPOfIVdNXi8g927BuUsUdSAHQdI9Xe0e5N5oiLj8FkpPAZ8dkGf2RbjLFX-IEe71ekmsjpTuwIOVMPQHKquwTf_XVx0TiK_uVLwWpCQbBXLSGRUCSHBLc6pfSVuiq0JXolyWJMIHzPY0JKbNVmLV3QrqPguZX70xGNn-0SiDeUa38oiwwIPt_UaAiIDtZKlMCSaXs5cDBK9kB2JFtOPi_n8cvHH7Gq6GF9PpiHZ49fJx9lkPLuez2eX8-nVbPIakl9uUTQsrsaL8dX1bD4Zj68Xr_8DhW-_Bg?type=png)](https://mermaid.live/edit#pako:eNqNVk1v2zgQ_SsC9-JilcJ2vLEjBAUMp4cC2e4izV4aFwIljR2iFCmQVNZuNv99h5Qt64Ny4oslzZvhzOO8IV9IKjMgEUk51fqW0a2i-VoE-HNfgnuZSBO8VJ_s7yKIY0FziAJtVPtzITUzTIooeCgLDo8bLqkJg-bfj7bHMzOgNdwx9HF2r3kptl5zQo0Btb-DZ-BeABhqPHnS1LBn-AZCS6WjgDNtHpdi38jt96ruUV3oh6ZtC8ZRMPoQdKJXtiMPzv4eKiq3Q7UDXj34ofqY2_KdU4eBCmY5GEq0IiLWFRMOdSSjCdXHek90IPKrFNBF1ZXvomOt-_rJPGEuh7ehAEcOeo0RBr1mGIrRJkZghbR8w8WRVHeLD0Wz7MDTqPqLAmTJh1SQy5rUt8AWOjoagpsbmuD6uC2fPrVSxMxKPWoHeF2LnlBXknNIjVRNxf4WxJBSZSAHYe5lCbrXKggpWObY_vvL7UoKo2wk1UU48ocR2sj0J93CnxT3nwnTNy5TU1qxdo227WBVJja3u0E91uWdOjEM_LWFQTeZnoRPjrGynn4NaR8yO9NPNvRx7TinOxe2VW8DYyVYHuTrwTha4tTy4iBealo91DRkYJAty6oz_1VYaVL-6BkurYAFS3_-U9R-iZS8xciTLHl2D6ZU4kF-k8p4YWm1Wat9yv3pqW6E8739oBiU3cYWyVIZlpac2tp0v7Go2PK6qbqDFO0bqdKqRfqSSKVKgHHnf8tS8-j67Tx71g17U1FM16m-rQEoGUfxbBgVKXi6rVFps8d9ZYbB-_NDNfhW7p9qSUybCw31ZcXqqSX7J5Q-oQT869uGIe24HamF49XjCbJ5Q4gnily09-5itUzDOadFwezwOx9hMA3XErFRzKXhOV8bCHwcPC_c4LBbickd9nKYpi7QvZ8hbHCQOBWyzd6NhFTJ4kuOw61OsnOzwPPOfIVdNXi8g927BuUsUdSAHQdI9Xe0e5N5oiLj8FkpPAZ8dkGf2RbjLFX-IEe71ekmsjpTuwIOVMPQHKquwTf_XVx0TiK_uVLwWpCQbBXLSGRUCSHBLc6pfSVuiq0JXolyWJMIHzPY0JKbNVmLV3QrqPguZX70xGNn-0SiDeUa38oiwwIPt_UaAiIDtZKlMCSaXs5cDBK9kB2JFtOPi_n8cvHH7Gq6GF9PpiHZ49fJx9lkPLuez2eX8-nVbPIakl9uUTQsrsaL8dX1bD4Zj68Xr_8DhW-_Bg)
