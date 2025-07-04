from pathlib import Path
import sys
import os
from pithon.evaluator.evaluator import initial_env, evaluate
from pithon.parser.simpleparser import SimpleParser
from pithon.syntax import PiAssignment

def run_cli(ast_only=False):
    parser = SimpleParser()
    env = initial_env()
    
    mode = " (mode AST)" if ast_only else ""
    print(f"🐍 Pithon CLI!{mode}")

    while True:
        try:
            line = input("> ").strip()
            if line.lower() in ("exit", "quit"):
                print("Au revoir 👋.")
                break
            if not line:
                continue
            tree = parser.parse(line)
            if ast_only:
                print(tree)
                continue
            result = evaluate(tree, env)
            if not isinstance(tree, PiAssignment):
                print(result)
        except KeyboardInterrupt:
            print("\nAu revoir 👋.")
            break
        except SyntaxError as e:
            print(f"Erreur de syntaxe: {e}")
        except NameError as e:
            print(f"Erreur de nom: {e}")
        except TypeError as e:
            print(f"Erreur de type: {e}")
        except ValueError as e: 
            print(f"Erreur de valeur: {e}")
        except ZeroDivisionError as e:
            print(f"Erreur de division: {e}")
        except AttributeError as e: 
            print(f"Erreur d'attribut: {e}")
        except Exception as e:
            print(f"Erreur inattendue: {e}")

def run_file(filename, ast_only=False):
    parser = SimpleParser()
    env = initial_env()

    try:
        with open(filename, "r", encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Erreur: Le fichier '{filename}' n'existe pas.")
        return
    except IOError as e:
        print(f"Erreur de lecture du fichier '{filename}': {e}")
        return
    
    try:
        tree = parser.parse(source)
        if ast_only:
            print(tree)
            return
        evaluate(tree, env)
    except SyntaxError as e: 
        print(f"Erreur de syntaxe dans '{filename}': {e}")
    except Exception as e:
        print(f"Erreur lors de l'execution de '{filename}': {e}")
        
def run_tests():
    test_dir = Path("tests/fixtures/programs")
    files = [f for f in os.listdir(test_dir) if f.endswith(".py")]
    if not files:
        print("Aucun fichier de test trouvé.")
        return
    for fname in sorted(files):
        path = os.path.join(test_dir, fname)
        print(f"--- Test : {fname} ---")
        try:
            run_file(path)
        except Exception as e:
            print(f"Erreur dans {fname}: {e}")

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            run_tests()
        elif sys.argv[1] == "--ast":
            if len(sys.argv) > 2:
                run_file(sys.argv[2], ast_only=True)
            else:
                run_cli(ast_only=True)
        else:
            run_file(sys.argv[1], ast_only=False)
    else:
        run_cli()

if __name__ == "__main__":
    main()