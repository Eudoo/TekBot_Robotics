from typing import Tuple, Optional, Any, Deque, List
from collections import deque
from math import cos, sin
from robot import Robot
from abc import ABC

# Si PIDController existe, on l'importe ; sinon, on peut définir un stub
class PIDController:
    def __init__(self, kp: float, ki: float, kd: float):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        # État interne pour le calcul PID (erreur précédente, intégrale, etc.)
        self._previous_error = 0.0
        self._integral = 0.0

    def compute(self, setpoint: float, measurement: float, dt: float) -> float:
        """
        Retourne la commande PID pour atteindre 'setpoint' à partir de la mesure 'measurement'.
        dt est l'intervalle de temps depuis la dernière mise à jour.
        """
        error = setpoint - measurement
        self._integral += error * dt
        derivative = (error - self._previous_error) / dt if dt > 0 else 0.0
        output = self.kp * error + self.ki * self._integral + self.kd * derivative
        self._previous_error = error
        return output



class RobotCollector(Robot, ABC):
    """
    RobotCollector : hérite de Robot.
    Gère la mobilité différentielle (deux roues) et la collecte de cubes.
    """

    def __init__(self, name: str, ecartementRoues: float, stockageMax: int):
        super().__init__(name)
        self._ecartementRoues: float = ecartementRoues

        # Initialise deux PID pour la régulation des vitesses
        self._pidLin: PIDController = PIDController(kp=1.0, ki=0.0, kd=0.0)
        self._pidAng: PIDController = PIDController(kp=1.0, ki=0.0, kd=0.0)

        # Stockage des cubes
        self._stockageMax: int = stockageMax
        self._stockActuel: int = 0
        self._listeCubes: List[Any] = [] 

    # ---------- Getters / Setters supplémentaires ----------

    def get_ecartement_roues(self) -> float:
        return self._ecartementRoues

    def set_ecartement_roues(self, d: float) -> None:
        if d <= 0:
            raise ValueError("L'écartement des roues doit être positif.")
        self._ecartementRoues = d

    def get_stockage_max(self) -> int:
        return self._stockageMax

    def get_stock_actuel(self) -> int:
        return self._stockActuel

    def get_liste_cubes(self) -> List[Any]:
        return self._listeCubes

    # ---------- Méthodes de collecte / mobilité ----------

    def move(self) -> None:
        """
        Implémentation du move() pour RobotCollector.
        Utilise la cinématique différentielle pour mettre à jour la position.
        Intègre la détection de cube à chaque itération.
        """
        # Vérification batterie + mise à jour d'état 
        super().move()

        # Exemple de calcul de vitesse et mise à jour position :
        # - On suppose avoir des consignes cibles self._vitesseLin et self._vitesseAngulaire
        # - On lit les vitesses réelles des roues (stub ici à 0.0)

        "Cas 1 : Avec encoders ou capteurs de vitesse"
        wheel_left_speed = 0.0
        wheel_right_speed = 0.0

        # Calcul de la vitesse linéaire et angulaire selon l'écartement des roues
        v = (wheel_right_speed + wheel_left_speed) / 2.0
        omega = (wheel_right_speed - wheel_left_speed) / self._ecartementRoues

        # Mise à jour de la position (approximation Euler simple pour dt arbitraire)
        dt = 0.1  # À remplacer par le vrai pas de temps en production
        x, y, theta = self.get_position()
        new_theta = theta + omega * dt
        new_x = x + v * dt * cos(theta)
        new_y = y + v * dt * sin(theta)
        self.set_position(new_x, new_y, new_theta)

        "Cas 2 : Sans encoders, juste vitesse linéaire et angulaire"
        '''
        v = self._vitesseLin
        omega = self._vitesseAngulaire 
        '''

        # Tentative de détection et collecte d'un cube
        cube_pos = self.detectCube()
        if cube_pos and self._stockActuel < self._stockageMax:
            success = self.pickUpCube()
            if success:
                print(f"Cube ramassé ! Stock actuel : {self._stockActuel}/{self._stockageMax}")
        
        consommation = 0.1  # Consommation d'énergie par mouvement
        if self.get_battery_level() < consommation:
            raise RuntimeError("Batterie insuffisante pour continuer le mouvement.")
        self.set_battery_level(self.get_battery_level() - consommation)

    def detectCube(self) -> Optional[Tuple[float, float]]:
        """
        Stub de détection de cube.
        Idéalement, on capture une image, on applique HSV + filtrage, etc.
        Retourne (x_cube, y_cube) si un cube est détecté à portée, sinon None.
        """
        # Implémenter la vraie détection via OpenCV.
        return None

    def pickUpCube(self) -> bool:
        """
        Ramasse un cube si détecté.
        - Si un cube est détecté (detectCube() != None) et si la capacité n'est pas pleine :
            • on aligne le robot (via bras interne ou scoop)
            • on ajoute l'objet Cube à la liste
            • on incrémente _stockActuel
            • on passe __etat = "ramassage"
        - Sinon, on retourne False.
        """
        cube_pos = self.detectCube()
        if cube_pos is None:
            return False
        if self._stockActuel >= self._stockageMax:
            return False

        # Aligner le robot sur cube_pos, puis actionner le bras ou scoop pour ramasser.
        # Pour l'instant, on simule la prise :
        cube_obj = {"position": cube_pos}  # Exemple d'objet stub
        self._listeCubes.append(cube_obj)
        self._stockActuel += 1
        self.set_etat("ramassage")
        return True

    def shouldReturnToSort(self) -> bool:
        """
        Retourne True si le robot doit retourner trier :
        - soit le stockage est plein
        - soit la batterie est trop faible (on choisit 20% comme seuil par exemple)
        """
        if self._stockActuel >= self._stockageMax:
            return True
        if self.get_battery_level() <= 20.0:
            return True
        return False

    def collectCycle(self) -> None:
        """
        Boucle principale de collecte.
        Tant que self.shouldReturnToSort() est False, le robot :
        - se déplace vers le département suivant
        - cherche un cube via detectCube()
        - tente pickUpCube()
        - met à jour l'état en "ramassage"
        Dès que shouldReturnToSort() devient True, on appelle returnToSort().
        """
        while not self.shouldReturnToSort():
            # Définir la logique pour choisir le prochain département ( surement ici sera l'algo de navigation A* , etc)
            # Exemple : self.navigateTo(next_dept_x, next_dept_y)
            # On simule un déplacement temporaire
            self.set_vitesse(0.5, 0.0)  # avancer droit
            self.move()

            # Tentative de ramassage
            if self.pickUpCube():
                print("Cube collecté pendant la boucle.")
            self.set_etat("en mouvement")

        # On revient trier
        self.returnToSort()

    def returnToSort(self) -> None:
        """
        Planifie et exécute le chemin vers la zone de tri (coordonnées fixes ou repérées).
        Appelle ensuite le tri via une classe RobotTrieur ou le stub de dépôt.
        """
        # Planifier un chemin vers la zone de tri (ex. coordonnées (0, 0))
        # On simule la navigation :
        self.set_vitesse(0.5, 0.0)
        self.move()
        self.set_etat("tri")
        print("Arrivé à la zone de tri, prêt pour le tri.")
