import tabula
import PyPDF2
import pandas as pd
import csv
import re
import os
from PyPDF2 import PdfReader
from pdfminer.high_level import extract_text

class Linha:
    def __init__(self, banco, data, descricao, valores):
        self.banco = banco
        self.data = data
        self.descricao = descricao

        pattern_letter = r"^[a-zA-Z\W]+$"

        teste01 = re.match(pattern_letter, valores)

        if valores == '' or teste01:
            self.valores = 0
        else:
            self.valores = valores

class lendo_pdf_brasil:

    def __init__(self):
        pass

    def lendo_pdf_brasil_v1(self, pdf):

        try:
            with open(pdf, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                num_pages = len(pdf_reader.pages)
        except:
            return print("número invalido")

        lista_formatada = []

        indice = 0
        area_analisada = [[85,20,820,580]]

        for i in range(num_pages):
            indice+=1
            dfs = tabula.read_pdf(pdf, pages=indice,  lattice=True, area=area_analisada)

            lista = []

            for table in dfs:
                table.to_csv("Banco_brasil_teste01.csv")

            with open('Banco_brasil_teste01.csv', 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    lista.append(row)

            for row in lista:

                linha_analisada = row[1]

                if len(row) >= 3:
                    linha_analisada = row[-1]

                linha_splitada = re.split(r'\n', linha_analisada)

                descricao_split = linha_splitada[0]

                descricao = f'{descricao_split[10:]} {linha_splitada[-1]}'
                data = linha_analisada[:10]
                
                valor = ''

                if len(linha_splitada) >= 2:

                    positivo_ou_neg = ''

                    if '-' in linha_splitada[1]:
                        positivo_ou_neg = 'Negativo'
                    
                    if '+' in linha_splitada[1]:
                        positivo_ou_neg = 'Positivo'

                    valor_formatado = re.sub(r'\s*\(+[-+]\)\s*', '', linha_splitada[1])

                    valor = valor_formatado
                    t = re.compile(r'^[a-zA-Z]+')

                    check = t.search(valor)

                    if check:

                        partes = re.split(r'(\d+(?:,\d+)?)', valor)
                        descricao = partes[0]
                        valor_split = partes[1:]
                        valor_join = ''.join(valor_split)

                        valor = valor_join
                    
                    if positivo_ou_neg == 'Negativo':
                        valor = f'-{valor}'
                

                row_value = Linha('Banco do Brasil', data, descricao, valor)
                lista_formatada.append(row_value)

    
        return lista_formatada
  
class leitor_pdf_santander:
    
    def __init__(self):
        pass

    def lendo_pdf_santander_v1(self, pdf):

            data_pattern = r"\d{2}/\d{2}/\d{4}"
            texto = r"[a-zA-Z]\w*"

            fim_page = True

            def eh_valor_valido(valor):

                padrao = r"^-?\d{1,3}(?:\.\d{3})*,\d{2}$"
                match = re.match(padrao, valor)

                if valor == '':
                    return True

                return bool(match)

            try:
                with open(pdf, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    num_pages = len(pdf_reader.pages)
            except:
                return num_pages

            area_page01_satander = [[174,0,568,818]]
            area_restPages_santander = [[28,0,568,818]]
            lista_formatada = []
            area_analisada = area_page01_satander
            valores = 0

            indice_teste = 0

            for i in range(num_pages):
                credito = ''
                debito = ''
                saldo = ''

                indice = i+1

                dfs = tabula.read_pdf(pdf, pages=indice, area = area_analisada)
                lista = []

                for table in dfs:
                    table.to_csv("Santander_page.csv")

                    with open('Santander_page.csv', 'r') as file:
                        reader = csv.reader(file)
                        for row in reader:
                            lista.append(row)

                if fim_page == True:

                    for row in lista:
                        credito_validando, debito_validando, saldo_validando = row[-3:]

                        teste_01 = eh_valor_valido(credito_validando)
                        teste_02 = eh_valor_valido(debito_validando)
                        teste_03 = eh_valor_valido(saldo_validando) 

                        if teste_01 and teste_02 and teste_03:
                            credito, debito, saldo = row[-3:]

                        data =  ''
                        descricao = ''

                        for value in row:
                            match = re.match(data_pattern, value)
                            match_texto = re.match(texto, value)

                            teste_01 = eh_valor_valido(value)

                            if match:
                                data = value
                            if match_texto and teste_01 is False:
                                descricao = value

                        if data and descricao:
                                
                            if credito:
                                valores = credito
                            if debito:
                                valores = debito
                            

                            linha = Linha('Banco Santander', data, descricao, valores)
                            lista_formatada.append(linha)
                        
                        if descricao == '' and saldo:

                            if descricao == '' and credito == '' and debito == '' and saldo:
                                descricao = data[10:]
                                data = data[0:10]
                                
                                if credito:
                                    valores = credito
                                if debito:
                                    valores = debito

                                linha = Linha('Banco Santander', data, descricao, valores)
                                lista_formatada.append(linha)

                                indice_teste = indice + 2
                                fim_page = False

                                break

                            descricao = data[10:]
                            data = data[0:10]

                            if credito:
                                valores = credito
                            if debito:
                                valores = debito

                            linha = Linha('Banco Santander', data, descricao, valores)
                            lista_formatada.append(linha)

                        if data is False and descricao is False:
                            
                            descricao = ''
                            data = ''
                            
                            if credito:
                                valores = credito
                            if debito:
                                valores = debito
                            
                            linha = Linha('Banco Santander', data, descricao, valores)
                            lista_formatada.append(linha)

                area_analisada = area_restPages_santander

                if indice == indice_teste:
                    fim_page = True
                    area_analisada = area_page01_satander
            
            return lista_formatada

class leitor_pdf_bradesco:

    def __init__(self):
        pass

    def lendo_bradesco_celular_v1(self, pdf):
        dados = {}

        lista_formatada = []

        with open(pdf, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(pdf_reader.pages)
        
        area_analisada = [[141,35,558+242,725+35]]

        # Regex:
        data_pattern = r"\d{2}/\d{2}/\d{4}"
        pattern_letter = r"^[a-zA-Z\W]+$"

        def eh_valor_valido(valor):

                padrao = r"^-?\d{1,3}(?:\.\d{3})*,\d{2}$"
                match = re.match(padrao, valor)

                if valor == '':
                    return True

                return bool(match)

        for i in range(num_pages):

            indice = i+1

            dfs = tabula.read_pdf(pdf, pages=indice, area=area_analisada)

            lista = []

            for table in dfs:
                # Aqui você abre o documento e acrescenta o valor:
                table.to_csv("Banco_bradesco_csv", mode='a', header=False, index=False)

            with open('Banco_bradesco_csv', 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    lista.append(row)
        
        os.remove("Banco_bradesco_csv")

        # Variaveis de dados

        # Array para armazenar a descrição, e mesclar depois.
        descricao = []

        # Armazenar a variável de Data no valor.
        data = ''

        # Variável que irá realizar o controle da descrição, onde assim que atingir três, ele reconhece que é uma linha completa.
        k = 0

        # Variáveis de valores, que irá armazenar e caso Debito(True) ou se caso Credito(True)
        valores = 0

        # Variável que irá receber a descrição, transformando ela em string, e assim adicionando na Classe.
        descricaoWord = ''
        
        for row in lista:

            # Buscando datas no PDF;
            buscando_data = re.match(data_pattern, row[0])
            # buscando_descricao = re.match(pattern_letter, row[1])

            # Os valores de credito, debito e saldo, sempre estão localizados nos 3 últimos indices.
            if row[-1]:
                credito, debito, saldo = row[-3:]

            # Se buscando_data for verdadeiro, a variável data é preenchida.
            if buscando_data:
                data = row[0]

            # O código abaixo foi feito e estruturado para pegar toda a descrição da linha, a qual era separada em 3 partes, e mescla-la em uma só.
            # Caso a descrição for SALDO, ela só tem somente uma linha, portanto ela zera o contador K, e retorna o laço ao inicio, dando seguimento na proxima linha.
            if 'SALDO' in row[1]:
                # Se saldo verdadeiro, ele irá aplicar a lógica para encontrar qual o valor válido na linha, sendo ele ou Debito(Caso verdadeiro) ou Crédito(Caso verdadeiro);
                if saldo:
                    valores = '0'
                    if credito:
                        valores = credito
                    if debito:

                        # Por questões de versões diversas, alguns vem com o '-' já declarado no valor, porém caso não, ele será adicionado automaticamente pela condição a baixo.
                        if '-' in debito:
                            valores = debito
                        else:
                            valores = f'-{debito}'
                        
                    if credito and debito:
                        valores = '0'
                
                # Usando a classe Linha, para repassar os dados corretamente.
                row_value = Linha('Bradesco', data, row[1], valores)
                lista_formatada.append(row_value)
                
                # Resetando a variável K
                k = 0
                continue
            
            # Adicionando a descrição no array.
            descricao.append(row[1])

            k+=1 

            if row[1] and row[2]:
                # Se saldo verdadeiro, ele irá aplicar a lógica para encontrar qual o valor válido na linha, sendo ele ou Debito(Caso verdadeiro) ou Crédito(Caso verdadeiro);
                if saldo:
                    valores = '0'
                    if credito:
                        valores = credito
                    if debito:
                        
                        # Por questões de versões diversas, alguns vem com o '-' já declarado no valor, porém caso não, ele será adicionado automaticamente pela condição a baixo.
                        if '-' in debito:
                            valores = debito
                        else:
                            valores = f'-{debito}'
                        
                    if credito and debito:
                        valores = '0'
                
                # Resetando a variável K
                k = 0

                # O Array criado para armazenar a descrição completa da linha, é desmembrado, sendo transformado em uma string.
                for words in descricao:
                    descricaoWord += f' {words}'

                # Usando a classe Linha, para repassar os dados corretamente.
                row_value = Linha('Bradesco', data, descricaoWord, valores)
                lista_formatada.append(row_value)

                # Resetando as variáveis para amabas não acumularem valores.
                descricao = []
                descricaoWord = ''

                continue
            
            if k == 3:
                # Se saldo verdadeiro, ele irá aplicar a lógica para encontrar qual o valor válido na linha, sendo ele ou Debito(Caso verdadeiro) ou Crédito(Caso verdadeiro);
                if saldo:
                    valores = '0'
                    if credito:
                        valores = credito
                    if debito:

                        # Por questões de versões diversas, alguns vem com o '-' já declarado no valor, porém caso não, ele será adicionado automaticamente pela condição a baixo.
                        if '-' in debito:
                            valores = debito
                        else:
                            valores = f'-{debito}'

                    if credito and debito:
                        valores = '0'

                # Resetando a variável K
                k = 0

                # O Array criado para armazenar a descrição completa da linha, é desmembrado, sendo transformado em uma string.
                for words in descricao:
                    descricaoWord += f' {words}'
                
                # Usando a classe Linha, para repassar os dados corretamente.
                row_value = Linha('Bradesco', data, descricaoWord, valores)
                lista_formatada.append(row_value)

                # Resetando as variáveis para amabas não acumularem valores.
                descricaoWord = ''
                descricao = []

                continue
    
        return lista_formatada

class leitor_pdf_banco_itau:

    def __init__(self):
        pass

    def lendo_pdf_banco_itau_v1(self, pdf):
         
        # Código para pegar o número de páginas do PDF.
        with open(pdf, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(pdf_reader.pages)
        
        # Extraindo a tabela de dados:

        area_analisada = [[121,17,757,560]]
        indice = 0
        lista = []
        lista_formatada = []

        for i in range(num_pages):

            indice+=1

            dfs = tabula.read_pdf(pdf, pages=indice, stream=True, area=area_analisada)

            for table in dfs:
                table.to_csv("Banco_bradesco_csv", mode='a', header=False, index=False)
            
        with open('Banco_bradesco_csv', 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    lista.append(row)    
        
        os.remove('Banco_bradesco_csv')

        for row in lista:

            data_pattern = r"\d{2}/\d{2}"

            data_bool = re.match(data_pattern, row[0])

            if data_bool:
                data = row[0]
            
            if row[1]:
                descricao = row[1]

            if row[-2]:
                valores = row[-2]

                row_value = Linha('Banco Itau', data, descricao, valores)
                lista_formatada.append(row_value)

        return lista_formatada

    def leitor_pdf_itau_empresas_grafico(self, pdf):

        lista = []
        lista_formatada = []

        pageUm = [[583, 130, 823, 556]]
        AllPage = [[0, 82, 826, 563]]
        indice = 0

        data_pattern = r"^(0[1-9]|[12][0-9]|3[01])\/(0[1-9]|1[0-2])$"
        data_pattern_text = r"(\d{2}\/\d{2})"

        area_analisada = AllPage

        with open(pdf, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(pdf_reader.pages)
        
        for i in range(num_pages):
            indice+=1

            if indice == 1:
                area_analisada = pageUm
            else:
                area_analisada = AllPage
            
            dfs = tabula.read_pdf(pdf, pages=indice, area=area_analisada)

            for table in dfs:
                table.to_csv("Banco_bradesco_csv", mode='a', header=False, index=False)

        with open('Banco_bradesco_csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                lista.append(row)

        data = ''

        for row in lista:

            validando_data_02 = ''

            descricao = ''
            valores = ''

            validando_data_final = bool(re.match(r"\d{2}/\d{2}/\d{2}", row[0]))

            validando_data_personnalite = r"\b\d{2}/\d{2}\b"

            for value in row:
                buscando_data = re.findall(validando_data_personnalite, value)
                if buscando_data:
                    data = buscando_data[0]
                    break

            # # Variáveis iniciadas para receber os valores de input.

            # Caso as duas buscas por data for falso, aqui ele irá realizar uma nova busca dentro da Linha.
            
            for value in row:
                tem_letras_01 = bool(re.search(r"[a-zA-Z]", value))
                if tem_letras_01 and len(value) > 2:
                    descricao = value

            # Validando/encontrando valores positivos e negativos, onde os mesmo podem estar localizados nos indices do row.
            # validando_valor = r"\d+,\d{2}"

            validando_valor = r"^(?:\d{1,3}(?:\.\d{3})*,\d{2}(?:[-+])?)$"

            for value in row:
                match = re.match(validando_valor, value)

                if match:
                    valores = value
                    break

            # Valida se o valor encontrado contém texto, caso sim, ele irá retornar True.

            tem_letras_valores = bool(re.search(r"[a-zA-Z]", valores))

            if descricao and valores:
                # Caso validar a data inicial, assim evitando duplicatas, e tbm se há valores inválidos nos números, ele irá adicionar o valor no array.
                if validando_data_final is False and tem_letras_valores is False:
                    rowValue = Linha('Banco Itau Empresa - Personnalite/PJ', data, descricao, valores)
                    lista_formatada.append(rowValue)

        os.remove("Banco_bradesco_csv")

        return lista_formatada

    def leitor_pdf_itau_extrato_simples(self, pdf):

        lista = []
        data = ''
        valores = ''
        descricao = ''
        lista_formatada = []
        indice = 0
        data_pattern_text = r'\d{2}/\d{2}'

        with open(pdf, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(pdf_reader.pages)
        
        for i in range(num_pages):
            indice+=1

            dfs = tabula.read_pdf(pdf, pages=indice, area=[[0, 0, 800, 417]])
            
            for table in dfs:
                table.to_csv('Banco_itau_extrato_simples.csv', mode='a', header=False, index=False)
        
        with open('Banco_itau_extrato_simples.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                lista.append(row)
        
        os.remove('Banco_itau_extrato_simples.csv')

        for row in lista:
            # Buscando data.
            for value in row:
                validando_data = re.findall(data_pattern_text, value)
                if validando_data:
                    data = validando_data[0]
                    break
            
            # Buscando valores.
            for value in row:
                validando_valor = r"\d+,\d{2}"
                buscando_valor = re.findall(validando_valor, value)

                if buscando_valor:
                    valores = value
                    break
            
            for value in row:
                tem_letras = bool(re.search(r"[a-zA-Z]", value))
                if tem_letras:
                    descricao = value
                    break
            
            tem_letras_valores = bool(re.search(r"[a-zA-Z]", valores))

            print(f'Linha analisada: {row}, data extraída: {data}')

            if tem_letras_valores is False and valores is not '0':
                rowValue = Linha('Banco do Itaú - Extrato simples', data, descricao, valores)
                lista_formatada.append(rowValue)
        
        return lista_formatada

    def leitor_pdf_itau_uniclass(self, pdf):

        with open(pdf, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(pdf_reader.pages)

        areaPageUm = [[259, 23, 825, 572]]
        areaPageAll = [[19, 19, 828, 570]]

        # regex para buscar valores padrões:
        data_pattern = r"\d{2}/\d{2}/\d{4}"
        texto = r".*[a-zA-Z]+.*"
        validando_valor = r"^-?\d{1,3}(?:\.\d{3})*,\d{2}$"

        # Variaveis de validação.
        data = ''
        descricao = ''
        indice = 0

        splitando = []

        lista = []
        lista_formatada = []

        area_analisada = ''

        for i in range(num_pages):
            indice+=1

            if indice == 1:
                area_analisada = areaPageUm
            else:
                area_analisada = areaPageAll

            dfs = tabula.read_pdf(pdf, pages=indice, area=area_analisada, stream=True)

            if indice == 1:
                print(dfs)
            
            for table in dfs:
                table.to_csv('Banco_itau_extrato_simples.csv', mode='a', index=False)

        with open('Banco_itau_extrato_simples.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                lista.append(row)
        
        os.remove('Banco_itau_extrato_simples.csv')
        
        for row in lista:

            valores = ''

            for value in row:
                match_data = re.match(data_pattern, value)
                match_valor = re.match(validando_valor, value)

                if match_data:
                    data = value[:10]
                if match_valor:
                    valores = value

                if len(row) >= 2:
                    splitando = row[1].split()

                # Separando o valor da descrição, já que em algumas colunas ambos vem grudados.
                for value in splitando:
                    match = re.search(validando_valor, value)
                    if match:
                        valores = match.group(0)
                
            for value in row:
                match_descricao = re.match(texto, value)

                if match_descricao:
                    
                    # Aqui você encontra uma gambiarra para solucionar a vinda de descrição com valores.
                    descricao = value
                    if 'R$' in descricao:
                        descricao = 'Saldo Conta'
                    break

            if valores:
                rowValue = Linha('banco itaú - uniclass', data, descricao, valores)
                lista_formatada.append(rowValue)

        return lista_formatada
            
class PdfReaderVersion:
    
    def __init__(self):
        pass
    
    def extraindo_texto(self, pdf):
        try:
            reader = PyPDF2.PdfReader(pdf)
            page = reader.pages[0]
            text = page.extract_text()

        except:
            text = extract_text(pdf)
        
        return text

class to_excel:

    def transformando_excel(self, lista):

        with open('extrato_lido.csv', 'w', newline='') as arquivo_csv:
            escritor_csv = csv.writer(arquivo_csv)

            escritor_csv.writerow(["Banco", "Data", "Descricao", 'Descricao', "Valores"])

            for row in lista:
                escritor_csv.writerow([row.banco, row.data, row.descricao, row.descricao, row.valores])

        try:
            df = pd.read_csv('extrato_lido.csv', encoding='mac_roman')
        except:
            return print("Formatação incorreta")
        
        df.to_excel('Banco_do_brasil.xlsx', index=False)








 
















