from typing import Optional, Tuple, Any
from abc import ABC, abstractmethod

class Robot(ABC): 
    def __init__(self, name : str):
        self.__name : str = name
        self.__position : Tuple[float, float, float] = (0.0, 0.0, 0.0)
        self.__vitesseLin : float = 0.0
        self.__vitesseAng : float = 0.0
        self.__batteryLevel : float = 100.0
        self.__etat : str = "à l'arrêt"
        self.__activeSensors : list[Any] = []

    # ---------- Getters ----------
   
    def get_name(self) -> str:
        return self.__name
    
    def get_position(self) -> Tuple[float, float, float]:
        return self.__position
    
    def get_vitesse(self) -> Tuple[float, float]:
        return (self.__vitesseLin, self.__vitesseAng)
    
    def get_battery_level(self) -> float:
        return self.__batteryLevel
    
    def get_etat(self) -> str:
        return self.__etat
    
    def get_active_sensors(self) -> list[Any]:
        return self.__activeSensors
    
    # ---------- Setters ----------
    
    def set_name(self, name: str) -> None:
        if not name:
            raise ValueError("Le nom ne peut pas être vide.")
        self.__name = name
    
    def set_position(self, x: float, y: float, theta: float) -> None:
        self.__position = (x, y, theta)

    def set_vitesse(self, vitesseLin: float, vitesseAng: float) -> None:
        self.__vitesseLin = vitesseLin
        self.__vitesseAng = vitesseAng

    def set_battery_level(self, niveau: float) -> None:
        if not (0.0 <= niveau <= 100.0):
            raise ValueError("Le niveau de batterie doit être entre 0 et 100.")
        self._batteryLevel = niveau

    def set_etat(self, etat: str) -> None:
        if etat not in {"à l'arrêt", "en mouvement", "ramassage", "tri"}:
            raise ValueError("État invalide.")
        self.__etat = etat

    def add_sensor(self, sensor: Any) -> None:
        if sensor not in self.__activeSensors:
            self.__activeSensors.append(sensor)

    def remove_sensor(self, sensor: Any) -> None:
        if sensor in self.__activeSensors:
            self.__activeSensors.remove(sensor)

    # ---------- Méthodes de comportement ----------
    
    @abstractmethod
    def move(self):
        """
        - A redéfinir dans chaque sous-classe.
        - Vérifier la batterie et mettre à jour l'état.
        """
        if self.__batteryLevel <= 0:
            self.__etat = "à l'arrêt"
            raise RuntimeError("Batterie vide, le robot ne peut pas se déplacer.")
        self.__etat = "en mouvement"

    def status(self) -> None:
        """
        Affiche un résumé des attributs essentiels du robot.
        """

        x, y, theta = self.get_position()
        print(f"Robot '{self.get_name()}' | Position: ({x:.2f}, {y:.2f}, θ={theta:.2f}) | "
              f"Batterie: {self.get_battery_level():.1f}% | État: {self.get_etat()}")
        if self.get_active_sensors():
            print(f"Capteurs actifs: {', '.join(str(s) for s in self.get_active_sensors())}")
        else:
            print("Aucun capteur actif.")
