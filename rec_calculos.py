#Funções de calculo para o painel de reconhecimentos
import pandas as pd
from datetime import datetime, timedelta, timezone

def definir_posicoes(dados, principios):
    # Seleciona as colunas desejadas e classifica com base na coluna '15d_Recebidos'
    dfrecebidos = dados[['nome_sobrenome', '15d_Recebidos','15d_Enviados']]
    dfrecebidos = dfrecebidos.sort_values(by='15d_Recebidos', ascending=False)
    
    # Obtém as três primeiras linhas como um DataFrame
    top_3 = dfrecebidos.head(3)
    
    # Acessa os valores individuais das colunas 'nome_sobrenome' e '15d_Recebidos'
    recebido1 = top_3.iloc[0]['nome_sobrenome']
    recebido2 = top_3.iloc[1]['nome_sobrenome']
    recebido3 = top_3.iloc[2]['nome_sobrenome']
    pontosR1 = top_3.iloc[0]['15d_Recebidos']
    pontosR2 = top_3.iloc[1]['15d_Recebidos']
    pontosR3 = top_3.iloc[2]['15d_Recebidos']
    
    dfrecebidos = dfrecebidos.sort_values(by='15d_Enviados', ascending=False)
    
    top_3 = dfrecebidos.head(3)
    
    enviado1 = top_3.iloc[0]['nome_sobrenome']
    enviado2 = top_3.iloc[1]['nome_sobrenome']
    enviado3 = top_3.iloc[2]['nome_sobrenome']
    pontosE1 = top_3.iloc[0]['15d_Enviados']
    pontosE2 = top_3.iloc[1]['15d_Enviados']
    pontosE3 = top_3.iloc[2]['15d_Enviados']
    
    total15dE=dfrecebidos['15d_Enviados'].sum()
    num_receptores = dfrecebidos['15d_Recebidos'].ne(0).sum()
    
    return total15dE, num_receptores, recebido1, recebido2, recebido3, pontosR1, pontosR2, pontosR3, enviado1, enviado2, enviado3, pontosE1,pontosE2, pontosE3


def definir_principios(dados):
    dftodos = dados[['nome_sobrenome','15d_Integridade','15d_Excelência','15d_Evolução','15d_Empatia','15d_Longo Prazo']]

    #Integridade
    dfii = dftodos[['nome_sobrenome','15d_Integridade']]
    dfii = dfii.sort_values(by='15d_Integridade', ascending=False)
    top1_ii = dfii.iloc[0]['nome_sobrenome']
    top2_ii = dfii.iloc[1]['nome_sobrenome']
    top3_ii = dfii.iloc[2]['nome_sobrenome']
    pont1_ii = dfii.iloc[0]['15d_Integridade']
    pont2_ii = dfii.iloc[1]['15d_Integridade']
    pont3_ii = dfii.iloc[2]['15d_Integridade']
    
    #Excelência
    dfex = dftodos[['nome_sobrenome', '15d_Excelência']]
    dfex = dfex.sort_values(by='15d_Excelência', ascending = False)
    top1_ex = dfex.iloc[0]['nome_sobrenome']
    top2_ex = dfex.iloc[1]['nome_sobrenome']
    top3_ex = dfex.iloc[2]['nome_sobrenome']
    pont1_ex = dfex.iloc[0]['15d_Excelência']
    pont2_ex = dfex.iloc[1]['15d_Excelência']
    pont3_ex = dfex.iloc[2]['15d_Excelência']
    
    #Evolução
    dfei = dftodos[['nome_sobrenome', '15d_Evolução']]
    dfei = dfei.sort_values(by='15d_Evolução', ascending = False)
    top1_ei = dfei.iloc[0]['nome_sobrenome']
    top2_ei = dfei.iloc[1]['nome_sobrenome']
    top3_ei = dfei.iloc[2]['nome_sobrenome']
    pont1_ei = dfei.iloc[0]['15d_Evolução']
    pont2_ei = dfei.iloc[1]['15d_Evolução']
    pont3_ei = dfei.iloc[2]['15d_Evolução']
    
    #Empatia
    dfct = dftodos[['nome_sobrenome', '15d_Empatia']]
    dfct = dfct.sort_values(by='15d_Empatia', ascending = False)
    top1_ct = dfct.iloc[0]['nome_sobrenome']
    top2_ct = dfct.iloc[1]['nome_sobrenome']
    top3_ct = dfct.iloc[2]['nome_sobrenome']
    pont1_ct = dfct.iloc[0]['15d_Empatia']
    pont2_ct = dfct.iloc[1]['15d_Empatia']
    pont3_ct = dfct.iloc[2]['15d_Empatia']   
    
    #Longo Prazo
    dfdd = dftodos[['nome_sobrenome', '15d_Longo Prazo']]
    dfdd = dfdd.sort_values(by='15d_Longo Prazo', ascending = False)
    top1_dd = dfdd.iloc[0]['nome_sobrenome']
    top2_dd = dfdd.iloc[1]['nome_sobrenome']
    top3_dd = dfdd.iloc[2]['nome_sobrenome']
    pont1_dd = dfdd.iloc[0]['15d_Longo Prazo']
    pont2_dd = dfdd.iloc[1]['15d_Longo Prazo']
    pont3_dd = dfdd.iloc[2]['15d_Longo Prazo']   
    
    
    return str(top1_ii), str(pont1_ii), str(top2_ii), str(pont2_ii), str(top3_ii), str(pont3_ii), str(top1_ex), str(pont1_ex), str(top2_ex), str(pont2_ex), str(top3_ex), str(pont3_ex), str(top1_ei), str(pont1_ei), str(top2_ei), str(pont2_ei), str(top3_ei), str(pont3_ei), str(top1_ct), str(pont1_ct), str(top2_ct), str(pont2_ct), str(top3_ct), str(pont3_ct), str(top1_dd), str(pont1_dd), str(top2_dd), str(pont2_dd), str(top3_dd), str(pont3_dd)


def definir_geral(dados):
    ii = dados['15d_Integridade'].sum()
    ex = dados['15d_Excelência'].sum()
    ei = dados['15d_Evolução'].sum()
    ct = dados['15d_Empatia'].sum()
    dd = dados['15d_Longo Prazo'].sum()
    
    return ii, ex, ei, ct, dd


def contagem(supabase):
    
    colaboradores_response = supabase.table('colaboradores').select('*').eq('removed', False).execute()
    colaboradores_data = colaboradores_response.data
    dfcolaboradores = pd.DataFrame(colaboradores_data).sort_values(by='nome_completo', ascending=True)

    reconhecimentos_response = supabase.table('reconhecimentos').select('*').execute()
    reconhecimentos_data = reconhecimentos_response.data
    dfreconhecimentos = pd.DataFrame(reconhecimentos_data)

    princípios = ['Integridade',
                'Excelência', 
                'Evolução', 
                'Empatia', 
                'Longo Prazo',
    ]

    princípios_novos = [
        'Integridade Inabalável',
        'Excelência nos Mínimos Detalhes',
        'Evolução Incessante',
        'Colaboração Nas Trincheiras',
        'Dados e Decisões, Nunca o Contrário'
    ]

    # Contagem para All time
    for email in dfcolaboradores['email']:
        for i in range(5):
            contagem = len(dfreconhecimentos[(dfreconhecimentos['receptor'] == email) & (dfreconhecimentos['princípio'] == princípios[i])]) + len(dfreconhecimentos[(dfreconhecimentos['receptor'] == email) & (dfreconhecimentos['princípio'] == princípios_novos[i])])
            coluna_de_contagem = 'at_' + princípios[i]
            dfcolaboradores.loc[dfcolaboradores['email'] == email, coluna_de_contagem] = int(contagem)
            
    for email in dfcolaboradores['email']:
        contagem = len(dfreconhecimentos[(dfreconhecimentos['enviador'] == email)])
        dfcolaboradores.loc[dfcolaboradores['email'] == email, 'at_Enviados'] = int(contagem)

    # Calcular a soma dessas colunas e criar/atualizar a coluna 'at_Recebidos'
    dfcolaboradores['at_Recebidos'] = dfcolaboradores[['at_' + p for p in princípios]].sum(axis=1)

    # Contagem para 15 dias
    # Convertendo 'created_at' para datetime
    dfreconhecimentos['created_at'] = pd.to_datetime(dfreconhecimentos['created_at'], utc=True)
    dfreconhecimentos['created_at'] = dfreconhecimentos['created_at'].dt.date# Arredonda para segundos


    # Definindo o limite dos últimos 15 dias
    limite_15d = datetime.now(timezone.utc) - timedelta(days=15)
    limite_15d = limite_15d.date()

    # Filtrar reconhecimentos dos últimos 15 dias
    df_ultimos_15d = dfreconhecimentos[dfreconhecimentos['created_at'] > limite_15d]

    for email in dfcolaboradores['email']:
        for i in range(5):
            contagem_15d = len(df_ultimos_15d[(df_ultimos_15d['receptor'] == email) & (df_ultimos_15d['princípio'] == princípios[i])]) + len(df_ultimos_15d[(df_ultimos_15d['receptor'] == email) & (df_ultimos_15d['princípio'] == princípios_novos[i])])
            coluna_de_contagem_15d = '15d_' + princípios[i]
            dfcolaboradores.loc[dfcolaboradores['email'] == email, coluna_de_contagem_15d] = int(contagem_15d)

        # Calcular a soma das colunas de contagem dos últimos 15 dias
        dfcolaboradores.loc[dfcolaboradores['email'] == email, '15d_Recebidos'] = dfcolaboradores.loc[dfcolaboradores['email'] == email, ['15d_' + p for p in princípios]].sum(axis=1)
    for email in dfcolaboradores['email']:
        dfcolaboradores.loc[dfcolaboradores['email'] == email, '15d_Enviados'] = int(contagem_15d)
        contagem_15d = len(df_ultimos_15d[(df_ultimos_15d['enviador'] == email)])
    # Fim das contagens
        
    # Converter o DataFrame atualizado para uma lista de dicionários
    dados_atualizados = dfcolaboradores.to_dict(orient='records')

    # Enviar a lista atualizada para o Supabase
    supabase.table('colaboradores').upsert(dados_atualizados).execute()

    return None
