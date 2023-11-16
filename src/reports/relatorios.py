from conexion.mongo_queries import MongoQueries
import pandas as pd
from pymongo import ASCENDING, DESCENDING

class Relatorio:
    def __init__(self):
        pass

    def get_relatorio_emprestimos(self) -> bool:
        # Cria uma nova conexão com o banco
        mongo = MongoQueries()
        mongo.connect()
        # Recupera os dados transformando em um DataFrame
        query_result = mongo.db["emprestimos"].aggregate([
                                                {
                                                    '$lookup': {
                                                        'from': "livros",
                                                        'localField': "id_livro",
                                                        'foreignField': "id_livro",
                                                        'as': "livro"
                                                    }
                                                },
                                                {
                                                    '$unwind': "$livro"
                                                },
                                                {
                                                    '$lookup': {
                                                        'from': "usuarios",
                                                        'localField': "id_usuario",
                                                        'foreignField': "id_usuario",
                                                        'as': "usuario"
                                                    }
                                                },
                                                {
                                                    '$unwind': "$usuario"
                                                },
                                                {
                                                    '$lookup': {
                                                        'from': "devolucoes",
                                                        'localField': "id_emprestimo",
                                                        'foreignField': "id_emprestimo",
                                                        'as': "devolucao"
                                                    }
                                                },
                                                {
                                                    '$addFields': {
                                                        'devolucao_realizada': {
                                                            '$cond': {
                                                            'if': { '$gt': [{ '$size': "$devolucao" }, 0] },
                                                            'then': "Devolvido",
                                                            'else': "Pendente"
                                                            }
                                                        }
                                                    }
                                                },
                                                {
                                                    '$project': {
                                                        "id_emprestimo": 1,
                                                        "id_livro": 1,
                                                        "id_usuario": 1,
                                                        "Nome Usuario": "$usuario.nome",
                                                        "Titulo Livro": "$livro.titulo",
                                                        "Data Emprestimo": "$data_emprestimo",
                                                        "Devolucao Sugerida": "$data_devolucao_sugerida",
                                                        "Status": "$devolucao_realizada",
                                                        '_id': 0
                                                    }
                                                },
                                                {
                                                    '$sort': {
                                                        "devolucao_realizada": 1,
                                                        "id_emprestimo": 1
                                                    }
                                                }
                                                ])
        dataframe = pd.DataFrame(list(query_result))
        # Fecha a conexão com o Mongo
        mongo.close()
        # Exibe o resultado
        if dataframe.empty:
            print("A tabela Emprestimos não possui registros.")
            return False        
        print(dataframe)
        return True
    
    def get_relatorio_devolucoes(self) -> bool:
        # Cria uma nova conexão com o banco
        mongo = MongoQueries()
        mongo.connect()
        # Recupera os dados transformando em um DataFrame
        query_result = mongo.db["devolucoes"].find({}, 
                                                 {"id_devolucao": 1, 
                                                  "id_emprestimo": 1, 
                                                  "data_devolucao": 1, 
                                                  "_id": 0
                                                 }).sort("id_devolucao", ASCENDING)
        dataframe = pd.DataFrame(list(query_result))
        # Fecha a conexão com o Mongo
        mongo.close()
        # Exibe o resultado
        if dataframe.empty:
            print("A tabela Devolucoes não possui registros.")
            return False        
        print(dataframe)
        return True
    
    def get_relatorio_livros(self) -> bool:
        # Cria uma nova conexão com o banco
        mongo = MongoQueries()
        mongo.connect()
        # Recupera os dados transformando em um DataFrame
        query_result = mongo.db["livros"].find({}, 
                                                 {"id_livro": 1, 
                                                  "titulo": 1, 
                                                  "autor": 1, 
                                                  "ano_publicacao": 1, 
                                                  "quantidade": 1, 
                                                  "_id": 0
                                                 }).sort("id_livro", ASCENDING)
        dataframe = pd.DataFrame(list(query_result))
        # Fecha a conexão com o mongo
        mongo.close()
        # Exibe o resultado
        if dataframe.empty:
            print("A tabela Livros não possui registros.")
            return False        
        print(dataframe)
        return True
    
    def get_relatorio_livros_quantidade(self) -> bool:
        # Cria uma nova conexão com o banco
        mongo = MongoQueries()
        mongo.connect()
        # Recupera os dados transformando em um DataFrame
        query_result = mongo.db["livros"].find( {}, 
                            {"_id": 0,
                            "id_livro": 1,
                            "titulo": 1,
                            "autor": 1,
                            "ano_publicacao": 1,
                            "quantidade": 1,
                            "disponibilidade": {
                                "$subtract": [
                                    "$quantidade",
                                        len(list(mongo.db["emprestimos"].find({
                                        "id_livro": {
                                            "$eq": "$_id"
                                        },
                                        "id_emprestimo": {
                                            "$nin": mongo.db["devolucoes"].distinct("id_emprestimo")
                                        }
                                    })))]
                            }
                        }).sort("id_livro", ASCENDING)
        
        dataframe = pd.DataFrame(list(query_result))
        # Fecha a conexão com o mongo
        mongo.close()
        # Exibe o resultado
        if dataframe.empty:
            print("A tabela Livros não possui registros.")
            return False        
        print(dataframe)
        return True
    
    def get_relatorio_livros_disponiveis(self) -> bool:
        dataframe = self.get_dataframe_livros_disponiveis()
        if dataframe.empty:
            print("A tabela Livros não possui registros.")
            return False        
        print(dataframe)
        return True
    
    def get_dataframe_livros_disponiveis(self) -> pd.DataFrame:
        # Cria uma nova conexão com o banco
        mongo = MongoQueries()
        mongo.connect()
        # Recupera os dados transformando em um DataFrame
        query_result = mongo.db["livros"].find({}, 
                            {"_id": 0,
                            "id_livro": 1,
                            "titulo": 1,
                            "autor": 1,
                            "ano_publicacao": 1,
                            "quantidade": 1,
                            "disponibilidade": {
                                "$subtract": [
                                    "$quantidade",
                                    len(list(mongo.db["emprestimos"].find({
                                        "id_livro": {
                                            "$eq": "$_id"
                                        },
                                        "id_emprestimo": {
                                            "$nin": mongo.db["devolucoes"].distinct("id_emprestimo")
                                        }
                                    })))]
                            }
                        }).sort("id_livro", ASCENDING)
        
        
        dataframe = pd.DataFrame(list(query_result))
        dataframe = dataframe[dataframe['disponibilidade'] > 0] 
        # Fecha a conexão com o mongo
        mongo.close()
        return dataframe

    def get_relatorio_usuarios(self) -> bool:
        # Cria uma nova conexão com o banco
        mongo = MongoQueries()
        mongo.connect()
        # Recupera os dados transformando em um DataFrame
        query_result = mongo.db["usuarios"].find({}, 
                                                 {"id_usuario": 1, 
                                                  "nome": 1, 
                                                  "email": 1, 
                                                  "telefone": 1, 
                                                  "_id": 0
                                                 }).sort("id_usuario", ASCENDING)
        dataframe = pd.DataFrame(list(query_result))
        # Fecha a conexão com o mongo
        mongo.close()
        # Exibe o resultado
        if dataframe.empty:
            print("A tabela Usuarios não possui registros.")
            return False        
        print(dataframe)
        return True
    
    def get_relatorio_usuarios_livros(self) -> bool:
        # Cria uma nova conexão com o banco
        mongo = MongoQueries()
        mongo.connect()
        # Recupera os dados transformando em um DataFrame      
        count_emprestimos_nao_devolvidos = mongo.db["emprestimos"].count_documents({
                'id_usuario': "$_id",
                'id_emprestimo': {'$nin': mongo.db["devolucoes"].distinct('id_emprestimo')}
            })
        


        query_result = mongo.db["usuarios"].aggregate([
                                                    {
                                                        '$lookup': {
                                                            'from': 'emprestimos',
                                                            'localField': 'id_usuario',
                                                            'foreignField': 'id_usuario',
                                                            'as': 'emprestimos_usuario'
                                                        }
                                                    },
                                                    {
                                                        '$project': {
                                                            '_id': 0,
                                                            'id_usuario': '$id_usuario',
                                                            'nome': '$nome',
                                                            'email': '$email',
                                                            'telefone': '$telefone',
                                                            'devolucoes': {
                                                                "$sum": [
                                                                    0,

                                                                    len(list(mongo.db["devolucoes"].find({
                                                                        "id_emprestimo": {
                                                                            "$eq": "$emprestimos_usuario"
                                                                        }
                                                                    })))

                                                                    ]                                                            
                                                            },
                                                            'devolucoes_pendentes': {
                                                                "$subtract": [
                                                                    {'$size': '$emprestimos_usuario'},
                                                                    mongo.db["devolucoes"].count_documents({
                                                                        'id_emprestimo': "$emprestimos_usuario"
                                                                    })
                                                                    ]                                                            
                                                            },
                                                            'emprestimos_realizados': {'$size': '$emprestimos_usuario'}
                                                        }
                                                    }
                                                    ])
        
        query_result = mongo.db['usuarios'].aggregate([
                                                {
                                                    '$lookup': {
                                                        'from': "emprestimos",
                                                        'localField': "id_usuario",
                                                        'foreignField': "id_usuario",
                                                        'as': "emprestimos"
                                                    }
                                                },
                                                {
                                                    '$lookup': {
                                                        'from': "devolucoes",
                                                        'localField': "id_usuario",
                                                        'foreignField': "id_usuario",
                                                        'as': "devolucoes"
                                                    }
                                                },
                                                {
                                                    '$addFields': {
                                                        'emprestimos_sem_devolucao': {
                                                            '$filter': {
                                                            'input': "$emprestimos",
                                                            'as': "emprestimo",
                                                            'cond': {
                                                                '$not': {
                                                                    '$in': ["$$emprestimo.id_emprestimo", "$devolucoes.id_emprestimo"]
                                                                }
                                                            }
                                                            }
                                                        }
                                                    }
                                                },
                                                {
                                                    '$addFields': {
                                                        'quantidade_emprestimos_sem_devolucao': {
                                                            '$size': "$emprestimos_sem_devolucao"
                                                        }
                                                    }
                                                },
                                                {
                                                    '$project': {
                                                        '_id': 0,
                                                        'id_usuario': '$id_usuario',
                                                        'Nome': '$nome',
                                                        'Email': '$email',
                                                        'Telefone': '$telefone',
                                                        'Devolucoes Pendente': '$quantidade_emprestimos_sem_devolucao',
                                                        'Emprestimos Realizados': {'$size': '$emprestimos'}
                                                    }
                                                }
                                                ])
        dataframe = pd.DataFrame(list(query_result))
        # Fecha a conexão com o mongo
        mongo.close()
        # Exibe o resultado
        if dataframe.empty:
            print("A tabela Usuarios não possui registros.")
            return False        
        print(dataframe)
        return True