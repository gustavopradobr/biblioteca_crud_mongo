from utils import config
from utils.splash_screen import SplashScreen
from reports.relatorios import Relatorio
from controller.controller_livro import Controller_Livro
from controller.controller_usuario import Controller_Usuario
from controller.controller_emprestimo import Controller_Emprestimo
from controller.controller_devolucao import Controller_Devolucao

tela_inicial = SplashScreen()
relatorio = Relatorio()
ctrl_livro = Controller_Livro()
ctrl_usuario = Controller_Usuario()
ctrl_emprestimo = Controller_Emprestimo()
ctrl_devolucao = Controller_Devolucao()

def reports(opcao_relatorio:int=0):

        if opcao_relatorio == 1:
            relatorio.get_relatorio_livros()
        if opcao_relatorio == 2:
            relatorio.get_relatorio_usuarios()
        if opcao_relatorio == 3:
            relatorio.get_relatorio_emprestimos()
        if opcao_relatorio == 4:
            relatorio.get_relatorio_devolucoes()
        if opcao_relatorio == 5:
            relatorio.get_relatorio_livros_disponiveis() 

        input("\nPressione Enter para fechar o relatório")

def inserir(opcao_inserir:int=0):

     while True:
        if opcao_inserir == 1:
            novo_livro = ctrl_livro.inserir_livro()
        elif opcao_inserir == 2:
            novo_cliente = ctrl_usuario.inserir_usuario()
        elif opcao_inserir == 3:
            novo_emprestimo = ctrl_emprestimo.inserir_emprestimo()
        elif opcao_inserir == 4:
            nova_devolucao = ctrl_devolucao.inserir_devolucao()
        else:
            print("Opção inválida. Tente novamente.")
            break

        continuar = input("Deseja fazer mais uma inserção? (S/N): ")
        if continuar.strip().lower() != "s":
            break
        config.clear_console(0)
            

def atualizar(opcao_atualizar:int=0) -> bool:

    while True:
        if opcao_atualizar == 1:
            if not relatorio.get_relatorio_livros():
                return False
            livro_atualizado = ctrl_livro.atualizar_livro()
        elif opcao_atualizar == 2:
            if not relatorio.get_relatorio_usuarios():
                return False
            usuario_atualizado = ctrl_usuario.atualizar_usuario()
        elif opcao_atualizar == 3:
            if not relatorio.get_relatorio_emprestimos():
                return False
            emprestimo_atualizado = ctrl_emprestimo.atualizar_emprestimo()
        elif opcao_atualizar == 4:
            if not relatorio.get_relatorio_devolucoes():
                return False
            devolucao_atualizada = ctrl_devolucao.atualizar_devolucao()
        else:
            print("Opção inválida. Tente novamente.")
            break

        continuar = input("Deseja fazer mais uma atualização? (S/N): ")
        if continuar.strip().lower() != "s":
            break
        config.clear_console(0)
    return True

def excluir(opcao_excluir:int=0) -> bool:

    while True:
        if opcao_excluir == 1:
            if not relatorio.get_relatorio_livros():
                return False
            ctrl_livro.excluir_livro()
        elif opcao_excluir == 2:
            if not relatorio.get_relatorio_usuarios():
                return False
            ctrl_usuario.excluir_usuario()
        elif opcao_excluir == 3:
            if not relatorio.get_relatorio_emprestimos():
                return False
            ctrl_emprestimo.excluir_emprestimo()
        elif opcao_excluir == 4:
            if not relatorio.get_relatorio_devolucoes():
                return False
            ctrl_devolucao.excluir_devolucao()
        else:
            print("Opção inválida. Tente novamente.")
            break

        continuar = input("Deseja fazer mais uma exclusão? (S/N): ")
        if continuar.strip().lower() != "s":
            break
        config.clear_console(0)
    return True

def run():
    print(tela_inicial.get_updated_screen())
    config.clear_console()

    while True:
        try:
            print(config.MENU_PRINCIPAL)
            opcao = int(input("Escolha uma opção [1-5]: "))
            config.clear_console(1)
            
            if opcao == 1: # Relatórios
                
                print(config.MENU_RELATORIOS)
                opcao_relatorio = int(input("Escolha uma opção [0-5]: "))
                config.clear_console(1)

                reports(opcao_relatorio)

                config.clear_console(1)

            elif opcao == 2: # Inserir Novos Registros
                
                print(config.MENU_ENTIDADES)
                opcao_inserir = int(input("Escolha uma opção [1-4]: "))
                config.clear_console(1)

                inserir(opcao_inserir=opcao_inserir)

                config.clear_console(0)
                print(tela_inicial.get_updated_screen())
                config.clear_console()

            elif opcao == 3: # Atualizar Registros

                print(config.MENU_ENTIDADES)
                opcao_atualizar = int(input("Escolha uma opção [1-4]: "))
                config.clear_console(1)

                if not atualizar(opcao_atualizar=opcao_atualizar):
                    config.clear_console()
                else:
                    config.clear_console(0)

                print(tela_inicial.get_updated_screen())
                config.clear_console()

            elif opcao == 4: # Excluir Registros
                print(config.MENU_ENTIDADES)
                opcao_excluir = int(input("Escolha uma opção [1-4]: "))
                config.clear_console(1)

                if not excluir(opcao_excluir=opcao_excluir):
                    config.clear_console()
                else:
                    config.clear_console(0)

                print(tela_inicial.get_updated_screen())
                config.clear_console()

            elif opcao == 5: # Sair do Sistema

                print(tela_inicial.get_updated_screen())
                config.clear_console()
                exit(0)

            else:
                print("Escolha uma opção entre 1-5. \n\n")

        except KeyboardInterrupt:
            print("\n\nObrigado por utilizar o nosso sistema. \n\n")
            exit(0)

        except SystemExit:
            print("\n\nObrigado por utilizar o nosso sistema. \n\n")
            exit(0)

        # Captura erro de tipo
        except ValueError:
            print("\n\nOpção incorreta. Tente novamente. \n\n")
        
        # Captura erro genérico
        except Exception as err:
            print("\n\n Erro:", err)

if __name__ == "__main__":
    run()