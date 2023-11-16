import datetime
from bson import ObjectId
import pandas as pd
from model.livro import Livro
from model.emprestimo import Emprestimo
from conexion.mongo_queries import MongoQueries
from controller.controller_livro import Controller_Livro
from controller.controller_usuario import Controller_Usuario
from reports.relatorios import Relatorio

class Controller_Emprestimo:
    def __init__(self):
        self.mongo = MongoQueries()
        self.relatorio = Relatorio()
        self.ctrl_usuario = Controller_Usuario()
        self.ctrl_livro = Controller_Livro()
        
    def inserir_emprestimo(self) -> Emprestimo:
        # Cria uma nova conexão com o banco
        self.mongo.connect()
        
        emprestimo_cadastrado = self.cadastrar_emprestimo()
        if(emprestimo_cadastrado == None):
            return None

        id_livro = int(emprestimo_cadastrado.get_livro().get_id_livro())
        id_usuario = int(emprestimo_cadastrado.get_usuario().get_id_usuario())
        data_emprestimo = emprestimo_cadastrado.get_data_emprestimo()
        data_devolucao_sugerida = emprestimo_cadastrado.get_data_devolucao()

        proximo = self.mongo.db["emprestimos"].aggregate([
                                                    {
                                                        '$group': {
                                                            '_id': '$emprestimos', 
                                                            'proximo_emprestimo': {
                                                                '$max': '$id_emprestimo'
                                                            }
                                                        }
                                                    }, {
                                                        '$project': {
                                                            'proximo_emprestimo': {
                                                                '$sum': [
                                                                    '$proximo_emprestimo', 1
                                                                ]
                                                            }, 
                                                            '_id': 0
                                                        }
                                                    }
                                                ])

        proximo = int(list(proximo)[0]['proximo_emprestimo'])
        
        # Insere e Recupera o código do novo registro
        id_registro = self.mongo.db["emprestimos"].insert_one({"id_emprestimo": proximo, "id_livro": id_livro, "id_usuario": id_usuario, "data_emprestimo": data_emprestimo, "data_devolucao_sugerida": data_devolucao_sugerida})
        # Recupera os dados do novo registro criado transformando em um DataFrame
        novo_registro = Controller_Emprestimo.get_emprestimo_from_dataframe(self.mongo, proximo)
        print(novo_registro.to_string())
        self.mongo.close()
        # Retorna o objeto novo_produto para utilização posterior, caso necessário
        return novo_registro

    def atualizar_emprestimo(self) -> Emprestimo:
        # Cria uma nova conexão com o banco que permite alteração
        self.mongo.connect()

        # Solicita ao usuário o código da entidade a ser alterada
        id_emprestimo = int(input("Código do Empréstimo que irá alterar: "))        

        # Verifica se o registro existe na base de dados
        if not Controller_Emprestimo.verifica_existencia_emprestimo(self.mongo, id_emprestimo):
            self.mongo.close()
            print(f"O código {id_emprestimo} não existe.")
            return None        

        emprestimo_atualizado = self.cadastrar_emprestimo()
        if(emprestimo_atualizado == None):
            return None

        # Atualiza a descrição do produto existente
        self.mongo.db["emprestimos"].update_one({"id_emprestimo": id_emprestimo}, {"$set": {"id_livro": emprestimo_atualizado.get_livro().get_id_livro(), "id_usuario": emprestimo_atualizado.get_usuario().get_id_usuario(), "data_emprestimo": emprestimo_atualizado.get_data_emprestimo(), "data_devolucao_sugerida": emprestimo_atualizado.get_data_devolucao()}})

        # Cria um novo objeto
        registro_atualizado = Controller_Emprestimo.get_emprestimo_from_dataframe(self.mongo, id_emprestimo)
        # Exibe os atributos do novo produto
        print(registro_atualizado.to_string())
        self.mongo.close()
        # Retorna o objeto
        return registro_atualizado

    def excluir_livro(self):
        # Cria uma nova conexão com o banco que permite alteração
        self.mongo.connect()

        # Solicita o código da entidade a ser excluida
        id_emprestimo = int(input("Código do Empréstimo que irá excluir: ")) 

        # Verifica se o produto existe na base de dados
        if not Controller_Emprestimo.verifica_existencia_emprestimo(self.mongo, id_emprestimo):
            self.mongo.close()
            print(f"O código {id_emprestimo} não existe.")
            return
        
        # Recupera os dados transformando em um DataFrame
        emprestimo_excluido = Controller_Emprestimo.get_emprestimo_from_dataframe(self.mongo, id_emprestimo)
        # Revome da tabela
        self.mongo.db["emprestimos"].delete_one({"id_emprestimo": id_emprestimo})
        # Exibe os atributos do produto excluído
        print("Livro removido com Sucesso!")
        print(emprestimo_excluido.to_string())
        self.mongo.close()

    def cadastrar_emprestimo(self) -> Emprestimo:
        #Solicita os dados de cadastro
        print("Informe os dados do empréstimo.\n")

        # Lista os usuarios existentes para inserir no item de emprestimo
        self.relatorio.get_relatorio_usuarios()
        codigo_usuario = str(input("\nDigite o código do usuário a fazer o empréstimo: "))
        usuario = Controller_Usuario.valida_usuario(self.mongo, codigo_usuario)
        if usuario == None:
            return None

        print("\n\n")

        self.relatorio.get_relatorio_livros_disponiveis()
        codigo_livro = str(input("\nDigite o código do livro a ser emprestado: "))
        livro = Controller_Livro.valida_livro_disponivel(self.mongo, codigo_livro)
        if livro == None:
            return None

        data_emprestimo = input("Data de empréstimo (DD/MM/YYYY): ")
        while not Controller_Emprestimo.valida_data_format(data_emprestimo):
            print("\nVocê tentou inserir um formato inválido, tente novamente.\n")
            data_emprestimo = input("Data de empréstimo (DD/MM/YYYY): ")

        data_devolucao = input("Data prevista de devolução (DD/MM/YYYY): ")
        while not Controller_Emprestimo.valida_data_format(data_devolucao):
            print("\nVocê tentou inserir um formato inválido, tente novamente.\n")
            data_devolucao = input("Data prevista de devolução (DD/MM/YYYY): ")
        
        while not Controller_Emprestimo.valida_data_entrega_devolucao(data_emprestimo, data_devolucao):
            print("\nVocê tentou inserir uma data de devolução menor que a data de entrega, tente novamente.\n")
            data_devolucao = input("Data prevista de devolução (DD/MM/YYYY): ")

        return Emprestimo(0, livro, usuario, data_emprestimo, data_devolucao)


    def verifica_existencia_livro(mongo:MongoQueries, codigo:int=None, external: bool = False) -> bool:
        if external:
            # Cria uma nova conexão com o banco que permite alteração
            mongo.connect()

        dataframe = pd.DataFrame(mongo.db["livros"].find({"id_livro":int(codigo)}, {"id_livro": 1, "_id": 0}))

        if external:
            # Fecha a conexão com o Mongo
            mongo.close()

        return not dataframe.empty

    @staticmethod
    def recupera_registro(mongo:MongoQueries, _id:ObjectId=None) -> pd.DataFrame:
        # Recupera os dados do registro transformando em um DataFrame
        dataframe = pd.DataFrame(list(mongo.db["emprestimos"].find({"_id":_id}, {"id_emprestimo": 1, "id_livro": 1, "id_usuario": 1, "data_emprestimo": 1, "data_devolucao_sugerida": 1, "_id": 0})))
        return dataframe


    @staticmethod   
    def recupera_emprestimo_codigo(mongo:MongoQueries, codigo:int=None, external: bool = False) -> pd.DataFrame:
        if external:
            # Cria uma nova conexão com o banco que permite alteração
            mongo.connect()

        # Recupera os dados do registro transformando em um DataFrame
        dataframe = pd.DataFrame(list(mongo.db["emprestimos"].find({"id_emprestimo":int(codigo)}, {"id_emprestimo": 1, "id_livro": 1, "id_usuario": 1, "data_emprestimo": 1, "data_devolucao_sugerida": 1, "_id": 0})))

        if external:
            # Fecha a conexão com o Mongo
            mongo.close()

        return dataframe    
    
    @staticmethod
    def verifica_existencia_emprestimo(mongo:MongoQueries, id_emprestimo:int=None) -> bool:
        df_emprestimo = Controller_Emprestimo.recupera_emprestimo_codigo(mongo, id_emprestimo)
        return not df_emprestimo.empty
    
    @staticmethod
    def get_emprestimo_from_dataframe(mongo:MongoQueries, id_emprestimo:int=None) -> Emprestimo:
        df_emprestimo = Controller_Emprestimo.recupera_emprestimo_codigo(mongo, id_emprestimo)
        livro = Controller_Livro.get_livro_from_dataframe(mongo, int(df_emprestimo.id_livro.values[0]))
        usuario = Controller_Usuario.get_usuario_from_dataframe(mongo, int(df_emprestimo.id_usuario.values[0]))
        return Emprestimo(int(df_emprestimo.id_emprestimo.values[0]), livro, usuario, df_emprestimo.data_emprestimo.values[0], df_emprestimo.data_devolucao_sugerida.values[0])

    @staticmethod
    def valida_emprestimo(mongo:MongoQueries, codigo_emprestimo:int=None) -> Emprestimo:
        if not Controller_Emprestimo.verifica_existencia_emprestimo(mongo, codigo_emprestimo):
            print(f"O empréstimo de código {codigo_emprestimo} não existe na base.")
            return None
        else:
            return Controller_Emprestimo.get_emprestimo_from_dataframe(mongo, codigo_emprestimo)

    @staticmethod
    def valida_data_format(data_string:str=None) -> bool:
        try:
            partes_data = data_string.split("/")
            dia = int(partes_data[0])
            mes = int(partes_data[1])
            ano = int(partes_data[2])

            datetime.datetime(ano, mes, dia)
            return True
        
        except:
            print("Erro ao validar data.")
            return False
        
    @staticmethod
    def valida_data_entrega_devolucao(data_entrega: str, data_devolucao: str) -> bool:
        try:
            def converter_data(data: str) -> datetime:
                partes_data = data.split("/")
                dia = int(partes_data[0])
                mes = int(partes_data[1])
                ano = int(partes_data[2])
                return datetime.datetime(ano, mes, dia)

            data_entrega = converter_data(data_entrega)
            data_devolucao = converter_data(data_devolucao)

            if data_devolucao < data_entrega:
                # Formata a data para exibição
                data_entrega_formatada = data_entrega.strftime('%d/%m/%Y')
                data_devolucao_formatada = data_devolucao.strftime('%d/%m/%Y')
                # Exibe mensagem de erro
                raise Exception(f"Data de Devolução ({data_devolucao_formatada}) menor que a Data de Entrega ({data_entrega_formatada})")

            return True

        except Exception as error:
            print(f"\nErro ao validar data: {error}")
            return False
