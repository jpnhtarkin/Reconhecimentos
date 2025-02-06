

import dash
from dash import html, dcc, Input, Output, State, no_update
from supabase import create_client, Client
import dash_bootstrap_components as dbc
from flask import Flask
from flask_caching import Cache
from dotenv import load_dotenv
import os, datetime
import pandas as pd
from rec_calculos import *
from flask_apscheduler import APScheduler


def atualizar_colaboradores():
    contagem(supabase)
    colaboradores_response = supabase.table('colaboradores').select('*').eq('removed', False).execute()
    colaboradores_data = colaboradores_response.data
    dfcolaboradores = pd.DataFrame(colaboradores_data).sort_values(by='nome_completo', ascending=True)
    return dfcolaboradores


# Supabase setup
load_dotenv()

url  = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

cache_config = {
    "DEBUG": True,       
    "CACHE_TYPE": "SimpleCache",  
    "CACHE_DEFAULT_TIMEOUT": 60
}

colaboradores_response = supabase.table('colaboradores').select('*').eq('removed', False).execute()
colaboradores_data = colaboradores_response.data

server = Flask(__name__)
server.config.from_mapping(cache_config)
cache = Cache(server)
server.config["SECRET_KEY"] = os.getenv('SECRET_KEY')

app = dash.Dash(__name__, 
                server=server, 
                external_stylesheets=[dbc.themes.UNITED], 
                suppress_callback_exceptions=True)
app.css.append_css({'external_url':'/assets/shared.css'})
app.css.append_css({'external_url':'/assets/rankings.css'})
app.css.append_css({'external_url':'/assets/principios.css'})
app.css.append_css({'external_url':'/assets/formulario.css'})


scheduler = APScheduler()
scheduler.init_app(server)
scheduler.start()

principios_response = supabase.table('princípios').select('*').execute()
principios_data = principios_response.data

# Transform principios_data into the desired format
principios_dimensoes = {}


for record in principios_data:
    for key, value in record.items():
        if value is not None:
            if key not in principios_dimensoes:
                principios_dimensoes[key] = []
            principios_dimensoes[key].append(value)
       
            
princípios = ['Integridade',
              'Excelência', 
              'Evolução', 
              'Empatia', 
              'Longo Prazo',
]


# função para encontrar o email via nome
def encontrar_email_por_nome(nome_completo, data):
    for item in data:
        if item['nome_completo'] == nome_completo:
            return item['email']
    return None



def layout_principal():
    return html.Div([
        dcc.Location(id='url', refresh=False),
        dcc.Store(id='old_ranks'),
        dcc.Store(id='stored_principios'),
        dcc.Store(id='stored_rankings'),
        html.Div([
            dbc.Row([
                dbc.Col(html.H1("Reconhecimento dos Colaboradores", className="header_title"))
                ]),
            dbc.Row(children=[
            dbc.Card(
            dcc.Link('Princípios', href='/principios',className='link'),
            className = 'menu_card'),
            html.Br(),
            dbc.Card(
            dcc.Link('Rankings', href='/rankings',className='link'),
            className = 'menu_card'),
            html.Br(),
            dbc.Card(
            dcc.Link('Formulário', href='/formulario',className='link'),
            className = 'menu_card'),
        ], className='menu'),
        html.Div(id='conteudo_principal')  # Conteúdo atualizado pela URL
        ]),
    ], className="main_container")


def layout_rankings ():
    return dbc.Container(children=[
        dcc.Interval(id='update_interval', interval=1000*60*15, n_intervals=0),
        dcc.Store(id='top3_store', storage_type='memory'),
        dbc.Row(children=[ 
            dbc.Row([
                dbc.Col(html.H2("Total de reconhecimentos", className="general_title"), ),
                dbc.Col(html.H2("# Reconhecidos", className='general_title'), ),
            ]),
            dbc.Row(children=[
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H2(id="total15dE", className='general_number'),
                        ]),
                    ], className='card_general card_center'),
                ],),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H2(id="num_receptores", className='general_number'),
                        ]),
                    ], className='card_general card_center'),
                ]),
            ]),
        ],className = 'row_general'),
        dbc.Row([
            dbc.Col(html.H2("Top Reconhecidos", className= "top3_title1"),align='center')
        ]),
        dbc.Row(children=([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H2(id="2_recebido" ,className='position_title2'),
                        html.H3(id="pontosR2", className='pontuação'),
                    ]),
                ], className='custom_card2'),
            ], className='d_flex justify_content_center'),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H2(id='1_recebido',className='position_title1'),
                        html.H3(id='pontosR1', className='pontuação'),
                    ]),
                ], className='custom_card1'),
            ],className='d_flex justify_content_center'),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H2(id='3_recebido',className='position_title3'),
                        html.H3(id='pontosR3', className='pontuação'),
                    ]),
                ], className='custom_card3'),
            ],className='d_flex justify_content_center'),
        ]), className = 'podium_container d_flex justify_content_center'),
        dbc.Row([
            dbc.Col(
                html.H2("Top Enviadores", className='top3_title2'),align='center')
        ]),
        dbc.Row(children=([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H2(id="1_enviado" ,className='enviado_title'),
                        html.H3(id="pontosE1", className='pontuação2'),
                    ]),
                ], className='card_enviado'),
            ]),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H2(id='2_enviado',className='enviado_title'),
                        html.H3(id='pontosE2', className='pontuação2'),
                    ]),
                ], className='card_enviado'),
            ], width=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H2(id='3_enviado',className='enviado_title'),
                        html.H3(id='pontosE3', className='pontuação2'),
                    ]),
                ], className='card_enviado'),
            ], width=4),
        ]), className = 'podium_container'),
                
    ], className="main_container")


def layout_principios():
    return dbc.Container(children=[
        dcc.Store ( id = 'top3_principios', storage_type = 'memory'),
        dcc.Store ( id = 'principios_geral', storage_type = 'memory'),
        dcc.Interval(id='update_interval_geral',interval = 1000*60*15, n_intervals = 0),
        dcc.Interval(id='update_interval_top3',interval = 1000*60*15, n_intervals = 0),
        dbc.Container(children=[
            dbc.Row(children=[
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(children=[
                                html.H2("Integridade Inabalável",className = 'nome_principio'),
                                html.H3(id = 'valorii', className='valor_principiog')
                        ]), className = 'card_principio'
                        ),
                    className='d_flex justify_content_center'
                    ),
                    dbc.Col([
                        dbc.Card(children=[
                            dbc.CardBody(
                                html.H2(id = 'top1_ii', className = 'nome')
                            ),
                                html.H3(id = 'pont1_ii', className ='valor_principior' ),
                        ],className = 'card_ranks'),
                    ],className = 'card_container'),
                    dbc.Col([
                        dbc.Card(children=[
                            dbc.CardBody(
                                html.H2(id = 'top2_ii', className = 'nome')
                            ),
                                html.H3(id = 'pont2_ii', className ='valor_principior' ),
                        ],className = 'card_ranks'),
                    ],className = 'card_container'),
                    dbc.Col([
                        dbc.Card(children=[
                            dbc.CardBody(
                                html.H2(id = 'top3_ii', className = 'nome')
                            ),
                                html.H3(id = 'pont3_ii', className ='valor_principior' ),
                        ],className = 'card_ranks'),
                    ],className = 'card_container'),
                ],className='row_principio'),
            dbc.Row(children=[
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(children=[
                                html.H2("Excelência nos Mínimos Detalhes",className = 'nome_principio'),
                                html.H3(id = 'valorex', className='valor_principiog')
                        ]), className = 'card_principio'
                        ),
                    className='d_flex justify_content_center'
                    ),
                    dbc.Col([
                        dbc.Card(children=[
                            dbc.CardBody(
                                html.H2(id = 'top1_ex', className = 'nome'),
                            ),
                            html.H3(id = 'pont1_ex', className ='valor_principior' ),
                        ],className = 'card_ranks'),
                    ],className = 'card_container'),
                    dbc.Col([
                        dbc.Card(children=[
                            dbc.CardBody(
                                html.H2(id = 'top2_ex', className = 'nome'),
                            ),
                            html.H3(id = 'pont2_ex', className ='valor_principior' ),
                        ],className = 'card_ranks'),
                    ],className = 'card_container'),
                    dbc.Col([
                        dbc.Card(children=[
                            dbc.CardBody(
                                html.H2(id = 'top3_ex', className = 'nome'),
                            ),
                            html.H3(id = 'pont3_ex', className ='valor_principior' ),
                        ],className = 'card_ranks'),
                    ],className = 'card_container'),
                ],className='row_principio'),
            dbc.Row(children=[
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(children=[
                                html.H2("Evolução Incessante",className = 'nome_principio'),
                                html.H3(id = 'valorei', className='valor_principiog')
                        ]), className = 'card_principio'
                        ),
                    className='d_flex justify_content_center'
                    ),
                    dbc.Col([
                        dbc.Card(children=[
                            dbc.CardBody(
                                html.H2(id = 'top1_ei', className = 'nome'),
                            ),
                                html.H3(id = 'pont1_ei', className ='valor_principior' ),
                        ],className = 'card_ranks'),
                    ],className = 'card_container'),
                    dbc.Col([
                        dbc.Card(children=[
                            dbc.CardBody(
                                html.H2(id = 'top2_ei', className = 'nome'),
                            ),
                                html.H3(id = 'pont2_ei', className ='valor_principior' ),
                        ],className = 'card_ranks'),
                    ],className = 'card_container'),
                    dbc.Col([
                        dbc.Card(children=[
                            dbc.CardBody(
                                html.H2(id = 'top3_ei', className = 'nome'),
                            ),
                                html.H3(id = 'pont3_ei', className ='valor_principior' ),
                        ],className = 'card_ranks'),
                    ],className = 'card_container'),
                ],className='row_principio'),
            dbc.Row(children=[
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(children=[
                                html.H2("Colaboração nas Trincheiras",className = 'nome_principio'),
                                html.H3(id = 'valorct', className='valor_principiog')
                        ]), className = 'card_principio'
                        ),
                    className='d_flex justify_content_center'
                    ),
                    dbc.Col([
                        dbc.Card(children=[
                            dbc.CardBody(
                                html.H2(id = 'top1_ct', className = 'nome'),
                            ),
                                html.H3(id = 'pont1_ct', className ='valor_principior' )
                        ],className = 'card_ranks'),
                    ],className = 'card_container'),
                    dbc.Col([
                        dbc.Card(children=[
                            dbc.CardBody(
                                html.H2(id = 'top2_ct', className = 'nome'),
                            ),
                                html.H3(id = 'pont2_ct', className ='valor_principior' )
                        ],className = 'card_ranks'),
                    ],className = 'card_container'),
                    dbc.Col([
                        dbc.Card(children=[
                            dbc.CardBody(
                                html.H2(id = 'top3_ct', className = 'nome'),
                            ),
                                html.H3(id = 'pont3_ct', className ='valor_principior' )
                        ],className = 'card_ranks'),
                    ],className = 'card_container'),
                ],className='row_principio'),
            dbc.Row(children=[
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(children=[
                                html.H2("Dados e Decisões",className = 'nome_principio'),
                                html.H3(id = 'valordd', className='valor_principiog')
                        ]), className = 'card_principio'
                        ),
                    className='d_flex justify_content_center'
                    ),
                    dbc.Col([
                        dbc.Card(children=[
                            dbc.CardBody(
                                html.H2(id = 'top1_dd', className = 'nome'),
                            ),
                            html.H3(id = 'pont1_dd', className ='valor_principior' ),
                        ],className = 'card_ranks'),
                    ],className = 'card_container'),
                    dbc.Col([
                        dbc.Card(children=[
                            dbc.CardBody(
                                html.H2(id = 'top2_dd', className = 'nome'),
                            ),
                            html.H3(id = 'pont2_dd', className ='valor_principior' ),
                        ],className = 'card_ranks'),
                    ],className = 'card_container'),
                    dbc.Col([
                        dbc.Card(children=[
                            dbc.CardBody(
                                html.H2(id = 'top3_dd', className = 'nome'),
                            ),
                            html.H3(id = 'pont3_dd', className ='valor_principior' ),
                        ],className = 'card_ranks'),
                    ],className = 'card_container'),
                ],className='row_principio'),
        ]),
    ], className="main_container")


def layout_formulario():
    return dbc.Container([
        dbc.Row(dbc.Col(html.Div(id='submission_status', className="submission_status"))),
        dbc.Row(dbc.Col([
            dcc.Input(id='email_input', type='email', placeholder='Digite seu email', className="email_input"),
            html.Button('Entrar', id='email_button', className="enter_button"),
            html.Div(id='form_content', style={'display': 'none'})
        ], width=12))
    ], className="main_container")


def create_form():
    dfcolaboradores = get_cached_dfcolaboradores()
    colaboradores = dfcolaboradores['nome_completo'].tolist()
    form_style = {'border': '1px solid #ccc', 'border_radius': '10px', 'padding': '20px', 'margin': '20px auto', 'max_width': '600px'}
    question_style = {'margin': '15px 0'}

    return html.Div([
        html.Div(html.Label("Quem está recebendo o reconhecimento?", className="question_label"), style=question_style),
        dcc.Dropdown(id='colaborador_dropdown', options=[{'label': nome, 'value': nome} for nome in colaboradores], className="dropdown"),

        html.Div(html.Label("Em qual princípio ele se destacou?", className="question_label"), style=question_style),
        dcc.Dropdown(id='principio_dropdown', options=[{'label': p, 'value': p} for p in principios_dimensoes.keys()], className="dropdown"),

        html.Div([
            html.Label("Seleciona a dimensão onde seu colega mais se destacou", className="question_label", style=question_style),
            html.Div(
                dcc.RadioItems(id='dimensoes_checklist', options=[], value=None, inline=False, className="radio"),
                className="dimensoes_container"
            )
        ], style=question_style),

        html.Div([
            html.Div(html.Label("Comente objetivamente o que motivou esse reconhecimento", className="question_label"), style=question_style),
            dcc.Textarea(
                id='comentario_textarea',
                maxLength=250,  # Set the maximum number of characters
                className="textarea",
                style={'width': '100%', 'height': '75px', 'margin': '0 auto'}  # Keep the size of the textarea
            ),
        ]),

        html.Button('Enviar', id='submit_button', className="submit_button")
    ], style=form_style, className="main_container")


@app.callback(
    Output('top3_principios', 'data'),
    [Input('update_interval_top3', 'n_intervals')]
)
def update_top_all(n_intervals):
    dfcolaboradores = get_cached_dfcolaboradores()
    top_values = definir_principios(dfcolaboradores)
    result_string = ",".join(map(str, top_values))
    return result_string


@app.callback(
    [Output('top1_ii','children'),
     Output('pont1_ii','children'),
     Output('top2_ii','children'),
     Output('pont2_ii','children'),
     Output('top3_ii','children'),
     Output('pont3_ii','children'),
     Output('top1_ex','children'),
     Output('pont1_ex','children'),
     Output('top2_ex','children'),
     Output('pont2_ex','children'),
     Output('top3_ex','children'),
     Output('pont3_ex','children'),
     Output('top1_ei','children'),
     Output('pont1_ei','children'),
     Output('top2_ei','children'),
     Output('pont2_ei','children'),
     Output('top3_ei','children'),
     Output('pont3_ei','children'),
     Output('top1_ct','children'),
     Output('pont1_ct','children'),
     Output('top2_ct','children'),
     Output('pont2_ct','children'),
     Output('top3_ct','children'),
     Output('pont3_ct','children'),
     Output('top1_dd','children'),
     Output('pont1_dd','children'),
     Output('top2_dd','children'),
     Output('pont2_dd','children'),
     Output('top3_dd','children'),
     Output('pont3_dd','children')],
    [Input('top3_principios','data')],
)
def update_top_principios(top3_principios, *args):
    top_values = top3_principios.split(',')
    return top_values


@app.callback (
    Output('principios_geral', 'data'),
    [Input('update_interval_geral', 'n_intervals')]
)
def update_geral_all(n_intervals):
    dfcolaboradores = get_cached_dfcolaboradores()
    ii, ex, ei, ct, dd = definir_geral(dfcolaboradores)
    return[ii, ex, ei, ct, dd]    


@app.callback(
    [Output('valorii', 'children'),
     Output('valorex','children'),
     Output('valorei','children'),
     Output('valorct','children'),
     Output('valordd','children')],
    [Input('principios_geral', 'data')],
    [State('valorii', 'children'),
     State('valorex','children'),
     State('valorei','children'),
     State('valorct','children'),
     State('valordd','children')],
)
def update_geral(geral, valorii, valorex, valorei, valorct, valordd):
    ii, ex, ei, ct, dd = geral
    return ii, ex, ei, ct, dd
    

@app.callback(
    Output('top3_store', 'data'),
    [Input('update_interval', 'n_intervals')]
)
def update_top_3(n_intervals):
    dfcolaboradores = get_cached_dfcolaboradores()
    total15dE, num_receptores, recebido1, recebido2, recebido3, pontosR1, pontosR2, pontosR3, enviado1, enviado2, enviado3, pontosE1,pontosE2, pontosE3 = definir_posicoes(dfcolaboradores, princípios)
    return [total15dE, num_receptores, recebido1, recebido2, recebido3, pontosR1, pontosR2, pontosR3, enviado1, enviado2, enviado3, pontosE1,pontosE2, pontosE3]


@app.callback(
    [Output('total15dE', 'children'),
     Output('num_receptores', 'children'),
     Output('1_recebido', 'children'),
     Output('2_recebido', 'children'),
     Output('3_recebido', 'children'),
     Output('pontosR1', 'children'),
     Output('pontosR2', 'children'),
     Output('pontosR3', 'children'),
     Output('1_enviado', 'children'),
     Output('2_enviado', 'children'),
     Output('3_enviado', 'children'),
     Output('pontosE1', 'children'),
     Output('pontosE2', 'children'),
     Output('pontosE3', 'children')],
    [Input('top3_store', 'data')],
    [State('total15dE', 'children'),
     State('num_receptores', 'children'),
     State('1_recebido', 'children'),
     State('2_recebido', 'children'),
     State('3_recebido', 'children'),
     State('pontosR1', 'children'),
     State('pontosR2', 'children'),
     State('pontosR3', 'children'),
     State('1_enviado', 'children'),
     State('2_enviado', 'children'),
     State('3_enviado', 'children'),
     State('pontosE1', 'children'),
     State('pontosE2', 'children'),
     State('pontosE3', 'children')]
)
def update_top_3_elements(top_3_data, total15dE, num_receptores, recebido1, recebido2, recebido3, pontosR1, pontosR2, pontosR3, enviado1, enviado2, enviado3, pontosE1,pontosE2, pontosE3):
    total15dE, num_receptores, recebido1, recebido2, recebido3, pontosR1, pontosR2, pontosR3, enviado1, enviado2, enviado3, pontosE1,pontosE2, pontosE3 = top_3_data
    return total15dE, num_receptores, recebido1, recebido2, recebido3, pontosR1, pontosR2, pontosR3, enviado1, enviado2, enviado3, pontosE1,pontosE2, pontosE3


# Callback para renderizar a página com base na URL
@app.callback(
    Output('conteudo_principal', 'children'),
    [Input('url', 'pathname')]
)
def renderizar_pagina(pathname):
    if pathname == '/principios':
        return layout_principios() 
    elif pathname == '/rankings':
        return layout_rankings()
    elif pathname == '/formulario':
        return layout_formulario()


@app.callback(
    Output('form_content', 'children'),
    [Input('email_button', 'n_clicks')],
    [State('email_input', 'value')],
    prevent_initial_call=True
)
def verify_email(n_clicks, email):
    colaboradores_data
    if n_clicks:
        emails = [row['email'] for row in colaboradores_data]
        if email in emails:
            return create_form()
        else:
            return html.Div("Email não autorizado.", className="unauthorized_message")


@app.callback(
    Output('dimensoes_checklist', 'options'),
    [Input('principio_dropdown', 'value')]
)
def set_dimensoes_options(selected_principio):
    if selected_principio:
        return [{'label': dimensao, 'value': dimensao} for dimensao in principios_dimensoes[selected_principio]]
    return []


@app.callback(
    [
        Output('form_content', 'style'),
        Output('submission_status', 'children')
    ],
    [Input('submit_button', 'n_clicks')],
    [State('email_input', 'value'), State('colaborador_dropdown', 'value'), State('principio_dropdown', 'value'), State('dimensoes_checklist', 'value'), State('comentario_textarea', 'value')],
    prevent_initial_call=True
)
def submit_form(n_clicks, email_enviador, nome_receptor, principio, dimensoes, comentario):

    if n_clicks:
        email_receptor = encontrar_email_por_nome(nome_receptor, colaboradores_data)
        if email_receptor is None:
            return {'display': 'block'}, "Erro: Email do receptor não encontrado."

        # Concatenate dimensions into a string
        dimensoes_string = dimensoes
        data_atual = datetime.now()
        data_atual = data_atual.strftime('%Y/%m/%d')
        print(data_atual)
        resposta = {
            "created_at": data_atual,
            "enviador": email_enviador,
            "receptor": email_receptor,
            "princípio": principio,
            "dimensões": dimensoes_string,
            "comentário": comentario
        }
        response = supabase.table("reconhecimentos").insert(resposta).execute()

        return {'display': 'none'}, "Obrigado pelo envio!"

    return {'display': 'block'}, no_update


@cache.memoize(timeout=300)  # Armazena em cache por 5 minutos (300 segundos)
def get_cached_dfcolaboradores():
    dfcolaboradores = atualizar_colaboradores()
    return dfcolaboradores


def atualizar_cache():
    contagem(supabase)

scheduler.add_job(id='atualizar_cache_job', func=atualizar_cache,trigger='interval',minutes=5)


app.layout = layout_principal()



if __name__ == '__main__':
    get_cached_dfcolaboradores()
    server.run(debug=True, port=8050)
