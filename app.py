import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
from dash import Dash
from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

markdown_text = '''
The gender wage gap is the average difference between the income for working men and women. Due to legal, social, and economic factors, women are considered to be paid less than men. According to [Wikipedia](https://en.wikipedia.org/wiki/Gender_pay_gap), "in the United States, for example, the non-adjusted average female's annual salary is 79% of the average male salary, compared to 95% for the adjusted average salary." An article from the [Economic Policy Institute](https://www.epi.org/publication/what-is-the-gender-pay-gap-and-is-it-real/) points out that the gender wage gap is often made a political issue, despite the fact that data supports the claim that a gender wage gap exists. This source also points out that in recent years the gap has been closing, and that data about the gender wage gap should be used carefully with clear goals in mind

The GSS is the "General Social Survey" which collects data on current American society in order to monitor trends in attitudes and behaviors. The General Social Survey is often conducted through face-to-face interviews, and the GSS's goal is to make high-quality data easily accessible to anyone who wishes to use it.
'''

gss_bar = gss_clean.groupby('sex', sort=False).agg({'income':'mean',
                                                    'job_prestige':'mean',
                                                    'socioeconomic_index':'mean', 
                                                    'education':'mean'})



gss_bar = round(gss_bar, 2)

gss_bar = gss_bar.reset_index().rename({'income':'Income',
                                   'job_prestige':'Job Prestige',
                                   'socioeconomic_index':'Socioeconomic Index',
                                   'education':'Years of Education',}, axis=1)

table = ff.create_table(gss_bar)

breadwinner = gss_clean.groupby(['sex', 'male_breadwinner']).size().reset_index(name='counts')

fig_bar = px.bar(breadwinner, x='male_breadwinner', y='counts', color='sex', 
                 labels = {'male_breadwinner': 'Response Level', 'counts': 'Count'})

fig_scatter = px.scatter(gss_clean, x='job_prestige', y='income', trendline='ols', 
                 color='sex',
                 height=600, width=600,
                 labels={'job_prestige':'Occupational Prestige', 'income':'Income'}, 
                 hover_data=['education', 'socioeconomic_index'])

fig_scatter.update(layout=dict(title=dict(x=0.5)))

fig_income = px.box(gss_clean, x='sex', y='income', color='sex', 
                    labels={'income':'Income', 'sex':''})
fig_income.update_layout(showlegend=False)

fig_prestige = px.box(gss_clean, x='sex', y='job_prestige', color='sex', 
                      labels={'job_prestige':'Job Prestige', 'sex':''})
fig_prestige.update_layout(showlegend=False)

# create a new dataframe
gss_df = gss_clean[['income', 'sex', 'job_prestige']]

# create new feature for prestige categories
# pd.cut docs on making equally sized bins: 
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.cut.html

gss_df['prestige_level'] = pd.cut(gss_clean['job_prestige'], 6, 
                                       labels=["level 1", "level 2", "level 3",
                                               "level 4", "level 5", "level 6"])

gss_df = gss_df.dropna()

fig6 = px.box(gss_df, x='sex', y='income', color='sex', 
             labels={'job_prestige':'Job Prestige', 'sex':''}, 
             facet_col='prestige_level', facet_col_wrap=2,
             category_orders = {'prestige_level':["level 1", "level 2", "level 3",
                                               "level 4", "level 5", "level 6"]},
             color_discrete_map = {'male':'blue', 'female':'red'})
fig6.for_each_annotation(lambda a: a.update(text=a.text.replace("prestige_level=", "")))


app = JupyterDash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': '#111111',
    'text': '#7FDBFF', 
    'red': '#9c1f16'
}


app.layout = html.Div(
    [
        html.Div([html.H1("Understanding the Gender Wage Gap")], style = {'padding':'20px 30px 20px 30px',
                                                                          'borderColor':'#9c1f16',
                                                                          'borderLeftStyle': 'solid', 
                                                                          'borderWidth':'30px', 
                                                                          'borderTopLeftRadius':'15px'}),
                
        html.Div([
            
            html.H3("Wage Gap Overview"),

            dcc.Markdown(children = markdown_text)], style = {'backgroundColor':'#9c1f16', 
                                                                    'color':'white', 
                                                                    'padding':'30px', 
                                                                    'margin':'30px'}),
        
        html.Div([
            
            html.H5("Comparing Mean Income, Occupational Prestige, and Socioeconomic Index"),
        
            dcc.Graph(figure=table)], style = {'margin':'30px', 
                                               'paddingTop':'30px', 
                                               'textAlign':'center'}), 
        

        html.Div([
            
            html.H5("Agreement Level About Male Breadwinner Question"),
        
            dcc.Graph(figure=fig_bar)], style={'margin':'30px', 
                                               'paddingTop':'30px', 
                                               'textAlign':'center'}),
        

        html.Div([        
            
            html.H5("Income by Occupational Prestige"),
        
            dcc.Graph(figure=fig_scatter)], style={'margin':'30px', 
                                                  'paddingTop':'30px', 
                                                  'textAlign':'center'}), 

        
        html.Div([

             html.Div([

                html.H5("Income Distribution"),

                dcc.Graph(figure=fig_income)

            ], style = {'width':'48%', 
                        'float':'left'}),


            html.Div([

                html.H5("Job Prestige Distribution"),

                dcc.Graph(figure=fig_prestige)

            ], style = {'width':'48%',
                        'float':'right'})
            
            
        ], style = {'margin':'30px', 
                  'paddingTop':'30px', 
                   'textAlign':'center'}),
        

        
        html.Div([
            
            html.H5("Income Distribution by Prestige Level"),
        
            dcc.Graph(figure=fig6)], style={'margin':'30px', 
                                            'paddingTop':'30px', 
                                            'textAlign':'center'})
        

        
    ], style = {
        'backgroundColor':'white', 
        'margin': '50px 200px 50px 200px', 
        'boxShadow': '5px 10px 18px #888888',
        'borderRadius':'15px'
    }
)

if __name__ == '__main__':
    app.run_server(debug=True)
