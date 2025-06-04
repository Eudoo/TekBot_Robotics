# test_robotics.py

from robot import Robot                # Classe de base (définie précédemment)
from robot_collector import RobotCollector
from robot_trieur import RobotTrieur

def test_robot_collector():
    print("=== Test RobotCollector ===")
    # Instanciation
    collector = RobotCollector(name="Collect1", ecartementRoues=0.5, stockageMax=2)
    
    # Afficher le statut initial
    collector.status()
    
    # Monkey‐patch : simulate detectCube pour la première itération
    calls = {"count": 0}
    def fake_detect():
        if calls["count"] == 0:
            calls["count"] += 1
            return (1.0, 2.0)   # position factice du cube
        else:
            return None
    collector.detectCube = fake_detect
    
    # Exécuter un move() : devrait simuler prise d’un cube
    print("\n-- Appel à move() avec un cube disponible --")
    collector.move()
    print(f"Stock actuel après move(): {collector.get_stock_actuel()}")
    collector.status()
    
    # Simuler une deuxième collecte dans la même boucle
    print("\n-- Appel à move() sans cube (détecte None) --")
    collector.move()
    print(f"Stock actuel après deuxième move(): {collector.get_stock_actuel()}")
    collector.status()
    
    # Test du cycle complet de collecte (collectCycle)
    print("\n-- Lancement de collectCycle() --")
    # Monkey‐patch pour faire détecter un cube à la prochaine itération
    collector.detectCube = lambda: (2.5, -0.5)  
    collector.collectCycle()  
    # Après avoir collecté jusqu’à stockageMax, il doit revenir au tri
    collector.status()
    print("=== Fin test RobotCollector ===\n")


def test_robot_trieur():
    print("=== Test RobotTrieur ===")
    # Définir un dictionnaire simulé pour les corbeilles
    corbeilles = {
        "bleu": (0.0, 0.0),
        "vert": (1.0, 0.0),
        "rouge": (0.0, 1.0),
        "doute": (1.0, 1.0)
    }
    trieur = RobotTrieur(name="Tri1", nbArticulations=3, corbeilles=corbeilles, seuilConfiance=0.6)
    
    # Afficher le statut initial
    trieur.status()
    
    # Préparer une liste de 2 cubes simulés (on ne se soucie que de leur existence)
    liste_cubes = [{"id": "C1"}, {"id": "C2"}]
    
    # Monkey‐patch classifyCube pour alterner "bleu" puis "rouge"
    seq = {"i": 0}
    def fake_classify(_):
        seq["i"] += 1
        return "bleu" if seq["i"] == 1 else "rouge"
    trieur.classifyCube = fake_classify
    
    # Monkey‐patch navigateArmTo pour afficher la cible
    def fake_navigate(x, y):
        print(f"--> Bras se déplace vers ({x}, {y})")
        # Simuler mise à jour d’angles
        trieur._angles = [0.1 * seq["i"]] * trieur.get_nb_articulations()
    trieur.navigateArmTo = fake_navigate
    
    # Tester sortNextCube pour deux itérations
    print("\n-- Tri du premier cube (doit aller à 'bleu') --")
    trieur.sortNextCube(liste_cubes)
    trieur.status()
    
    print("\n-- Tri du deuxième cube (doit aller à 'rouge') --")
    trieur.sortNextCube(liste_cubes)
    trieur.status()
    print("=== Fin test RobotTrieur ===\n")


if __name__ == "__main__":
    test_robot_collector()
    test_robot_trieur()
