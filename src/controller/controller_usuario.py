from bson import ObjectId
import pandas as pd
from model.usuario import Usuario
from conexion.mongo_queries import MongoQueries

class Controller_Usuario:
    def __init__(self):
        self.mongo = MongoQueries()
        
    def inserir_usuario(self) -> Usuario:
        # Cria uma nova conexão com o banco
        self.mongo.connect()
        
        #Solicita os dados de cadastro
        print("\nInsira os dados do usuário.\n")
        nome = input("Nome: ")
        email = input("Email: ")
        telefone = input("Telefone: ")

        proximo = self.mongo.db["usuarios"].aggregate([
                                                    {
                                                        '$group': {
                                                            '_id': '$usuarios', 
                                                            'proximo_usuario': {
                                                                '$max': '$id_usuario'
                                                            }
                                                        }
                                                    }, {
                                                        '$project': {
                                                            'proximo_usuario': {
                                                                '$sum': [
                                                                    '$proximo_usuario', 1
                                                                ]
                                                            }, 
                                                            '_id': 0
                                                        }
                                                    }
                                                ])

        proximo = int(list(proximo)[0]['proximo_usuario'])
        
        # Insere e Recupera o código do novo registro
        id_registro = self.mongo.db["usuarios"].insert_one({"id_usuario": proximo, "nome": nome, "email": email, "telefone": telefone})
        # Recupera os dados do novo registro criado transformando em um DataFrame
        dataframe = Controller_Usuario.recupera_registro(self.mongo, id_registro.inserted_id)
        # Cria um novo objeto
        novo_registro = Usuario(dataframe.id_usuario.values[0], dataframe.nome.values[0], dataframe.email.values[0], dataframe.telefone.values[0])
        # Exibe os atributos do novo registro
        print(novo_registro.to_string())
        self.mongo.close()
        # Retorna o objeto novo_produto para utilização posterior, caso necessário
        return novo_registro

    def atualizar_usuario(self) -> Usuario:
        # Cria uma nova conexão com o banco que permite alteração
        self.mongo.connect()

        # Solicita ao usuário o código da entidade a ser alterada
        id_usuario = int(input("Código do Usuário que irá alterar: "))

        # Verifica se o registro existe na base de dados
        if not Controller_Usuario.verifica_existencia_usuario(self.mongo, id_usuario):
            self.mongo.close()
            print(f"O código {id_usuario} não existe.")
            return None
        
        print("Insira os novos dados do usuário a ser atualizado.\n")
        nome = input("Nome: ")
        email = input("Email: ")
        telefone = input("Telefone: ")

        # Atualiza a descrição do produto existente
        self.mongo.db["usuarios"].update_one({"id_usuario": id_usuario}, {"$set": {"nome": nome, "email": email, "telefone": telefone}})
        # Recupera os dados em um DataFrame
        dataframe = Controller_Usuario.recupera_usuario_codigo(self.mongo, id_usuario)
        # Cria um novo objeto
        usuario_atualizado = Usuario(dataframe.id_usuario.values[0], dataframe.nome.values[0], dataframe.email.values[0], dataframe.telefone.values[0])
        # Exibe os atributos do novo produto
        print(usuario_atualizado.to_string())
        self.mongo.close()
        # Retorna o objeto
        return usuario_atualizado

    def excluir_usuario(self):
        # Cria uma nova conexão com o banco que permite alteração
        self.mongo.connect()

        # Solicita o código da entidade a ser excluida
        id_usuario = int(input("Código do Usuário que irá excluir: "))  

        # Verifica se o produto existe na base de dados
        if not Controller_Usuario.verifica_existencia_usuario(self.mongo, id_usuario): 
            self.mongo.close()
            print(f"O código {id_usuario} não existe.")
            return
        
        # Confirma se o usuário realmente deseja excluir o item selecionado
        confirmar_exclusao = input("Deseja realmente continuar com a exclusão? (S/N): ")
        if confirmar_exclusao.strip().lower() != "s":
            return None

        if not Controller_Usuario.get_usuario_relacoes(self.mongo, id_usuario).empty:
            print(f"O usuário de código {id_usuario} possui registros dependentes. Deseja excluir mesmo assim? [S/N]")
            opcao = input()

            if opcao.upper() != "S":
                print("Operação cancelada.")
                return None
            
            print("Excluindo registros dependentes...")

        # Recupera os dados transformando em um DataFrame
        dataframe = Controller_Usuario.recupera_usuario_codigo(self.mongo, id_usuario)

        Controller_Usuario.excluir_usuario_relacoes(self.mongo, id_usuario)

        # Cria um novo objeto para informar que foi removido
        usuario_excluido = Usuario(dataframe.id_usuario.values[0], dataframe.nome.values[0], dataframe.email.values[0], dataframe.telefone.values[0])
        # Exibe os atributos do produto excluído
        print("Usuário removido com sucesso!")
        print(usuario_excluido.to_string())
        self.mongo.close()

    @staticmethod
    def verifica_existencia_usuario(mongo:MongoQueries, codigo:int=None, external: bool = False) -> bool:
        if external:
            # Cria uma nova conexão com o banco que permite alteração
            mongo.connect()

        dataframe = pd.DataFrame(mongo.db["usuarios"].find({"id_usuario":int(codigo)}, {"id_usuario": 1, "_id": 0}))

        if external:
            # Fecha a conexão com o Mongo
            mongo.close()

        return not dataframe.empty
    
    @staticmethod
    def excluir_usuario_relacoes(mongo:MongoQueries, id_usuario):
        from controller.controller_emprestimo import Controller_Emprestimo
        emprestimos_com_usuario_df = Controller_Usuario.get_usuario_relacoes(mongo, id_usuario)

        if emprestimos_com_usuario_df.empty:
            return
        
        # Remove relações
        for id_emprestimo in emprestimos_com_usuario_df['id_emprestimo'].tolist():
            Controller_Emprestimo.excluir_emprestimo_relacoes(mongo, id_emprestimo)

        # Remove da tabela usuarios
        mongo.db["usuarios"].delete_many({"id_usuario": int(id_usuario)})

    @staticmethod
    def get_usuario_relacoes(mongo:MongoQueries, id_usuario:int) -> pd.DataFrame:
        query_result = mongo.db["emprestimos"].find({ 'id_usuario': int(id_usuario) }, { '_id': 0, 'id_emprestimo': 1, 'id_usuario': 1 })
        dataframe = pd.DataFrame(list(query_result))
        return dataframe

    @staticmethod
    def recupera_registro(mongo:MongoQueries, _id:ObjectId=None) -> pd.DataFrame:
        # Recupera os dados do registro transformando em um DataFrame
        dataframe = pd.DataFrame(list(mongo.db["usuarios"].find({"_id":_id}, {"id_usuario": 1, "nome": 1, "email": 1, "telefone": 1, "_id": 0})))
        return dataframe

    @staticmethod
    def get_usuario_from_dataframe(mongo:MongoQueries, codigo_usuario:int=None) -> pd.DataFrame:
        dataframe = Controller_Usuario.recupera_usuario_codigo(mongo, codigo_usuario)
        return Usuario(dataframe.id_usuario.values[0], dataframe.nome.values[0], dataframe.email.values[0], dataframe.telefone.values[0])

    @staticmethod
    def recupera_usuario_codigo(mongo:MongoQueries, codigo:int=None, external: bool = False) -> pd.DataFrame:
        if external:
            # Cria uma nova conexão com o banco que permite alteração
            mongo.connect()

        # Recupera os dados do registro transformando em um DataFrame
        dataframe = pd.DataFrame(list(mongo.db["usuarios"].find({"id_usuario":int(codigo)}, {"id_usuario": 1, "nome": 1, "email": 1, "telefone": 1, "_id": 0})))

        if external:
            # Fecha a conexão com o Mongo
            mongo.close()

        return dataframe
    
    @staticmethod
    def valida_usuario(mongo:MongoQueries, codigo_usuario:int=None) -> Usuario:
        if not Controller_Usuario.verifica_existencia_usuario(mongo, codigo_usuario):
            print(f"O usuário de código {codigo_usuario} não existe na base.")
            return None
        else:
            return Controller_Usuario.get_usuario_from_dataframe(mongo, codigo_usuario)