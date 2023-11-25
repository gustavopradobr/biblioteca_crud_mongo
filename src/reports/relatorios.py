from conexion.mongo_queries import MongoQueries
import pandas as pd
from pymongo import ASCENDING, DESCENDING

class Relatorio:
    def __init__(self):
        pass

    def get_query_emprestimos_detail(self):
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
                                                        #"Data Emprestimo": "$data_emprestimo",
                                                        #"Data Emprestimo": {'$toDate':"$data_emprestimo"},
                                                        "Data Emprestimo":
                                                        { '$dateToString': {
                                                                'date': {'$toDate':"$data_emprestimo"},
                                                                'format': "%d/%m/%Y"
                                                            } },
                                                        #"Devolucao Sugerida": "$data_devolucao_sugerida",
                                                        #"Devolucao Sugerida": {'$toDate':"$data_devolucao_sugerida"},
                                                        "Devolucao Sugerida":
                                                        { '$dateToString': {
                                                                'date': {'$toDate':"$data_devolucao_sugerida"},
                                                                'format': "%d/%m/%Y"
                                                            } },

                                                        "Status": "$devolucao_realizada",
                                                        '_id': 0
                                                    }
                                                },
                                                {
                                                    '$sort': {
                                                        "Status": 1,
                                                        "id_emprestimo": 1
                                                    }
                                                }
                                                ])
        
        return query_result

    def get_relatorio_emprestimos(self) -> bool:
        # Recupera os dados transformando em um DataFrame
        query_result = self.get_query_emprestimos_detail()
        dataframe = pd.DataFrame(list(query_result))

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
                                                  #"Data Devolucao": "$data_devolucao",
                                                  "Data Devolucao":
                                                        { '$dateToString': {
                                                                'date': {'$toDate':"$data_devolucao"},
                                                                'format': "%d/%m/%Y"
                                                        } },
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
    
    def get_relatorio_livros(self) -> bool:
        dataframe = self.get_dataframe_livros_detail()
        if dataframe.empty:
            print("A tabela Livros não possui registros.")
            return False     
        print(dataframe)
        return True
    
    def get_relatorio_livros_disponiveis(self) -> bool:
        dataframe = self.get_dataframe_livros_detail()
        if dataframe.empty:
            print("A tabela Livros não possui registros.")
            return False     
        dataframe = dataframe[dataframe['Disponibilidade'] > 0]
        if dataframe.empty:
            print("Não existem livros disponíveis no momento.")
            return False
        print(dataframe)
        return True
    
    def get_dataframe_livros_detail_disponiveis(self) -> pd.DataFrame:
        dataframe = self.get_dataframe_livros_detail()
        if not dataframe.empty:
            dataframe = dataframe[dataframe['Disponibilidade'] > 0]
        return dataframe

    def get_dataframe_livros_detail(self) -> pd.DataFrame:
        # Cria uma nova conexão com o banco
        mongo = MongoQueries()
        mongo.connect()
        # Recupera os dados transformando em um DataFrame
        query_result = mongo.db['livros'].aggregate([
                                                {
                                                    '$lookup': {
                                                        'from': "emprestimos",
                                                        'localField': "id_livro",
                                                        'foreignField': "id_livro",
                                                        'as': "emprestimos"
                                                    }
                                                },
                                                {
                                                    '$lookup': {
                                                        'from': "devolucoes",
                                                        'localField': "emprestimos.id_emprestimo",
                                                        'foreignField': "id_emprestimo",
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
                                                        'devolucoes_pendentes': {
                                                            '$size': "$emprestimos_sem_devolucao"
                                                        }
                                                    }
                                                },
                                                {
                                                    '$addFields': {
                                                        'disponibilidade': {
                                                            '$subtract': [
                                                                '$quantidade',
                                                                '$devolucoes_pendentes'
                                                            ]
                                                        }
                                                    }
                                                },
                                                {
                                                    '$project': {
                                                        '_id': 0,
                                                        "id_livro": 1,
                                                        "Titulo": "$titulo",
                                                        "Autor": "$autor",
                                                        "Ano Publicacao": "$ano_publicacao",
                                                        "Quantidade": "$quantidade",
                                                        "Disponibilidade": "$disponibilidade",
                                                        #'Emprestimos Realizados': {'$size': '$emprestimos'},
                                                        #'Devolucoes Pendentes': '$devolucoes_pendentes'
                                                    }
                                                }
                                                ])        
        
        dataframe = pd.DataFrame(list(query_result))
        # Fecha a conexão com o mongo
        mongo.close()
        return dataframe

    #Não utilizado -------------------------
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
                                                        'localField': "emprestimos.id_emprestimo",
                                                        'foreignField': "id_emprestimo",
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
                                                        'devolucoes_pendentes': {
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
                                                        'Emprestimos Realizados': {'$size': '$emprestimos'},
                                                        'Devolucoes Pendentes': '$devolucoes_pendentes'
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
    
    def get_relatorio_emprestimos_pendentes_por_usuario(self, codigo_usuario) -> bool:        
        # Recupera os dados transformando em um DataFrame
        query_result = self.get_query_emprestimos_detail()
        dataframe = pd.DataFrame(list(query_result))
        dataframe = dataframe[dataframe['id_usuario'] == int(codigo_usuario)]
        dataframe = dataframe[dataframe['Status'] == "Pendente"]

        if dataframe.empty:
            print("\nNão existem devoluções pendentes para este usuário.")
        else:        
            print(dataframe)
        #retorna se a consulta foi vazia, para saber se existem registros baseados neste usuario
        return not dataframe.empty
