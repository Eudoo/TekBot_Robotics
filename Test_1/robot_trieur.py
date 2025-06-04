from typing import Tuple, Any, List, Dict
from abc import ABC
from robot import Robot

class RobotTrieur(Robot, ABC):
    """
    RobotTrieur : hérite de Robot.
    Spécialisé dans la phase de tri/dépôt dans les corbeilles à l'aide d'un bras articulé.
    """

    def __init__(self, name: str, nbArticulations: int, corbeilles: Dict[str, Tuple[float, float]], seuilConfiance: float = 0.7):
        super().__init__(name)

        self._nbArticulations: int = nbArticulations
        self._angles: List[float] = [0.0] * nbArticulations    # Angles actuels des articulations
        self._forceMax: float = 1.0                            # Force maximale de préhension

        # --- Carte des corbeilles (couleur → coordonnées) ---
        self._corbeilles: Dict[str, Tuple[float, float]] = corbeilles

        # Caméra utilisée pour la classification ou pour lire des QR Codes
        self._cameraTri: Any = None

        # Seuil de confiance pour la classification d’un cube (si on utilise un CNN ou HSV)
        self._seuilConfiance: float = seuilConfiance


    # ---------- Getters / Setters ----------

    def get_nb_articulations(self) -> int:
        return self._nbArticulations

    def get_angles(self) -> List[float]:
        return list(self._angles)

    def set_angles(self, new_angles: List[float]) -> None:
        if len(new_angles) != self._nbArticulations:
            raise ValueError("Le nombre d'angles doit correspondre au nombre d'articulations.")
        self._angles = new_angles

    def get_force_max(self) -> float:
        return self._forceMax

    def set_force_max(self, f: float) -> None:
        if f <= 0:
            raise ValueError("La force maximale doit être positive.")
        self._forceMax = f

    def get_corbeilles(self) -> Dict[str, Tuple[float, float]]:
        # Renvoie une copie pour ne pas exposer directement la référence interne
        return self._corbeilles.copy()

    def set_corbeilles(self, mapping: Dict[str, Tuple[float, float]]) -> None:
        if not mapping:
            raise ValueError("La carte des corbeilles ne peut pas être vide.")
        self._corbeilles = mapping

    def get_camera_tri(self) -> Any:
        return self._cameraTri

    def set_camera_tri(self, cam: Any) -> None:
        self._cameraTri = cam

    def get_seuil_confiance(self) -> float:
        return self._seuilConfiance

    def set_seuil_confiance(self, seuil: float) -> None:
        if not (0.0 <= seuil <= 1.0):
            raise ValueError("Le seuil de confiance doit être compris entre 0 et 1.")
        self._seuilConfiance = seuil


    # ---------- Méthodes principales ----------

    def move(self) -> None:
        """
        Implémentation de move() pour RobotTrieur :
        - Vérifie la batterie puis met à jour l’état.
        - Simule la mise à jour instantanée des articulations du bras.
        """
        super().move()   # vérification de la batterie + etat = "en mouvement"
        self.set_etat("en mouvement")
        print(f"[{self.get_name()}] Bras positionné selon angles {self._angles}.")


    def classifyCube(self, cropImage: Any) -> str:
        """
        Classifie un cube à partir d'une image recadrée (cropImage).
        - Stub : renvoie toujours "doute". À remplacer par HSV ou CNN.
        - Doit renvoyer l’une des chaînes : "bleu", "vert", "rouge" ou "doute".
        """
        return "doute"


    def sortNextCube(self, listeCubes: List[Any]) -> None:
        """
        Dépose le prochain cube de listeCubes dans la corbeille appropriée.
        1. Si listeCubes est vide, ne fait rien.
        2. Sinon : 
           - pop() pour retirer un cube,
           - classifyCube() pour déterminer la couleur,
           - navigateArmTo() pour orienter le bras vers la corbeille,
           - move() pour exécuter le placement,
           - release() pour lâcher le cube,
           - passe l'état à "à l'arrêt".
        """
        if not listeCubes:
            return

        # Récupération du cube (dernier ajouté)
        cube = listeCubes.pop()

        # Stub : récupère l'image du cube pour classification (à implémenter)
        cropImage = None  
        couleur = self.classifyCube(cropImage)
        if couleur not in self._corbeilles:
            couleur = "doute"

        # Coordonnées de la corbeille cible
        xC, yC = self._corbeilles[couleur]

        # Oriente le bras vers la corbeille
        self.navigateArmTo(xC, yC)
        # Exécute la manipulation
        self.move()
        # Lâche le cube
        self.release()
        self.set_etat("à l'arrêt")
        print(f"Cube déposé dans la corbeille '{couleur}' aux coords ({xC}, {yC}).")


    def calibrateSortingZone(self) -> None:
        """
        Lit les QR Codes devant chaque corbeille pour mettre à jour leur position réelle.
        Stub : on simule la reconnaissance ; on reconfirme juste la position actuelle.
        """
        for couleur, coords in self._corbeilles.items():
            true_coords = coords  # Stub : ici, on ferait lecture QR pour recalibrer
            self._corbeilles[couleur] = true_coords
            print(f"Corbeille '{couleur}' calibrée à la position {true_coords}.")


    def handleError(self) -> None:
        """
        En cas d'échec de dépôt, on effectue une micro-rotation et on retente l’opération.
        """
        print(f"[{self.get_name()}] Erreur détectée lors du dépôt, réessai en cours...")
        self.move()  # Nouveau positionnement du bras (stub)
        print("Réessai de dépôt effectué.")


    def navigateArmTo(self, xC: float, yC: float) -> None:
        """
        Calcule la cinématique inverse pour orienter le bras vers la position (xC, yC).
        Met à jour self._angles en conséquence (stub simplifié).
        """
        # Stub : on simule la mise à jour des angles pour toutes les articulations
        # (ex. répartir une même valeur sur chaque articulation)
        for i in range(self._nbArticulations):
            self._angles[i] = 0.5  # Valeur arbitraire simulée
        print(f"Navigation du bras vers ({xC}, {yC}) calculée, angles fixés à {self._angles}.")


    def release(self) -> None:
        """
        Ouvre la pince pour déposer le cube.
        Stub : en pratique, on commanderait le servomoteur de la pince.
        """
        print("Pince ouverte, cube relâché.")

