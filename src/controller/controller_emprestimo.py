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
        
        data_emprestimo_format = datetime.datetime.strptime(data_emprestimo, '%d/%m/%Y')
        data_devolucao_format = datetime.datetime.strptime(data_devolucao_sugerida, '%d/%m/%Y')

        # Insere e Recupera o código do novo registro
        id_registro = self.mongo.db["emprestimos"].insert_one({"id_emprestimo": proximo, "id_livro": id_livro, "id_usuario": id_usuario, "data_emprestimo": data_emprestimo_format, "data_devolucao_sugerida": data_devolucao_format})
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

        id_livro = int(emprestimo_atualizado.get_livro().get_id_livro())
        id_usuario = int(emprestimo_atualizado.get_usuario().get_id_usuario())
        data_emprestimo = emprestimo_atualizado.get_data_emprestimo()
        data_devolucao_sugerida = emprestimo_atualizado.get_data_devolucao()

        data_emprestimo_format = datetime.datetime.strptime(data_emprestimo, '%d/%m/%Y')
        data_devolucao_format = datetime.datetime.strptime(data_devolucao_sugerida, '%d/%m/%Y')

        # Atualiza a descrição do produto existente
        self.mongo.db["emprestimos"].update_one({"id_emprestimo": id_emprestimo}, {"$set": {"id_livro": id_livro, "id_usuario": id_usuario, "data_emprestimo": data_emprestimo_format, "data_devolucao_sugerida": data_devolucao_format}})

        # Cria um novo objeto
        registro_atualizado = Controller_Emprestimo.get_emprestimo_from_dataframe(self.mongo, id_emprestimo)
        # Exibe os atributos do novo produto
        print(registro_atualizado.to_string())
        self.mongo.close()
        # Retorna o objeto
        return registro_atualizado

    def excluir_emprestimo(self):
        # Cria uma nova conexão com o banco que permite alteração
        self.mongo.connect()

        # Solicita o código da entidade a ser excluida
        id_emprestimo = int(input("Código do Empréstimo que irá excluir: ")) 

        # Verifica se o produto existe na base de dados
        if not Controller_Emprestimo.verifica_existencia_emprestimo(self.mongo, id_emprestimo):
            self.mongo.close()
            print(f"O código {id_emprestimo} não existe.")
            return
        
        # Confirma se o usuário realmente deseja excluir o item selecionado
        confirmar_exclusao = input("Deseja realmente continuar com a exclusão? (S/N): ")
        if confirmar_exclusao.strip().lower() != "s":
            return None

        if Controller_Emprestimo.verifica_emprestimos_relacoes(self.mongo, id_emprestimo):
            print(f"O empréstimo de código {id_emprestimo} possui registros dependentes. Deseja excluir mesmo assim? [S/N]")
            opcao = input()

            if opcao.upper() != "S":
                print("Operação cancelada.")
                return None
            
            print("Excluindo registros dependentes...")

        # Recupera os dados transformando em um DataFrame
        emprestimo_excluido = Controller_Emprestimo.get_emprestimo_from_dataframe(self.mongo, id_emprestimo)

        Controller_Emprestimo.excluir_emprestimo_relacoes(self.mongo, id_emprestimo)

        # Exibe os atributos do produto excluído
        print("Empréstimo removido com sucesso!")
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

        if not self.relatorio.get_relatorio_livros_disponiveis():
            #retorna se nao possuir livros disponiveis
            return None
        
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

    @staticmethod
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
    def excluir_emprestimo_relacoes(mongo:MongoQueries, id_emprestimo:int):
        # Remove relação devolucoes
        mongo.db["devolucoes"].delete_many({"id_emprestimo": int(id_emprestimo)})
        # Remove da tabela emprestimos
        mongo.db["emprestimos"].delete_one({"id_emprestimo": int(id_emprestimo)})

    @staticmethod
    def verifica_emprestimos_relacoes(mongo:MongoQueries, id_emprestimo:int) -> bool:
        query_result = mongo.db["devolucoes"].find({ 'id_emprestimo': int(id_emprestimo) }, { '_id': 0, 'id_emprestimo': 1 })
        dataframe = pd.DataFrame(list(query_result))
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
    def verifica_emprestimo_aberto(mongo:MongoQueries, id_emprestimo:int=None) -> bool:
        query_result = mongo.db['emprestimos'].aggregate([
            {
                '$match': {
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
                '$project': {
                    '_id': 0,
                    'id_emprestimo': 1,
                    'devolucao_realizada': {
                        '$cond': {
                            'if': { '$gt': [{ '$size': "$devolucoes" }, 0] },
                            'then': 1,
                            'else': 0
                        }
                    }
                    }
            }
        ])
        dataframe = pd.DataFrame(list(query_result))

        if dataframe.empty:
            return False
        
        return int(dataframe.devolucao_realizada.values[0]) == 0


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
