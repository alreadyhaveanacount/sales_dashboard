############ IMPORTS ############

from dash import Dash, html, dcc, Input, Output, callback
import dash_ag_grid as dag
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

############ LOADING DATA ############

data = pd.read_csv("./data/sales_data_formatted.csv")
unique_years = data["YEAR"].unique()
unique_years.sort()
months_sorted = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]

############ HELPER FUNCTIONS ############

def build_AgGrid(id_, columns):
    """Creates a standardized AG Grid component"""

    return dag.AgGrid(id=id_, columnDefs=columns,
        defaultColDef={
            "flex": 1,
            "filter": True,
            "resizable": True,
            "sortable": True,
            "editable": False,
            "minWidth": 120
        },
        dashGridOptions={
            "pagination": True,
            "paginationPageSize": 20,
            "domLayout": "autoHeight",
            "animateRows": True,
            "rowSelection": "single",
            "enableCellTextSelection": True
        }
    )

def graph_years(year_list):
    """Generates the main sales trend graph"""

    filtered = [data[data["YEAR"] == year].groupby("MONTH")["Sales_Amount"].sum().reset_index() for year in year_list]
    
    new_fig = go.Figure()

    if len(filtered) == 1:
        new_fig = px.bar(filtered[0], x=filtered[0].MONTH, y="Sales_Amount", color="Sales_Amount", labels={"Sales_Amount": "Vendas totais", "MONTH": "Mês"}, custom_data=["Sales_Amount"])
    else:
        for i, df in enumerate(filtered):
            new_fig.add_trace(go.Scatter(x=df.MONTH, y=df.Sales_Amount, mode="lines+markers", name=f"Vendas de {year_list[i]}", custom_data=["Sales_Amount"]))
    
    new_fig.update_layout(
        template="plotly_white",
        title=f"Vendas de {min(year_list)} até {max(year_list)}" if len(year_list) > 1 else f"Vendas de {year_list[0]}",
        xaxis=dict(
            showgrid=False,
            tickfont=dict(family="Helvetica"),
            tickmode="array",
            tickvals=[i for i in range(1, 13)],
            ticktext=months_sorted
        ),
        yaxis=dict(showgrid=False)
    )

    new_fig.update_traces(hovertemplate="Mês: %{x}<br>Faturado: $ %{y:,.2f}")

    return new_fig

def rank_products(years, total_sum):
    """Ranks the products"""

    filtered_df = data[data["YEAR"].isin(years)].groupby("Product_ID")["Sales_Amount"].sum().reset_index()

    filtered_df["Product_Participation"] = round(filtered_df["Sales_Amount"] / total_sum, 4)
    filtered_df["Product_Ranking"] = filtered_df["Sales_Amount"].rank(ascending=False)

    filtered_df.sort_values(by="Product_Ranking", inplace=True)

    return filtered_df.to_dict(orient="records")

def rank_salesrep(years, total_sum):
    """Ranks the sales representatives and generates a pie graph"""

    filtered_df = data[data["YEAR"].isin(years)].groupby("Sales_Rep")["Sales_Amount"].sum().reset_index()

    filtered_df["SalesRep_Participation"] = round(filtered_df["Sales_Amount"] / total_sum, 4)
    filtered_df["SalesRep_Ranking"] = filtered_df["Sales_Amount"].rank(ascending=False)

    filtered_df.sort_values(by="SalesRep_Ranking", inplace=True)

    rep_graph = px.pie(filtered_df, values="Sales_Amount", names="Sales_Rep")
    rep_graph.update_traces(hovertemplate="Faturado: $ %{value:,.2f}<br>Vendedor: %{label}<br>Participação: %{percent}")

    return [filtered_df.to_dict(orient="records"), rep_graph]

############ SETTING UP DASH ############

app = Dash()

app.layout = html.Div(children=[
    dcc.Dropdown(unique_years, multi=True, placeholder="Filtrar por ano", id="chosen_years"),
    html.Br(),
    html.Div(children=[
        html.Div(children=[
            html.H4("Total De Vendas"),
            html.H3(f"Carregando", id="total_sales"),
            html.Hr(),
            dcc.Graph(id="sales_graph"),
        ], className="container", style={"width": "calc(50vw - 4px)"}),
        html.Div(children=[
            html.H4("Rank de produtos"),
            html.Hr(),
            build_AgGrid(id_="product_ranking", columns=[
                {"field": "Product_ID", "headerName": "ID do Produto"},
                {"field": "Sales_Amount", "headerName": "Total de vendas", "valueFormatter": {"function": "d3.format('($,.2f')(params.value)"}},
                {"field": "Product_Participation", "headerName": "Participação do Produto", "valueFormatter": {"function": "d3.format('.2%')(params.value)"}},
                {"field": "Product_Ranking", "headerName": "Rank do produto"}
            ])
        ], className="container", style={"width": "calc(50vw - 4px)", "marginLeft": "10px"})
    ], style={"display": "flex"}),
    html.Div(children=[
        html.Div(children=[
            html.H3("Métricas Principais", style={"textAlign": "center"}),
            html.Hr(),
            html.H4("Total de unidades vendidas:"),
            html.H3("Carregando", id="unidades_vendidas"),
            html.Hr(),
            html.H4("Valor médio por unidade:"),
            html.H3("Carregando", id="medio_unidade"),
            html.Hr(),
            html.H4("Desconto médio por unidade:"),
            html.H3("Carregando", id="desconto_unidade"),
            html.Hr(),
            html.H4("Categoria mais vendida:"),
            html.H3("Carregando", id="melhor_categoria"),
            html.Hr(),
            html.H4("Método de pagamento mais utilizado:"),
            html.H3("Carregando", id="pagamento_principal"),
            html.Hr(),
            html.H4("Canal de venda principal:"),
            html.H3("Carregando", id="canal_principal"),
            html.Hr(),
            html.H4("Região com mais faturamento:"),
            html.H3("Carregando", id="faturamento_regiao"),
            html.Hr(),
            html.H4("Distribuição do valor por pedido"),
            dcc.Graph(id="request_histogram")
        ], className="container", style={"width": "calc(60vw - 4px)"}),
        html.Div(children=[
            html.H4("Rank de vendedores"),
            html.Hr(),
            build_AgGrid(id_="salesrep_ranking", columns=[
                {"field": "Sales_Rep", "headerName": "Nome do vendedor"},
                {"field": "Sales_Amount", "headerName": "Vendas por vendedor", "valueFormatter": {"function": "d3.format('($,.2f')(params.value)"}},
                {"field": "SalesRep_Participation", "headerName": "Participação do vendedor", "valueFormatter": {"function": "d3.format('.2%')(params.value)"}},
                {"field": "SalesRep_Ranking", "headerName": "Rank do vendedor"}
            ]),
            html.Hr(),
            dcc.Graph(id="salesrep_graph")
        ], className="container", style={"width": "calc(40vw - 4px)", "marginLeft": "10px"})
    ], style={"display": "flex", "marginTop": "10px"})
])

############ CALLBACKS ############

@callback(
    [
        Output(component_id="sales_graph", component_property="figure"), Output(component_id="total_sales", component_property="children"),
        Output(component_id="product_ranking", component_property="rowData"), Output(component_id="unidades_vendidas", component_property="children"),
        Output(component_id="medio_unidade", component_property="children"), Output(component_id="desconto_unidade", component_property="children"),
        Output(component_id="melhor_categoria", component_property="children"), Output(component_id="pagamento_principal", component_property="children"),
        Output(component_id="canal_principal", component_property="children"), Output(component_id="faturamento_regiao", component_property="children"),
        Output(component_id="salesrep_ranking", component_property="rowData"), Output(component_id="salesrep_graph", component_property="figure"),
        Output(component_id="request_histogram", component_property="figure")
    ],
    Input(component_id="chosen_years", component_property="value")
)
def year_resume(year_list):
    if year_list is None or len(year_list) == 0: year_list = unique_years

    filtered_df = data[data["YEAR"].isin(year_list)]

    sales_int = filtered_df["Sales_Amount"].sum()
    unity_sold_int = filtered_df["Quantity_Sold"].sum()

    medio_unidade = f"$ {sales_int / unity_sold_int:,.2f}"
    desconto_unidade = f"{filtered_df["Discount"].mean():.2f}%"
    melhor_categoria = filtered_df.groupby("Product_Category")["Sales_Amount"].sum().idxmax()
    pagamento_principal = filtered_df["Payment_Method"].value_counts().idxmax()
    canal_principal = filtered_df["Sales_Channel"].value_counts().idxmax()
    faturamento_regiao = filtered_df.groupby("Region")["Sales_Amount"].sum().idxmax()

    rep_data = rank_salesrep(year_list, sales_int)

    ##### Making request histogram

    request_histogram = px.histogram(filtered_df["Sales_Amount"], labels={"value": "Faturamento por venda ($)", "Sales_Amount": "Faturamento"}, marginal="violin",
                                     title="Histograma de vendas", color_discrete_sequence=["#3366CC"])
    request_histogram.update_traces(hovertemplate="Faixa de faturamento: $ %{x}<br>Quantidade de transações: %{y}")

    request_histogram.update_layout(
        yaxis_title="Quantidade de vendas",
        template="plotly_white",
        xaxis=dict(
            showgrid=False,
            tickfont=dict(family="Helvetica")
        ),
        yaxis=dict(showgrid=False),
        showlegend=False
    )

    request_histogram.add_vline(
        x=filtered_df["Sales_Amount"].mean(), 
        line_dash="dot",
        annotation_text=f"Média: $ {filtered_df['Sales_Amount'].mean():.2f}",
        annotation_position="top"
    )

    return graph_years(year_list), f"$ {sales_int:,.2f}", rank_products(year_list, sales_int), f"{unity_sold_int:,}", medio_unidade, desconto_unidade, melhor_categoria, pagamento_principal, canal_principal, faturamento_regiao, rep_data[0], rep_data[1], request_histogram


############ RUNNING DASHBOARD ############

if __name__ == '__main__':
    app.run(debug=True)