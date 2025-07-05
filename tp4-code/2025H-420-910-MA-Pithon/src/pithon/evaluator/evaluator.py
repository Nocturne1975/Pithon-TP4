from pithon.evaluator.envframe import EnvFrame
from pithon.evaluator.primitive import check_type, get_primitive_dict
from pithon.syntax import (
    PiAssignment, PiBinaryOperation, PiNumber, PiBool, PiStatement, PiProgram, PiSubscript, PiVariable,
    PiIfThenElse, PiNot, PiAnd, PiOr, PiWhile, PiNone, PiList, PiTuple, PiString, PiClassDef, PiAttribute, 
    PiFunctionDef, PiAttributeAssignment, PiFunctionCall, PiFor, PiBreak, PiContinue, PiIn, PiReturn
)
from pithon.evaluator.envvalue import EnvValue, VFunctionClosure, VList, VNone, VTuple, VNumber, VBool, VString, VClassDef, VObject, VMethodClosure
from pithon.exceptions import (PithonNameError, PithonError, PithonSyntaxError, PithonAttributeError, PithonBreakError, PithonCallError, 
     PithonIndexError, PithonTypeError, PithonValueError, PithonZeroDivisionError)

def initial_env() -> EnvFrame:
    """Crée et retourne l'environnement initial avec les primitives."""
    env = EnvFrame()
    env.vars.update(get_primitive_dict())
    return env

def lookup(env: EnvFrame, name: str) -> EnvValue:
    try:
        return env.lookup(name)
    except NameError:
        # Collecte toutes les variables disponibles
        available_vars = set()  # Utiliser un set pour éviter les doublons
        current_env = env
        while current_env:
            available_vars.update(current_env.vars.keys())
            current_env = current_env.parent

        if available_vars and name:
            # Suggestions plus intelligentes basées sur la distance de Levenshtein
            from difflib import get_close_matches
            suggestions = get_close_matches(name, available_vars, n=3, cutoff=0.6)
            if suggestions: 
                raise PithonNameError(f"Variable '{name}' non définie", suggestions)
        
        raise PithonNameError(f"Variable '{name}' non définie.")

def validate_function_call(funcdef: PiFunctionDef, args: list[EnvValue]):
    """Valide les arguments d'un appel de fonction"""
    min_args = len(funcdef.arg_names)
    max_args = min_args if not funcdef.vararg else float('inf')

    if len(args) < min_args: 
        raise PithonCallError(f"La fonction '{funcdef.name}' attend au moins {min_args} argument(s), "
                        f"{len(args)} fourni(s)")
    
    if len(args) > max_args: 
        raise PithonCallError(f"La fonction '{funcdef.name}' attend au maximum {min_args} argument(s), "
                        f"{len(args)} fourni(s)")


def insert(env: EnvFrame, name: str, value: EnvValue) -> None:
    """Insère une variable dans l'environnement."""
    env.insert(name, value)


def evaluate(node: PiProgram, env: EnvFrame) -> EnvValue:
    """Évalue un programme ou une liste d'instructions."""
    if isinstance(node, list):
        last_value = VNone(value=None)
        for stmt in node:
            last_value = evaluate_stmt(stmt, env)
        return last_value
    elif isinstance(node, PiStatement):
        return evaluate_stmt(node, env)
    else:
        raise PithonTypeError("PiProgram ou PiStatement", type(node).__name__)

def evaluate_stmt(node: PiStatement, env: EnvFrame) -> EnvValue:
    """Évalue une instruction ou expression Pithon."""

    if isinstance(node, PiNumber):
        return VNumber(node.value)

    elif isinstance(node, PiBool):
        return VBool(node.value)

    elif isinstance(node, PiNone):
        return VNone(node.value)

    elif isinstance(node, PiString):
        return VString(node.value)

    elif isinstance(node, PiList):
        elements = [evaluate_stmt(e, env) for e in node.elements]
        return VList(elements)

    elif isinstance(node, PiTuple):
        elements = tuple(evaluate_stmt(e, env) for e in node.elements)
        return VTuple(elements)

    elif isinstance(node, PiVariable):
        return lookup(env, node.name)

    elif isinstance(node, PiBinaryOperation):
        fct_call = PiFunctionCall(
        function=PiVariable(name=node.operator),
        args=[node.left, node.right]
        )
        return evaluate_stmt(fct_call, env)

    elif isinstance(node, PiAssignment):
        value = evaluate_stmt(node.value, env)
        insert(env, node.name, value)
        return value

    elif isinstance(node, PiIfThenElse):
        cond = evaluate_stmt(node.condition, env)
        cond = check_type(cond, VBool)
        branch = node.then_branch if cond.value else node.else_branch
        last_value = evaluate(branch, env)
        return last_value

    elif isinstance(node, PiNot):
        operand = evaluate_stmt(node.operand, env)
        # Vérifie le type pour l'opérateur 'not'
        _check_valid_piandor_type(operand)
        return VBool(not operand.value) # type: ignore

    elif isinstance(node, PiAnd):
        left = evaluate_stmt(node.left, env)
        _check_valid_piandor_type(left)
        if not left.value: # type: ignore
            return left
        right = evaluate_stmt(node.right, env)
        _check_valid_piandor_type(right)
        return right

    elif isinstance(node, PiOr):
        left = evaluate_stmt(node.left, env)
        _check_valid_piandor_type(left)
        if left.value: # type: ignore
            return left
        right = evaluate_stmt(node.right, env)
        _check_valid_piandor_type(right)
        return right

    elif isinstance(node, PiWhile):
        return _evaluate_while(node, env)

    elif isinstance(node, PiFunctionDef):
        closure = VFunctionClosure(node, env)
        insert(env, node.name, closure)
        return VNone(value=None)

    elif isinstance(node, PiReturn):
        value = evaluate_stmt(node.value, env)
        raise ReturnException(value)

    elif isinstance(node, PiFunctionCall):
        func_val = evaluate_stmt(node.function, env)
        args = [evaluate_stmt(arg, env) for arg in node.args]
        
        # Primitive Function
        if callable(func_val):
            return func_val(args)
        
        if isinstance(func_val, VMethodClosure):
            funcdef = func_val.function.funcdef
            closure_env = func_val.function.closure_env
            
            call_env = EnvFrame(parent=closure_env)
            # Ajouter 'self' comme premier argument
            all_args = [func_val.instance] + args
            # Assigner les arguments
            for i, arg_name in enumerate(funcdef.arg_names):
                if i < len(all_args):
                    call_env.insert(arg_name, all_args[i])
                else:
                    raise PithonCallError(f"Argument manquant pour la méthode '{funcdef.name}'")
            # Gérer les arguments variables si nécessaire
            if funcdef.vararg:
                varargs = VList(all_args[len(funcdef.arg_names):])
                call_env.insert(funcdef.vararg, varargs)
            elif len(all_args) > len(funcdef.arg_names):
                raise PithonCallError(f"Trop d'arguments pour la méthode '{funcdef.name}'")
            
            result = VNone(value=None)
            try:
                for stmt in funcdef.body:
                    result = evaluate_stmt(stmt, call_env)
            except ReturnException as ret:
                return ret.value
            return result
        
        # Constructeur de classe ou fonction utilisateur
        if isinstance(func_val, VFunctionClosure):
            funcdef = func_val.funcdef
            closure_env = func_val.closure_env
            call_env = EnvFrame(parent=closure_env)
            # Assigner les arguments
            for i, arg_name in enumerate(funcdef.arg_names):
                if i < len(args):
                    call_env.insert(arg_name, args[i])
                else:
                    raise PithonCallError(f"Argument manquant pour la fonction '{funcdef.name}'")
            # Gérer les arguments variables
            if funcdef.vararg:
                varargs = VList(args[len(funcdef.arg_names):])
                call_env.insert(funcdef.vararg, varargs)
            elif len(args) > len(funcdef.arg_names):
                raise PithonCallError(f"Trop d'arguments pour la fonction '{funcdef.name}'")
            
            result = VNone(value=None)
            try:
                for stmt in funcdef.body:
                    result = evaluate_stmt(stmt, call_env)
            except ReturnException as ret:
                return ret.value
            return result
        
        # Constructeur de classe
        if isinstance(func_val, VClassDef):
            instance = VObject(class_def=func_val, attributes={})

            if '__init__' in func_val.methods:
                init_method = func_val.methods['__init__']
                init_args = [instance] + args

                funcdef = init_method.funcdef
                closure_env = init_method.closure_env
                call_env = EnvFrame(parent=closure_env)

                for i, arg_name in enumerate(funcdef.arg_names):
                    if i < len(init_args):
                        call_env.insert(arg_name, init_args[i])
                    else: 
                        raise PithonCallError(f"Argument manquant pour le constructeur de '{func_val.name}'")
                
                if funcdef.vararg:
                    varargs = VList(init_args[len(funcdef.arg_names):])
                    call_env.insert(funcdef.vararg, varargs)
                elif len(init_args) > len(funcdef.arg_names):
                    raise PithonCallError(f"Trop d'arguments pour le constructeur de '{func_val.name}'")
                
                try:
                    for stmt in funcdef.body:
                        evaluate_stmt(stmt, call_env)
                except ReturnException:
                    pass    # __init__ ne devrait pas retourner de valeur

            return instance
        
        raise PithonTypeError("fonction", type(func_val).__name__, "appel de fonction")

    elif isinstance(node, PiFor):
        return _evaluate_for(node, env)

    elif isinstance(node, PiBreak):
        raise BreakException()

    elif isinstance(node, PiContinue):
        raise ContinueException()

    elif isinstance(node, PiIn):
        return _evaluate_in(node, env)

    elif isinstance(node, PiSubscript):
        return _evaluate_subscript(node, env)
        
    elif isinstance(node, PiClassDef):
        # Créer un nouvel environnement pour la classe
        class_env = EnvFrame(parent=env)
        # Évaluer toutes les méthodes et les stocker
        methods = {}
        for method in node.methods:
            method_closure = VFunctionClosure(method, class_env)
            methods[method.name] = method_closure
        
        class_def = VClassDef(name=node.name, methods=methods)
        insert(env, node.name, class_def)
        return VNone(value=None)

    elif isinstance(node, PiAttribute):
        try:
            obj = evaluate_stmt(node.object, env)
            
            if isinstance(obj, VObject):
                # Chercher d'abord dans les attributs de l'instance
                if node.attr in obj.attributes:
                    return obj.attributes[node.attr]
                # puis dans les méthodes de la classe
                elif node.attr in obj.class_def.methods:
                    method = obj.class_def.methods[node.attr]
                    return VMethodClosure(method, obj)
                else:
                    raise PithonAttributeError(f"L'objet '{obj.class_def.name}' n'a pas d'attribut '{node.attr}'")
            else:
                type_name = type(obj).__name__.replace('V', '').lower()
                raise PithonTypeError("objet", type_name, "accès attribut")
        except (PithonAttributeError, PithonTypeError):
            raise
        except Exception as e:
            raise PithonError(f"Erreur lors de l'accès à l'attribut: {str(e)}")
    
    elif isinstance(node, PiAttributeAssignment):
        obj = evaluate_stmt(node.object, env)
        value = evaluate_stmt(node.value, env)

        if isinstance(obj, VObject):
            obj.attributes[node.attr] = value
            return value
        else:
            type_name = type(obj).__name__.replace('V', '').lower()
            raise PithonTypeError("objet", type_name, "assignation d'attribut")
        
    elif isinstance(node, PiAttributeAssignment):
        obj = evaluate_stmt(node.object, env)
        value = evaluate_stmt(node.value, env)
        if not isinstance(obj, VObject):
            raise PithonTypeError("objet", type(obj).__name__, "attribution d'attribut")
        obj.fields[node.attr] = value
        return value

    else:
        raise PithonTypeError("nœud supporté", type(node).__name__)


def _check_valid_piandor_type(obj):
    """Vérifie que le type est valide pour 'and'/'or'."""
    if not isinstance(obj, (VBool, VNumber, VString, VNone, VList, VTuple)):
        type_name = type(obj).__name__.replace('V', '').lower()
        raise PithonTypeError("bool, number, string, none, list ou tuple", type_name, "opérateur 'and'/'or'")


def _evaluate_while(node: PiWhile, env: EnvFrame) -> EnvValue:
    """Évalue une boucle while."""
    last_value = VNone(value=None)
    while True:
        cond = evaluate_stmt(node.condition, env)
        cond = check_type(cond, VBool)
        if not cond.value:
            break
        try:
            last_value = evaluate(node.body, env)
        except BreakException:
            break
        except ContinueException:
            continue
    return last_value


def _evaluate_for(node: PiFor, env: EnvFrame) -> EnvValue:
    """Évalue une boucle for."""
    iterable_val = evaluate_stmt(node.iterable, env)
    if not isinstance(iterable_val, (VList, VTuple)):
        type_name = type(iterable_val).__name__.replace('V', '').lower()
        raise PithonTypeError("list ou tuple", type_name, "boucle for")
    
    last_value = VNone(value=None)
    iterable = iterable_val.value
    for item in iterable:
        env.insert(node.var, item)  # Pas de nouvel environnement pour la variable de boucle
        try:
            last_value = evaluate(node.body, env)
        except BreakException:
            break
        except ContinueException:
            continue
    return last_value


def _evaluate_subscript(node: PiSubscript, env: EnvFrame) -> EnvValue:
    """Évalue une opération d'indexation (subscript)."""
    collection = evaluate_stmt(node.collection, env)
    index = evaluate_stmt(node.index, env)
    
    # Indexation pour liste, tuple ou chaîne
    if isinstance(collection, VList):
        idx = check_type(index, VNumber)
        idx_val = int(idx.value)
        if idx_val < 0 or idx_val >= len(collection.value):
            raise PithonIndexError(f"Index {idx_val} hors limites pour une liste de taille {len(collection.value)}")
        return collection.value[idx_val]
               
    elif isinstance(collection, VTuple):
        idx = check_type(index, VNumber)
        idx_val = int(idx.value)
        if idx_val < 0 or idx_val >= len(collection.value):
            raise PithonIndexError(f"Index {idx_val} hors limites pour un tuple de taille {len(collection.value)}")
        return collection.value[idx_val]
        
    elif isinstance(collection, VString):
        idx = check_type(index, VNumber)
        idx_val = int(idx.value)
        if idx_val < 0 or idx_val >= len(collection.value):
            raise PithonIndexError(f"Index {idx_val} hors limites pour une chaîne de longueur {len(collection.value)}")
        return VString(collection.value[idx_val])
    else:
        type_name = type(collection).__name__.replace('V', '').lower()
        raise PithonTypeError("list, tuple ou string", type_name, "indexation")


def _evaluate_in(node: PiIn, env: EnvFrame) -> EnvValue:
    """Évalue l'opérateur 'in'."""
    container = evaluate_stmt(node.container, env)
    element = evaluate_stmt(node.element, env)
    
    if isinstance(container, (VList, VTuple)):
        return VBool(element in container.value)
    elif isinstance(container, VString):
        if isinstance(element, VString):
            return VBool(element.value in container.value)
        else:
            return VBool(False)
    else:
        type_name = type(container).__name__.replace('V', '').lower()
        raise PithonTypeError("list, tuple ou string", type_name, "opérateur 'in'")


# Classes d'exception pour le contrôle de flux
class ReturnException(Exception):
    """Exception pour retourner une valeur depuis une fonction."""
    def __init__(self, value):
        self.value = value


class BreakException(Exception):
    """Exception pour sortir d'une boucle (break)."""
    pass


class ContinueException(Exception):
    """Exception pour passer à l'itération suivante (continue)."""
    pass