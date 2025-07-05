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
            msg += f" pour l'opération '{operation}'"
        super().__init__(msg)

class PithonNameError(PithonError):
    """Variable ou fonction non définie"""
    def __init__(self, message, suggestions=None):
        if suggestions:
            message += f". Suggestions: {', '.join(suggestions)}"
        super().__init__(message)

class PithonAttributeError(PithonError):
    """Attribut non trouvé"""
    def __init__(self, message):
        super().__init__(message)

class PithonIndexError(PithonError):
    """Index hors limites"""
    def __init__(self, message):
        super().__init__(message)

class PithonZeroDivisionError(PithonError):
    """Division par zéro"""
    def __init__(self):
        super().__init__("Division par zéro")

class PithonValueError(PithonError):
    """Valeur inappropriée"""
    def __init__(self, message):
        super().__init__(f"Valeur incorrecte: {message}")

class PithonCallError(PithonError):
    """Erreur lors d'un appel de fonction"""
    def __init__(self, message):
        super().__init__(message)

class PithonBreakError(PithonError):
    """Break en dehors d'une boucle"""
    def __init__(self):
        super().__init__("'break' en dehors d'une boucle")

class PithonContinueError(PithonError):
    """Continue en dehors d'une boucle"""
    def __init__(self):
        super().__init__("'continue' en dehors d'une boucle") 
class Student:
    def greet(self):
        print("Hi, I'm", self.name, "from", self.school)