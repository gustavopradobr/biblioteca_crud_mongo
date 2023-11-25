# Biblioteca CRUD MongoDB 📚

Este projeto representa um sistema de gerenciamento de biblioteca escolar, contendo coleções como: usuarios, livros, emprestimos e devolucoes.

O sistema exige que as coleções existam, então basta executar o script Python a seguir para criação das coleções e preenchimento de dados de exemplos:
```shell
~$ python createCollectionsAndData.py
```
**Atenção: tendo em vista que esse projeto é continuidade do [biblioteca_crud_oracle](https://github.com/gustavopradobr/biblioteca_crud_oracle), é importante que as tabelas do Oracle existam e estejam preenchidas, pois o script _createCollectionsAndData.py_ irá realizar uma consulta em cada uma das tabelas e preencher as _collections_ com os novos _documents_.**

Para executar o sistema basta executar o script Python a seguir:
```shell
~$ python principal.py
```

## Organização
- [diagrams](diagrams): Nesse diretório está o [diagrama relacional](diagrams/BIBLIOTECA_DIAGRAMA_RELACIONAL.pdf) (lógico) do sistema.
    * O sistema possui quatro entidades: USUARIOS, LIVROS, EMPRESTIMOS e DEVOLUCOES
- [src](src): Nesse diretório estão os scripts do sistema
    * [conexion](src/conexion): Nesse repositório encontra-se o [módulo de conexão com o banco de dados Oracle](src/conexion/oracle_queries.py) e o [módulo de conexão com o banco de dados Mongo](src/conexion/mongo_queries.py). Esses módulos possuem algumas funcionalidades úteis para execução de instruções. O módulo do Oracle permite obter como resultado das queries JSON, Matriz e Pandas DataFrame. Já o módulo do Mongo apenas realiza a conexão, os métodos CRUD e de recuperação de dados são implementados diretamente nos objetos controladores (_Controllers_) e no objeto de Relatório (_reports_).
      - Exemplo de utilização para conexão no Mongo;
      ```python
            # Importa o módulo MongoQueries
            from conexion.mongo_queries import MongoQueries
            
            # Cria o objeto MongoQueries
            mongo = MongoQueries()

            # Realiza a conexão com o Mongo
            mongo.connect()

            """<inclua aqui suas declarações>"""

            # Fecha a conexão com o Mong
            mongo.close()
      ```
      - Exemplo de criação de um documento no Mongo:
      ```python
            from conexion.mongo_queries import MongoQueries
            import pandas as pd
            
            # Cria o objeto MongoQueries
            mongo = MongoQueries()

            # Realiza a conexão com o Mongo
            mongo.connect()

            #Solicita o título do livro
            titulo_livro = input("Título: ")
            #Solicita o nome do autor do livro
            autor_livro = input("Autor: ")
            #Solicita o ano de publicação do livro
            ano_publicacao_livro = int(input("Ano de publicação (número): "))
            #Solicita a quantidade de exemplares do livro
            qtd_livro = int(input("Quantidade (número): "))

            # Gera o próximo id incremental da coleção livros
            proximo_id = self.mongo.db["livros"].aggregate([
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
            proximo_id = int(list(proximo)[0]['proximo_livro'])

            # Insere e persiste o novo livro
            mongo.db["livros"].insert_one({"id_livro": proximo_id, "titulo": titulo_livro, "autor": autor_livro, "ano_publicacao": ano_publicacao_livro "quantidade": qtd_livro})

            # Recupera os dados do novo livro criado transformando em um DataFrame
            df_livro = pd.DataFrame(list(mongo.db["livros"].find({"id_livro":int(proximo_id)}, {"id_livro": 1, "titulo": 1, "autor": 1, "ano_publicacao": 1, "quantidade": 1, "_id": 0})))

            # Exibe os dados do livro em formato DataFrame
            print(df_livro)

            # Fecha a conexão com o MongoDB
            mongo.close()
      ```
    * [controller](src/controller/): Nesse diretório encontram-sem as classes controladoras, responsáveis por realizar inserção, alteração e exclusão dos registros das tabelas.
    * [model](src/model/): Nesse diretório encontram-ser as classes das entidades descritas no [diagrama relacional](diagrams/BIBLIOTECA_DIAGRAMA_RELACIONAL.pdf)
    * [reports](src/reports/) Nesse diretório encontra-se a [classe](src/reports/relatorios.py) responsável por gerar todos os relatórios do sistema
    * [utils](src/utils/): Nesse diretório encontram-se scripts de [configuração](src/utils/config.py) e automatização da [tela de informações iniciais](src/utils/splash_screen.py)
    * [createCollectionsAndData.py](src/createCollectionsAndData.py): Script responsável por criar as tabelas e registros fictícios. Esse script deve ser executado antes do script [principal.py](src/principal.py) para gerar as tabelas, caso não execute os scripts diretamente no SQL Developer ou em alguma outra IDE de acesso ao Banco de Dados.
    * [principal.py](src/principal.py): Script responsável por ser a interface entre o usuário e os módulos de acesso ao Banco de Dados. Deve ser executado após a criação das tabelas.

### Bibliotecas Utilizadas
- [requirements.txt](src/requirements.txt): `pip install -r requirements.txt`