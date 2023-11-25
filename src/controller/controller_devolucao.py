import datetime
from bson import ObjectId
import pandas as pd
from model.emprestimo import Emprestimo
from model.devolucao import Devolucao
from controller.controller_emprestimo import Controller_Emprestimo
from conexion.mongo_queries import MongoQueries
from controller.controller_usuario import Controller_Usuario
from reports.relatorios import Relatorio

class Controller_Devolucao:
    def __init__(self):
        self.mongo = MongoQueries()
        self.relatorio = Relatorio()
        self.ctrl_emprestimo = Controller_Emprestimo()
        
    def inserir_devolucao(self) -> Devolucao:
        # Cria uma nova conexão com o banco
        self.mongo.connect()
        
        devolucao_cadastrada = self.cadastrar_devolucao()
        if(devolucao_cadastrada == None):
            return None

        id_emprestimo = int(devolucao_cadastrada.get_emprestimo().get_id_emprestimo())
        data_devolucao = devolucao_cadastrada.get_data_devolucao()

        proximo = self.mongo.db["devolucoes"].aggregate([
                                                    {
                                                        '$group': {
                                                            '_id': '$devolucoes', 
                                                            'proximo_devolucao': {
                                                                '$max': '$id_devolucao'
                                                            }
                                                        }
                                                    }, {
                                                        '$project': {
                                                            'proximo_devolucao': {
                                                                '$sum': [
                                                                    '$proximo_devolucao', 1
                                                                ]
                                                            }, 
                                                            '_id': 0
                                                        }
                                                    }
                                                ])

        proximo = int(list(proximo)[0]['proximo_devolucao'])
        
        data_devolucao_format = datetime.datetime.strptime(data_devolucao, '%d/%m/%Y')

        # Insere e Recupera o código do novo registro
        id_registro = self.mongo.db["devolucoes"].insert_one({"id_devolucao": proximo, "id_emprestimo": id_emprestimo, "data_devolucao": data_devolucao_format})
        # Recupera os dados do novo registro criado transformando em um DataFrame
        novo_registro = Controller_Devolucao.get_devolucao_from_dataframe(self.mongo, proximo)
        print(novo_registro.to_string())
        self.mongo.close()
        # Retorna o objeto novo_produto para utilização posterior, caso necessário
        return novo_registro

    def atualizar_devolucao(self) -> Devolucao:
        # Cria uma nova conexão com o banco que permite alteração
        self.mongo.connect()

        # Solicita ao usuário o código da entidade a ser alterada
        id_devolucao = int(input("Código da Devolução que irá alterar: "))        

        # Verifica se a entidade existe na base de dados
        if not Controller_Devolucao.verifica_existencia_devolucao(self.mongo, id_devolucao):
            self.mongo.close()
            print(f"O código {id_devolucao} não existe.")
            return None

        devolucao_original = Controller_Devolucao.get_devolucao_from_dataframe(self.mongo, id_devolucao)

        self.relatorio.get_relatorio_emprestimos()
        codigo_emprestimo = str(input("\nDigite o novo código do empréstimo: "))

        emprestimo = Controller_Emprestimo.valida_emprestimo(self.mongo, codigo_emprestimo)
        if emprestimo == None:
            return None
        
        if int(codigo_emprestimo) == devolucao_original.get_emprestimo().get_id_emprestimo():
            print("O empréstimo se manteve o mesmo.")
        elif not Controller_Emprestimo.verifica_emprestimo_aberto(self.mongo, codigo_emprestimo):
            print("O empréstimo digitado não está em aberto (já possui devolução). Tente novamente com um empréstimo em aberto.")
            return None

        data_devolucao = input("Digite a nova Data da devolução (DD/MM/YYYY): ")
        while not Controller_Emprestimo.valida_data_format(data_devolucao):
            print("\nVocê tentou inserir um formato inválido, tente novamente.\n")
            data_devolucao = input("Digite a nova Data da devolução (DD/MM/YYYY): ")

        devolucao_cadastrada = Devolucao(0, emprestimo, data_devolucao)
        id_emprestimo = int(devolucao_cadastrada.get_emprestimo().get_id_emprestimo())
        data_devolucao = devolucao_cadastrada.get_data_devolucao()

        data_devolucao_format = datetime.datetime.strptime(data_devolucao, '%d/%m/%Y')

        # Atualiza a descrição do produto existente
        self.mongo.db["devolucoes"].update_one({"id_devolucao": id_devolucao}, {"$set": {"id_emprestimo": id_emprestimo, "data_devolucao": data_devolucao_format}})

        # Cria um novo objeto
        registro_atualizado = Controller_Devolucao.get_devolucao_from_dataframe(self.mongo, id_devolucao)
        # Exibe os atributos do novo produto
        print(registro_atualizado.to_string())
        self.mongo.close()
        # Retorna o objeto
        return registro_atualizado

    def excluir_devolucao(self):
        # Cria uma nova conexão com o banco que permite alteração
        self.mongo.connect()

        # Solicita ao usuário o código da entidade a ser alterada
        id_devolucao = int(input("Código da Devolução que irá excluir: "))  

        # Verifica se a entidade existe na base de dados
        if not Controller_Devolucao.verifica_existencia_devolucao(self.mongo, id_devolucao):
            self.mongo.close()
            print(f"O código de Devolução {id_devolucao} não existe.")
            return None
        
        # Confirma se o usuário realmente deseja excluir o item selecionado
        confirmar_exclusao = input("Deseja realmente continuar com a exclusão? (S/N): ")
        if confirmar_exclusao.strip().lower() != "s":
            return None
        
        # Recupera os dados da entidade e cria um novo objeto para informar que foi removido
        devolucao_excluida = Controller_Devolucao.get_devolucao_from_dataframe(self.mongo, id_devolucao)

        # Revome da tabela
        self.mongo.db["devolucoes"].delete_one({"id_devolucao": id_devolucao})
        # Exibe os atributos do produto excluído
        print("Devolução removida com sucesso!")
        print(devolucao_excluida.to_string())
        self.mongo.close()

    def cadastrar_devolucao(self) -> Devolucao:
        #Solicita os dados de cadastro
        print("Informe os dados solicitado para cadastrar a devolução.\n")

        # Lista os usuarios existentes
        self.relatorio.get_relatorio_usuarios()
        codigo_usuario = str(input("\nDigite o código do usuário a fazer a devolução: "))
        usuario = Controller_Usuario.valida_usuario(self.mongo, codigo_usuario)
        if usuario == None:            
            return None

        # Lista os empréstimos existentes
        emprestimos_existentes = self.relatorio.get_relatorio_emprestimos_pendentes_por_usuario(codigo_usuario)
        if emprestimos_existentes == False:
            return None
        
        codigo_emprestimo = str(input("\nDigite o código do empréstimo a ser devolvido: "))
        emprestimo = Controller_Emprestimo.valida_emprestimo(self.mongo, codigo_emprestimo)
        if emprestimo == None:
            return None

        print("\n")

        if not Controller_Devolucao.valida_emprestimo_aberto_por_usuario(self.mongo, codigo_usuario, codigo_emprestimo):
            print(f"Não foi encontrado neste usuário um empréstimo em aberto com código {codigo_emprestimo}")
            return None

        data_devolucao = input("Data da devolução (DD/MM/YYYY): ")
        while not Controller_Emprestimo.valida_data_format(data_devolucao):
            print("\nVocê tentou inserir um formato inválido, tente novamente.\n")
            data_devolucao = input("Data da devolução (DD/MM/YYYY): ")

        return Devolucao(0, emprestimo, data_devolucao)

    @staticmethod
    def recupera_registro(mongo:MongoQueries, _id:ObjectId=None) -> pd.DataFrame:
        # Recupera os dados do registro transformando em um DataFrame
        dataframe = pd.DataFrame(list(mongo.db["devolucoes"].find({"_id":_id}, {"id_devolucao": 1, "id_emprestimo": 1, "data_devolucao": 1})))
        return dataframe

    @staticmethod
    def recupera_devolucao_codigo(mongo:MongoQueries, codigo:int=None, external: bool = False) -> pd.DataFrame:
        if external:
            # Cria uma nova conexão com o banco que permite alteração
            mongo.connect()
        # Recupera os dados do registro transformando em um DataFrame
        dataframe = pd.DataFrame(list(mongo.db["devolucoes"].find({"id_devolucao":int(codigo)}, {"id_devolucao": 1, "id_emprestimo": 1, "data_devolucao": 1})))
        if external:
            # Fecha a conexão com o Mongo
            mongo.close()
        return dataframe    
    
    @staticmethod
    def verifica_existencia_devolucao(mongo:MongoQueries, id_devolucao:int=None) -> bool:
        df_devolucao = Controller_Devolucao.recupera_devolucao_codigo(mongo, id_devolucao)
        return not df_devolucao.empty
    
    @staticmethod
    def get_devolucao_from_dataframe(mongo:MongoQueries, id_devolucao:int=None) -> Devolucao:
        df_devolucao = Controller_Devolucao.recupera_devolucao_codigo(mongo, id_devolucao)
        emprestimo = Controller_Emprestimo.get_emprestimo_from_dataframe(mongo, int(df_devolucao.id_emprestimo.values[0]))        
        return Devolucao(int(df_devolucao.id_devolucao.values[0]), emprestimo, df_devolucao.data_devolucao.values[0])

    
    @staticmethod
    def valida_emprestimo_aberto_por_usuario(mongo:MongoQueries, id_usuario:int=None, id_emprestimo:int=None) -> bool:
        #o id_emprestimo nao pode estar na tabela devolucoes, pois ele ja estaria devolvido
        #depois comparar se o id_emprestimo informado está relacionado com o id_usuario informado
        
        query_result = mongo.db['emprestimos'].aggregate([
            {
                '$match': {
                    'id_usuario': { '$eq': int(id_usuario) },
                    'id_emprestimo': { '$eq': int(id_emprestimo) }
                }
            },
            {
                '$lookup': {
                    'from': "devolucoes",
                    'localField': "id_emprestimo",
                    'foreignField': "id_emprestimo",
                    'as': "devolucoes"
                }
            },
            {
                '$match': {
                    "devolucoes": { '$eq': [] }
                }
            },
            {
                '$project': {
                    'devolucoes': 0
                }
            }
        ])
        dataframe = pd.DataFrame(list(query_result))

        return not dataframe.empty
