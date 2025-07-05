from typing import Any, Type, TypeVar
from pithon.evaluator.envvalue import EnvValue, VList, VNone, VTuple, VNumber, VBool, VString
from pithon.exceptions import PithonTypeError, PithonZeroDivisionError


T = TypeVar('T')
def check_type(obj: Any, mytype: Type[T]) -> T:
    """Vérifie que l'objet est du type attendu, sinon lève une exception."""
    if not isinstance(obj, mytype):
        type_attendu = mytype.__name__.replace('V', '').lower()
        type_obtenu = type(obj).__name__.replace('V', '').lower()
        raise PithonTypeError(type_attendu, type_obtenu)
    return obj

def get_primitive_dict():
    return {
        '+': primitive_adds,
        '-': primitive_sub,
        '*': primitive_mul,
        '/': primitive_div,
        '//': primitive_floordiv,
        '%': primitive_mod,
        '**': primitive_pow, 
        '==': primitive_eq,
        '!=': primitive_neq,
        '<': primitive_lt,
        '>': primitive_gt, 
        '<=': primitive_lte,
        '>=': primitive_gte, 
        'abs': primitive_abs, 
        'max': primitive_max,
        'min': primitive_min,
        'len': primitive_len,
        'head': primitive_head,
        'tail': primitive_tail,
        'append': primitive_append,
        'concat': primitive_concat,
        'upper': primitive_upper,
        'lower': primitive_lower,
        'str': primitive_str,
        'range': primitive_range, 
        'print': primitive_print,
        'tuple': primitive_tuple
    }

def primitive_adds(args: list[EnvValue]):
    """Fonction d'addition primitive avec gestion d'erreurs améliorée."""
    if len(args) != 2:
        raise PithonTypeError("2 arguments", f"{len(args)} arguments", "addition")
    
    a, b = args
    if isinstance(a, VList) and isinstance(b, VList):
        return VList(a.value + b.value)
    if isinstance(a, VTuple) and isinstance(b, VTuple):
        return VTuple(a.value + b.value)
    if isinstance(a, VNumber) and isinstance(b, VNumber):
        return VNumber(a.value + b.value)
    if isinstance(a, VString) and isinstance(b, VString):
        return VString(a.value + b.value)
    
    # Message d'erreur plus détaillé
    type_a = type(a).__name__.replace('V', '').lower()
    type_b = type(b).__name__.replace('V', '').lower()
    
    raise PithonTypeError(f"types compatibles pour l'addition", f"{type_a} et {type_b}", "addition")

def primitive_sub(args: list[EnvValue]):
    """Soustrait deux nombres."""
    if len(args) != 2:
        raise PithonTypeError("2 arguments", f"{len(args)} arguments", "soustraction")
    
    a, b = args
    if isinstance(a, VNumber) and isinstance(b, VNumber):
        return VNumber(a.value - b.value)
    
    type_a = type(a).__name__.replace('V', '').lower()
    type_b = type(b).__name__.replace('V', '').lower()
    raise PithonTypeError("number et number", f"{type_a} et {type_b}", "soustraction")

def primitive_mul(args: list[EnvValue]):
    """Multiplie deux nombres ou répète une séquence (liste, tuple, chaîne)."""
    if len(args) != 2:
        raise PithonTypeError("2 arguments", f"{len(args)} arguments", "multiplication")
    
    a, b = args
    # Multiplication de nombres
    if isinstance(a, VNumber) and isinstance(b, VNumber):
        return VNumber(a.value * b.value)
    # Répétition de séquences
    if isinstance(a, VList) and isinstance(b, VNumber):
        return VList(a.value * int(b.value))
    if isinstance(a, VNumber) and isinstance(b, VList):
        return VList(b.value * int(a.value))
    if isinstance(a, VTuple) and isinstance(b, VNumber):
        return VTuple(a.value * int(b.value))
    if isinstance(a, VNumber) and isinstance(b, VTuple):
        return VTuple(b.value * int(a.value))
    if isinstance(a, VString) and isinstance(b, VNumber):
        return VString(a.value * int(b.value))
    if isinstance(a, VNumber) and isinstance(b, VString):
        return VString(b.value * int(a.value))
    
    type_a = type(a).__name__.replace('V', '').lower()
    type_b = type(b).__name__.replace('V', '').lower()
    raise PithonTypeError("types compatibles pour la multiplication", f"{type_a} et {type_b}", "multiplication")

def primitive_div(args: list[EnvValue]):
    """Divise deux nombres, lève une erreur si division par zéro."""
    if len(args) != 2:
        raise PithonTypeError("2 arguments", f"{len(args)} arguments", "division")
    
    a, b = args
    if isinstance(a, VNumber) and isinstance(b, VNumber):
        if b.value == 0:
            raise PithonZeroDivisionError()
        return VNumber(a.value / b.value)
    
    type_a = type(a).__name__.replace('V', '').lower()
    type_b = type(b).__name__.replace('V', '').lower()
    raise PithonTypeError("number et number", f"{type_a} et {type_b}", "division")

def primitive_floordiv(args: list[EnvValue]) -> EnvValue:
    """Division entière (//)."""
    if len(args) != 2:
        raise PithonTypeError("2 arguments", f"{len(args)} arguments", "division entière")
    
    a, b = args
    if not isinstance(a, VNumber) or not isinstance(b, VNumber):
        type_a = type(a).__name__.replace('V', '').lower()
        type_b = type(b).__name__.replace('V', '').lower()
        raise PithonTypeError("number et number", f"{type_a} et {type_b}", "division entière")
    
    if b.value == 0:
        raise PithonZeroDivisionError()
    
    return VNumber(a.value // b.value)
 
def primitive_mod(args: list[EnvValue]):
    """Calcule le modulo de deux nombres, lève une erreur si division par zéro."""
    if len(args) != 2:
        raise PithonTypeError("2 arguments", f"{len(args)} arguments", "modulo")
    
    a, b = args
    if isinstance(a, VNumber) and isinstance(b, VNumber):
        if b.value == 0:
            raise PithonZeroDivisionError()
        return VNumber(a.value % b.value)
    
    type_a = type(a).__name__.replace('V', '').lower()
    type_b = type(b).__name__.replace('V', '').lower()
    raise PithonTypeError("number et number", f"{type_a} et {type_b}", "modulo")

def primitive_eq(args: list[EnvValue]):
    """Teste l'égalité entre deux valeurs."""
    if len(args) != 2:
        raise PithonTypeError("2 arguments", f"{len(args)} arguments", "égalité")
    
    a, b = args
    return VBool(a == b)

def primitive_neq(args: list[EnvValue]):
    """Teste la différence entre deux valeurs."""
    if len(args) != 2:
        raise PithonTypeError("2 arguments", f"{len(args)} arguments", "inégalité")
    
    a, b = args
    return VBool(a != b)

def primitive_lt(args: list[EnvValue]):
    """Teste si la première valeur est inférieure à la seconde (nombres ou chaînes)."""
    if len(args) != 2:
        raise PithonTypeError("2 arguments", f"{len(args)} arguments", "comparaison <")
    
    a, b = args
    if isinstance(a, VNumber) and isinstance(b, VNumber):
        return VBool(a.value < b.value)
    if isinstance(a, VString) and isinstance(b, VString):
        return VBool(a.value < b.value)
    
    type_a = type(a).__name__.replace('V', '').lower()
    type_b = type(b).__name__.replace('V', '').lower()
    raise PithonTypeError("types comparables", f"{type_a} et {type_b}", "comparaison <")

def primitive_lte(args: list[EnvValue]) -> EnvValue:
    """Teste si la première valeur est inférieure ou égale à la seconde (nombres ou chaînes)."""
    if len(args) != 2:
        raise PithonTypeError("2 arguments", f"{len(args)} arguments", "comparaison <=")

    a, b = args
    if isinstance(a, VNumber) and isinstance(b, VNumber):
        return VBool(a.value <= b.value)
    if isinstance(a, VString) and isinstance(b, VString):
        return VBool(a.value <= b.value)

    type_a = type(a).__name__.replace('V', '').lower()
    type_b = type(b).__name__.replace('V', '').lower()
    raise PithonTypeError("types comparables", f"{type_a} et {type_b}", "comparaison <=")

def primitive_gte(args: list[EnvValue]) -> EnvValue:
    if len(args) != 2:
        raise PithonTypeError("2 arguments", f"{len(args)} arguments", "comparaison >=")

    a, b = args
    if isinstance(a, VNumber) and isinstance(b, VNumber):
        return VBool(a.value >= b.value)
    if isinstance(a, VString) and isinstance(b, VString):
        return VBool(a.value >= b.value)

    type_a = type(a).__name__.replace('V', '').lower()
    type_b = type(b).__name__.replace('V', '').lower()
    raise PithonTypeError("types comparables", f"{type_a} et {type_b}", "comparaison >=") 

def primitive_gt(args: list[EnvValue]) -> EnvValue:
    """Teste si la première valeur est strictement supérieure à la seconde (nombres ou chaînes)."""
    if len(args) != 2:
        raise PithonTypeError("2 arguments", f"{len(args)} arguments", "comparaison >")
    
    a, b = args
    if isinstance(a, VNumber) and isinstance(b, VNumber):
        return VBool(a.value > b.value)
    if isinstance(a, VString) and isinstance(b, VString):
        return VBool(a.value > b.value)
    
    type_a = type(a).__name__.replace('V', '').lower()
    type_b = type(b).__name__.replace('V', '').lower()
    raise PithonTypeError("types comparables", f"{type_a} et {type_b}", "comparaison >")
    
def primitive_abs(args: list[EnvValue]) -> EnvValue:
    if len(args) != 1 or not isinstance(args[0], VNumber):
        raise PithonTypeError("1 argument de type number", f"{len(args)} arguments", "abs")
    return VNumber(abs(args[0].value))

def primitive_pow(args: list[EnvValue]) -> EnvValue:
    if len(args) != 2 or not all(isinstance(arg, VNumber) for arg in args):
        raise PithonTypeError("2 arguments de type number", f"{len(args)} arguments", "puissance")
    return VNumber(args[0].value ** args[1].value)

def primitive_max(args: list[EnvValue]) -> EnvValue:
    if len(args) != 2 or not all(isinstance(arg, VNumber) for arg in args):
        raise PithonTypeError("2 arguments de type number", f"{len(args)} arguments", "max")
    return VNumber(max(args[0].value, args[1].value))

def primitive_min(args: list[EnvValue]) -> EnvValue:
    if len(args) != 2 or not all(isinstance(arg, VNumber) for arg in args):
        raise PithonTypeError("2 arguments de type number", f"{len(args)} arguments", "min")
    return VNumber(min(args[0].value, args[1].value))

def primitive_len(args: list[EnvValue]) -> EnvValue:
    if len(args) != 1:
        raise PithonTypeError("1 argument", f"{len(args)} arguments", "len")
    arg = args[0]
    if isinstance(arg, (VList, VTuple, VString)):
        return VNumber(len(arg.value))
    raise PithonTypeError("list, tuple ou string", type(arg).__name__, "len")

def primitive_head(args: list[EnvValue]) -> EnvValue:
    if len(args) != 1:
        raise PithonTypeError("1 argument", f"{len(args)} arguments", "head")
    arg = args[0]
    if isinstance(arg, (VList, VTuple)) and arg.value:
        return arg.value[0]
    raise PithonTypeError("liste ou tuple non vide", type(arg).__name__, "head")

def primitive_tail(args: list[EnvValue]) -> EnvValue:
    if len(args) != 1:
        raise PithonTypeError("1 argument", f"{len(args)} arguments", "tail")
    arg = args[0]
    if isinstance(arg, VList):
        return VList(arg.value[1:])
    if isinstance(arg, VTuple):
        return VTuple(arg.value[1:])
    raise PithonTypeError("liste ou tuple", type(arg).__name__, "tail")

def primitive_append(args: list[EnvValue]) -> EnvValue:
    if len(args) != 2 or not isinstance(args[0], VList):
        raise PithonTypeError("liste + élément", f"{type(args[0]).__name__} + ?", "append")
    return VList(args[0].value + [args[1]])

def primitive_concat(args: list[EnvValue]) -> EnvValue:
    if len(args) != 2:
        raise PithonTypeError("2 arguments", f"{len(args)} arguments", "concat")
    a, b = args
    if isinstance(a, VList) and isinstance(b, VList):
        return VList(a.value + b.value)
    if isinstance(a, VTuple) and isinstance(b, VTuple):
        return VTuple(a.value + b.value)
    if isinstance(a, VString) and isinstance(b, VString):
        return VString(a.value + b.value)
    raise PithonTypeError("deux séquences compatibles", f"{type(a).__name__} et {type(b).__name__}", "concat")

def primitive_upper(args: list[EnvValue]) -> EnvValue:
    if len(args) != 1 or not isinstance(args[0], VString):
        raise PithonTypeError("1 string", f"{len(args)} arguments", "upper")
    return VString(args[0].value.upper())

def primitive_lower(args: list[EnvValue]) -> EnvValue:
    if len(args) != 1 or not isinstance(args[0], VString):
        raise PithonTypeError("1 string", f"{len(args)} arguments", "lower")
    return VString(args[0].value.lower())

def primitive_str(args: list[EnvValue]) -> EnvValue:
    if len(args) != 1:
        raise PithonTypeError("1 argument", f"{len(args)} arguments", "str")
    return VString(str(args[0].value))

def primitive_range(args: list[EnvValue]) -> EnvValue:
    if not (1 <= len(args) <= 2):
        raise PithonTypeError("1 ou 2 arguments", f"{len(args)} arguments", "range")
    if not all(isinstance(arg, VNumber) for arg in args):
        raise PithonTypeError("number(s)", "autre type", "range")
    if len(args) == 1:
        end = int(args[0].value)
        return VList([VNumber(i) for i in range(end)])
    else: 
        start = int(arg[0].value)
        end = int(args[1].valut)
        return VList([VNumber(i) for i in range(start, end)])

def primitive_tuple(args: list[EnvValue]) -> EnvValue:
    if len(args) != 1 or not isinstance(args[0], VList):
        raise PithonTypeError("1 argument de type list", f"{len(args)} arguments", "tuple")
    return VTuple(tuple(args[0].value))

def primitive_print(args: list[EnvValue]) -> VNone:
    print(" ".join(str(arg.value) for arg in args))
    return VNone()
    