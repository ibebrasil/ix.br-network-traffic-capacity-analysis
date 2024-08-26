import os
import subprocess

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def run_module(module_number):
    script_name = f"{module_number}_"
    for filename in os.listdir('.'):
        if filename.startswith(script_name) and filename.endswith('.py'):
            print(f"Executando {filename}...")
            subprocess.run(['python', filename])
            input("Pressione Enter para continuar...")
            return
    print(f"Módulo {module_number} não encontrado.")
    input("Pressione Enter para continuar...")

def run_all_modules():
    for i in range(1, 6):
        run_module(i)

def main_menu():
    while True:
        clear_screen()
        print("=== Menu Principal ===")
        print("1. PeeringDB Extract Data")
        print("2. IX-BR Entities Extract Data")
        print("3. IX-BR Slugs Extract Data")
        print("4. IX-BR Charts Images Download")
        print("5. IX-BR Charts Images Extract Data")
        print("6. ALL - Executar todos os módulos")
        print("0. EXIT - Sair")
        
        choice = input("Escolha uma opção: ")
        
        if choice == '0':
            print("Saindo do programa...")
            break
        elif choice in ['1', '2', '3', '4', '5']:
            run_module(int(choice))
        elif choice == '6':
            run_all_modules()
        else:
            print("Opção inválida. Tente novamente.")
            input("Pressione Enter para continuar...")

if __name__ == "__main__":
    main_menu()
