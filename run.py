from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd

from components.data_prepare import get_data, get_column_vals, convert_month_to_date, filter_data
from components.constants import BASE_DATA_COLUMNS
from app import app

df_data = get_data()
payer_vals = get_column_vals(df_data, 'PAYER')
serv_cat_vals = get_column_vals(df_data, 'SERVICE_CATEGORY')
cl_spec_vals = get_column_vals(df_data, 'CLAIM_SPECIALTY')

app.layout = html.Div([
    html.Header([
        html.H2(
            'Test financial dashboard')
    ],
        style={'background-color': '#88a3d4'},
        className='row gs-header gs-text-header'
    ),

    html.Div(
        [
            html.H4('Base filters'),
            html.Div(
                [
                    html.H6('Select date range'),
                    dcc.DatePickerRange(
                        id='date_period_selector',
                        start_date_placeholder_text='Start Period',
                        end_date_placeholder_text='End Period',
                        calendar_orientation='vertical',
                        display_format='MMMM Y',
                        stay_open_on_select=True,
                        start_date=convert_month_to_date(df_data['MONTH'].min()),
                        end_date=convert_month_to_date(df_data['MONTH'].max()),
                    )

                ]
            ),
            html.Div(
                [
                    html.H6('Select PAYERS'),
                    dcc.Dropdown(
                        id='payer-dropdown',
                        options=[{'label': item, 'value': item} for item in payer_vals],
                        value=payer_vals[:3],
                        multi=True,
                    ),

                ],
            ),
            html.Div(
                [
                    html.H6('Select SERVICE CATEGORIES'),
                    dcc.Dropdown(
                        id='serv-cat-dropdown',
                        options=[{'label': item, 'value': item} for item in serv_cat_vals],
                        value=serv_cat_vals[:3],
                        multi=True
                    ),

                ],
            ),
            html.Div(
                [
                    html.H6('Select CLAIM SPECIALTY'),
                    dcc.Dropdown(
                        id='cl-spec-dropdown',
                        options=[{'label': item, 'value': item} for item in cl_spec_vals],
                        value=cl_spec_vals,
                        multi=True,
                        style={'overflow-y': 'scroll', 'height': '200px'}
                    ),
                ],
            ),
        ],
        style={'background-color': '#dbe0ec',
               'padding': '10px'},
    ),


    html.Div(
        [
            html.H6('PAID AMOUNT graph by month'),
            dcc.Graph(id='base-graph'),
        ]
    ),
    html.Div(
        className='row',
        children=[
            html.Div(
                [
                    html.H6('Data in table format'),
                    dash_table.DataTable(
                        id='table-paging-with-graph',
                        columns=[{'name': i, 'id': i} for i in BASE_DATA_COLUMNS],
                        data=df_data[BASE_DATA_COLUMNS].to_dict('records'),
                        page_size=20,
                        sort_mode='multi',
                        filter_action='native',
                        sort_action='native',
                    ),
                ],

                style={'margin': {'l': 10, 'r': 10, 't': 10, 'b': 50}}
            ),
            html.Div(
                id='table-paging-with-graph-container',
            )
        ]
    )

], style={'width': '500'})


@app.callback(Output('base-graph', 'figure'), [Input('payer-dropdown', 'value'),
                                               Input('serv-cat-dropdown', 'value'),
                                               Input('cl-spec-dropdown', 'value'),
                                               Input('date_period_selector', 'start_date'),
                                               Input('date_period_selector', 'end_date')])
def update_graph(payer_value, serv_cat_value, cl_spec_value, start_date, end_date):
    filtered_df = filter_data(df_data, payer_value, serv_cat_value, cl_spec_value, start_date, end_date)
    return {
        'data': [{
            'x': filtered_df.MONTH_DT,
            'y': filtered_df.PAID_AMOUNT
        }],
        'layout': {'margin': {'l': 40, 'r': 0, 't': 20, 'b': 30}}
    }


@app.callback(Output('table-paging-with-graph', 'data'), [Input('payer-dropdown', 'value'),
                                                          Input('serv-cat-dropdown', 'value'),
                                                          Input('cl-spec-dropdown', 'value'),
                                                          Input('date_period_selector', 'start_date'),
                                                          Input('date_period_selector', 'end_date')])
def update_table(payer_value, serv_cat_value, cl_spec_value, start_date, end_date):
    filtered_df = filter_data(df_data, payer_value, serv_cat_value, cl_spec_value, start_date, end_date)
    return filtered_df[BASE_DATA_COLUMNS].to_dict('records')


@app.callback(
    Output('table-paging-with-graph-container', 'children'),
    [Input('table-paging-with-graph', 'data')])
def update_table_graph(rows):
    dff = pd.DataFrame(rows)
    if not dff.empty:
        return html.Div(
            [
                html.H6('PAID AMOUNT bars group by'),
                html.Div([
                    dcc.Graph(
                        id=column,
                        figure={
                            'data': [
                                {
                                    'x': dff[column] if column in dff else [],
                                    'y': dff['PAID_AMOUNT'],
                                    'type': 'bar',
                                    'marker': {'color': '#0074D9'},
                                }
                            ],
                            'layout': {
                                'title': column,
                                'xaxis': {'automargin': True},
                                'yaxis': {'automargin': True},
                                'height': '400px',
                                'margin': {'t': '20px', 'l': '20px', 'r': '20px'},
                            },
                        },
                    )
                    for column in ['SERVICE_CATEGORY', 'PAYER']
                ])
            ]
        )


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
