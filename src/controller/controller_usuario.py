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
        dataframe = self.recupera_registro(id_registro.inserted_id)
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
        if not self.verifica_existencia_usuario(id_usuario):
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
        dataframe = self.recupera_usuario_codigo(id_usuario)
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
        if not self.verifica_existencia_usuario(id_usuario): 
            self.mongo.close()
            print(f"O código {id_usuario} não existe.")
            return
        
        # Recupera os dados transformando em um DataFrame
        dataframe = self.recupera_usuario_codigo(id_usuario)
        # Revome da tabela
        self.mongo.db["usuarios"].delete_one({"id_usuario": id_usuario})
        # Cria um novo objeto para informar que foi removido
        usuario_excluido = Usuario(dataframe.id_usuario.values[0], dataframe.nome.values[0], dataframe.email.values[0], dataframe.telefone.values[0])
        # Exibe os atributos do produto excluído
        print("Usuário removido com Sucesso!")
        print(usuario_excluido.to_string())
        self.mongo.close()

    def verifica_existencia_usuario(self, codigo:int=None, external: bool = False) -> bool:
        if external:
            # Cria uma nova conexão com o banco que permite alteração
            self.mongo.connect()

        dataframe = pd.DataFrame(self.mongo.db["usuarios"].find({"id_usuario":codigo}, {"id_usuario": 1, "_id": 0}))

        if external:
            # Fecha a conexão com o Mongo
            self.mongo.close()

        return not dataframe.empty

    def recupera_registro(self, _id:ObjectId=None) -> pd.DataFrame:
        # Recupera os dados do registro transformando em um DataFrame
        dataframe = pd.DataFrame(list(self.mongo.db["usuarios"].find({"_id":_id}, {"id_usuario": 1, "nome": 1, "email": 1, "telefone": 1, "_id": 0})))
        return dataframe

    def recupera_usuario_codigo(self, codigo:int=None, external: bool = False) -> pd.DataFrame:
        if external:
            # Cria uma nova conexão com o banco que permite alteração
            self.mongo.connect()

        # Recupera os dados do registro transformando em um DataFrame
        dataframe = pd.DataFrame(list(self.mongo.db["usuarios"].find({"id_usuario":codigo}, {"id_usuario": 1, "nome": 1, "email": 1, "telefone": 1, "_id": 0})))

        if external:
            # Fecha a conexão com o Mongo
            self.mongo.close()

        return dataframe