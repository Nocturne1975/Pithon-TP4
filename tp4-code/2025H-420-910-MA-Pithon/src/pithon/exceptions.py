class PithonError(Exception):
    """Exception de base pour Pithon"""
    pass

class PithonSyntaxError(PithonError):
    """Erreur de syntaxe dans le code Pithon"""
    def __init__(self, message, line=None, column=None):
        self.line = line
        self.column = column
        super().__init__(f"Erreur de syntaxe: {message}" + 
                        (f" à la ligne {line}" if line else ""))

class PithonTypeError(PithonError):
    """Erreur de type dans Pithon"""
    def __init__(self, expected, got, operation=None):
        msg = f"Type incorrect: attendu {expected}, reçu {got}"
        if operation:
            msg += f" pour l'opération {operation}"
        super().__init__(msg)

class PithonNameError(PithonError):
    """Variable ou fonction non définie"""
    def __init__(self, name):
        super().__init__(f"Nom '{name}' n'est pas défini")

class PithonAttributeError(PithonError):
    """Attribut non trouvé"""
    def __init__(self, obj_type, attr_name):
        super().__init__(f"L'objet de type '{obj_type}' n'a pas d'attribut '{attr_name}'")

class PithonIndexError(PithonError):
    """Index hors limites"""
    def __init__(self, index, length):
        super().__init__(f"Index {index} hors limites pour une collection de taille {length}")

class PithonZeroSivisionError(PithonError):
    """Division par zero"""
    def __init__(self):
        super().__init__("Division par zero")

class PithonValueError(PithonError):
    """Valeur inappropriee"""
    def __init__(self, message):
        super().__init__("Valeur incorrecte:{message}")

class PithonCallError(PithonError):
    """Erreur lors d'un appel de fonction"""
    def __init__(self, func_name, message):
        super().__init__(f"Erreur lors de l'appel de '{func_name}' : {message}")

class PithonBreakError(PithonError):
    """Break en dehors d'une boucle"""
    def __init__(self):
        super().__init__("'continue' en dehors d'une boucle")
        