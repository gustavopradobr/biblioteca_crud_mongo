from bson import ObjectId
import pandas as pd
from model.livro import Livro
from conexion.mongo_queries import MongoQueries
from reports.relatorios import Relatorio

class Controller_Livro:
    def __init__(self):
        self.mongo = MongoQueries()
        
    def inserir_livro(self) -> Livro:
        # Cria uma nova conexão com o banco
        self.mongo.connect()
        
        #Solicita ao usuario os dados do livro
        print("\nInsira os dados do livro a ser cadastrado.\n")
        titulo_novo_livro = input("Título: ")
        autor_novo_livro = input("Autor: ")
        ano_novo_livro = int(input("Ano de publicação (número): "))
        qtd_novo_livro = int(input("Quantidade (número): "))
        while qtd_novo_livro < 1:
            print(f"\n\nQuantidade inválida. Insira um valor maior ou igual a 1: ")
            qtd_novo_livro = int(input("\nDigite a quantidade total desejada (número): "))

        proximo = self.mongo.db["livros"].aggregate([
                                                    {
                                                        '$group': {
                                                            '_id': '$livros', 
                                                            'proximo_livro': {
                                                                '$max': '$id_livro'
                                                            }
                                                        }
                                                    }, {
                                                        '$project': {
                                                            'proximo_livro': {
                                                                '$sum': [
                                                                    '$proximo_livro', 1
                                                                ]
                                                            }, 
                                                            '_id': 0
                                                        }
                                                    }
                                                ])

        proximo = int(list(proximo)[0]['proximo_livro'])
        
        # Insere e Recupera o código do novo registro
        id_registro = self.mongo.db["livros"].insert_one({"id_livro": proximo, "titulo": titulo_novo_livro, "autor": autor_novo_livro, "ano_publicacao": ano_novo_livro, "quantidade": qtd_novo_livro})
        # Recupera os dados do novo registro criado transformando em um DataFrame
        dataframe = Controller_Livro.recupera_registro(self.mongo, id_registro.inserted_id)
        # Cria um novo objeto
        novo_registro = Livro(dataframe.id_livro.values[0], dataframe.titulo.values[0], dataframe.autor.values[0], dataframe.ano_publicacao.values[0], dataframe.quantidade.values[0])
        # Exibe os atributos do novo registro
        print(novo_registro.to_string())
        self.mongo.close()
        # Retorna o objeto novo_produto para utilização posterior, caso necessário
        return novo_registro

    def atualizar_livro(self) -> Livro:
        # Cria uma nova conexão com o banco que permite alteração
        self.mongo.connect()

        # Solicita ao usuário o código da entidade a ser alterada
        id_livro = int(input("Código do Livro que irá alterar: "))

        # Verifica se o registro existe na base de dados
        if not Controller_Livro.verifica_existencia_livro(self.mongo, id_livro):
            self.mongo.close()
            print(f"O código {id_livro} não existe.")
            return None
        
        livro_atual = Controller_Livro.get_livro_from_dataframe(self.mongo, id_livro)

        print("Insira os novos dados do livro a ser atualizado.\n")
        titulo = input("Título: ")
        autor = input("Autor: ")
        ano = int(input("Ano de publicação (número): "))
        qtd = int(input("Quantidade (número): "))
        while qtd < livro_atual.get_quantidade():
            print(f"Você não pode reduzir a quantidade total de {livro_atual.get_quantidade()}. Insira um valor maior ou igual: ")
            qtd = int(input("Quantidade total (número): "))

        # Atualiza a descrição do produto existente
        self.mongo.db["livros"].update_one({"id_livro": id_livro}, {"$set": {"titulo": titulo, "autor": autor, "ano_publicacao": ano, "quantidade": qtd}})

        # Recupera os dados em um DataFrame
        dataframe = Controller_Livro.recupera_livro_codigo(self.mongo, id_livro)
        # Cria um novo objeto
        livro_atualizado = Livro(dataframe.id_livro.values[0], dataframe.titulo.values[0], dataframe.autor.values[0], dataframe.ano_publicacao.values[0], dataframe.quantidade.values[0])
        # Exibe os atributos do novo produto
        print(livro_atualizado.to_string())
        self.mongo.close()
        # Retorna o objeto
        return livro_atualizado

    def excluir_livro(self):
        # Cria uma nova conexão com o banco que permite alteração
        self.mongo.connect()

        # Solicita o código da entidade a ser excluida
        id_livro = int(input("Código do Livro que irá excluir: "))  

        # Verifica se o produto existe na base de dados
        if not Controller_Livro.verifica_existencia_livro(self.mongo, id_livro): 
            self.mongo.close()
            print(f"O código {id_livro} não existe.")
            return
        
        # Confirma se o usuário realmente deseja excluir o item selecionado
        confirmar_exclusao = input("Deseja realmente continuar com a exclusão? (S/N): ")
        if confirmar_exclusao.strip().lower() != "s":
            return None

        # Recupera os dados transformando em um DataFrame
        dataframe = Controller_Livro.recupera_livro_codigo(self.mongo, id_livro)
        # Revome da tabela
        self.mongo.db["livros"].delete_one({"id_livro": id_livro})
        # Cria um novo objeto para informar que foi removido
        livro_excluido = Livro(dataframe.id_livro.values[0], dataframe.titulo.values[0], dataframe.autor.values[0], dataframe.ano_publicacao.values[0], dataframe.quantidade.values[0])
        # Exibe os atributos do produto excluído
        print("Livro removido com Sucesso!")
        print(livro_excluido.to_string())
        self.mongo.close()

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
        dataframe = pd.DataFrame(list(mongo.db["livros"].find({"_id":_id}, {"id_livro": 1, "titulo": 1, "autor": 1, "ano_publicacao": 1, "quantidade": 1, "_id": 0})))
        return dataframe


    @staticmethod   
    def recupera_livro_codigo(mongo:MongoQueries, codigo:int=None, external: bool = False) -> pd.DataFrame:
        if external:
            # Cria uma nova conexão com o banco que permite alteração
            mongo.connect()

        # Recupera os dados do registro transformando em um DataFrame
        dataframe = pd.DataFrame(list(mongo.db["livros"].find({"id_livro":int(codigo)}, {"id_livro": 1, "titulo": 1, "autor": 1, "ano_publicacao": 1, "quantidade": 1, "_id": 0})))

        if external:
            # Fecha a conexão com o Mongo
            mongo.close()

        return dataframe
    
    @staticmethod
    def get_livro_from_dataframe(mongo:MongoQueries, id_livro:int=None) -> Livro:
        dataframe = Controller_Livro.recupera_livro_codigo(mongo, id_livro)
        # Cria novo objeto a partir do DataFrame
        return Livro(dataframe.id_livro.values[0], dataframe.titulo.values[0], dataframe.autor.values[0], dataframe.ano_publicacao.values[0], dataframe.quantidade.values[0])
    

    @staticmethod
    def valida_livro_disponivel(mongo:MongoQueries, id_livro:int=None) -> Livro:
        if not Controller_Livro.verifica_existencia_livro(mongo, id_livro):
            print(f"O livro de código {id_livro} não existe na base.")
            return None
        
        livros_disponiveis_df = Relatorio().get_dataframe_livros_detail_disponiveis()

        if not (int(id_livro) in livros_disponiveis_df.id_livro.values.tolist()):
            print(f"O livro de código {id_livro} não possui quantidade disponível.")
            return None

        return Controller_Livro.get_livro_from_dataframe(mongo, id_livro)