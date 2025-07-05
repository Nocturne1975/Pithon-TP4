class Counter:
    def __init__(self, start=0):
        self.count = start
        self.name = "Counter"
    
    def increment(self):
        self.count = self.count + 1
        return self.count
    
    def reset(self):
        self.count = 0
        return "Reset to " + str(self.count)

# Créer une instance
c = Counter(5)

# Accéder aux attributs
print("Initial count:", c.count)
print("Counter name:", c.name)

# Modifier un attribut directement
c.name = "MyCounter"


# Appeler des méthodes qui modifient des attributs
print("After increment:", c.increment())
print("After increment again:", c.increment())

# Ajouter un nouvel attribut
c.max_value = 100
print("Max value:", c.max_value)

# Réinitialiser
print(c.reset())
print("Final count:", c.count)
