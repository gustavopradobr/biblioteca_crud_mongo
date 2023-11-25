from utils import config

class SplashScreen:

    def __init__(self):
        # Nome(s) do(s) criador(es)
        self.created_by = """
        #       CAIO FELIPE CARDOZO DO ESPIRITO SANTO
        #       GUILHERME FERRAZ THOMÉ CASSIS DE OLIVEIRA
        #       GUSTAVO SOARES PRADO
        #       LUIZ FELIPE MACEDO CRUZ
        #       PEDRO HENRIQUE MARINHO DE OLIVEIRA
        #       VINÍCIUS DIAS DE OLIVEIRA"""
        self.professor = "Prof. M.Sc. Howard Roatti"
        self.disciplina = "Banco de Dados"
        self.semestre = "2023/2"

    def get_documents_count(self, collection_name):
        # Retorna o total de registros computado pela query
        df = config.query_count(collection_name=collection_name)
        return df[f"total_{collection_name}"].values[0]

    def get_updated_screen(self):
        return f"""
        ########################################################
        #       SISTEMA DE GESTÃO DE BIBLIOTECA ESCOLAR                     
        #                                                         
        #  TOTAL DE REGISTROS:                                    
        #      1 - LIVROS:          {str(self.get_documents_count(collection_name="livros")).rjust(5)}
        #      2 - USUÁRIOS:        {str(self.get_documents_count(collection_name="usuarios")).rjust(5)}
        #      3 - EMPRÉSTIMOS:     {str(self.get_documents_count(collection_name="emprestimos")).rjust(5)}
        #      4 - DEVOLUÇÕES:      {str(self.get_documents_count(collection_name="devolucoes")).rjust(5)}
        #
        #  GRUPO: {self.created_by}
        #
        #  PROFESSOR: {self.professor}
        #
        #  DISCIPLINA: {self.disciplina}
        #              {self.semestre}
        ########################################################
        """