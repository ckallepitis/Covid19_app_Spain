# Imports:
import pandas as pd
import numpy as np
import io
import requests

#=============================================================================#
#                                                                             #
#                         Data preparation - Spain                            #
#                                                                             #
#=============================================================================#

#=============================================================================#
# ========== Load Covid19 data ==========

def get_covid_data_Spain():

    url = 'https://github.com/datadista/datasets/raw/master/COVID%2019/'+\
          'ccaa_covid19_datos_sanidad_nueva_serie.csv'
    url_hospitals = 'https://github.com/datadista/datasets/raw/master/COVID%2019/'+\
                    'ccaa_ingresos_camas_convencionales_uci.csv'

    s = requests.get(url).content
    sh = requests.get(url_hospitals).content

    df_spain = pd.read_csv(io.StringIO(s.decode('utf-8')),error_bad_lines=False)
    df_spain = df_spain.drop(['cod_ine'],axis=1)
    df_hospitals = pd.read_csv(io.StringIO(sh.decode('utf-8')),error_bad_lines=False)
    df_hospitals = df_hospitals[['Fecha','CCAA','Altas COVID últimas 24 h']]
    df_spain = pd.merge(df_spain, df_hospitals, how='left', on=['Fecha', 'CCAA'])

    df_spain.columns = ['Date', 'Region', 'Cases', 'Hospitalised', 'ICU',
                        'Deaths', 'Recovered_24h']

    df_spain = df_spain.replace({'Region':
                                 {'Andalucía':'Andalusia',
                                  'Aragón':'Aragon',
                                  'Baleares':'Balearic Islands',
                                  'C. Valenciana':'Valencia',
                                  'Canarias':'Canary Islands',
                                  'Castilla La Mancha':'Castille-La Mancha',
                                  'Castilla y León':'Castille and Leon',
                                  'Cataluña':'Catalonia',
                                  'Navarra':'Navarre',
                                  'País Vasco':'Basque Country'}})

    df_spain = df_spain.query('Region != ["Ceuta","Melilla"]')
    df_spain.Date = pd.to_datetime(df_spain.Date, format = '%Y/%m/%d')

    df_spain['Daily_Cases'] = df_spain['Cases']
    df_spain['Daily_Deaths'] = df_spain['Deaths']
    df_spain.Daily_Cases[df_spain.Daily_Cases < 0] = 0
    df_spain.Daily_Deaths[df_spain.Daily_Deaths < 0] = 0
    df_spain['Cases'] = df_spain.groupby(['Region']).cumsum().Cases
    df_spain['Deaths'] = df_spain.groupby(['Region']).cumsum().Deaths

    df_spain['Daily Cases; 7-day rolling average'] = df_spain.groupby(['Region']).rolling(window=7)\
                                                                      .Daily_Cases.mean().reset_index()\
                                                                      .set_index('level_1').Daily_Cases
    df_spain['Daily Deaths; 7-day rolling average'] = df_spain.groupby(['Region']).rolling(window=7)\
                                                                     .Daily_Deaths.mean().reset_index()\
                                                                     .set_index('level_1').Daily_Deaths
    df_spain['Daily Cases; 7-day rolling average'] = df_spain['Daily Cases; 7-day rolling average']\
                                                       .fillna(0).astype(np.int64, errors='ignore')
    df_spain['Daily Deaths; 7-day rolling average'] = df_spain['Daily Deaths; 7-day rolling average']\
                                                         .fillna(0).astype(np.int64, errors='ignore')

    from elements import SPAIN_GEOLOCATIONS
    df_loc = pd.DataFrame(SPAIN_GEOLOCATIONS)

    df_spain = pd.merge(df_spain, df_loc, how='inner', on='Region')

    Spain = df_spain.groupby('Date').sum().reset_index()
    Spain['Region'] = 'Spain'
    df_spain = pd.concat([df_spain,Spain],axis=0)

    return df_spain

#=============================================================================#
# ========== Spain Map ==========

def get_geo_Spain_data(df_spain):

    df_geo_spain = df_spain[['Date','Region','Lat','Long','Cases','Deaths']][df_spain.Region != 'Spain']
    df_geo_spain = df_geo_spain.set_index(['Date', 'Region'])\
    .unstack().transform(lambda v: v.ffill()).transform(lambda v: v.ffill())\
    .transform(lambda v: v.bfill()).asfreq('D')\
    .stack().sort_index(level=1).reset_index()
    df_geo_spain = df_geo_spain.merge(df_spain[['Date','Region',
                             'Daily Cases; 7-day rolling average','Daily Deaths; 7-day rolling average']],
                   how='left', on=['Date','Region']).fillna(0)
    df_geo_spain.Date = df_geo_spain.Date.dt.strftime("%d %b %y").astype(str)
    df_geo_spain = df_geo_spain.rename(columns={'Daily Cases; 7-day rolling average':'Daily Cases',
                                                'Daily Deaths; 7-day rolling average':'Daily Deaths'})

    return df_geo_spain

#=============================================================================#
# ========== Sunburst chart ==========

def get_sunburst_data(df_spain):
    df_s = df_spain[df_spain.Region != 'Spain']
    df_sunburst = df_s[['Date', 'Region', 'Cases', 'Deaths', 'Hospitalised','ICU','Recovered_24h']]

    dd = df_s[['Date','Recovered_24h']].dropna().loc[df_s[['Date','Recovered_24h']].dropna().Date.idxmin()].Date
    d = df_s[df_s.Date == dd]
    d['Recovered'] = d.Cases - d.Deaths - d.Hospitalised - d.ICU
    df_sunburst.loc[(df_sunburst.Date == dd),'Recovered_24h'] = d.Recovered * 2
    df_sunburst['Recovered'] = df_sunburst.groupby(['Region']).cumsum().Recovered_24h

    df_sunburst = df_sunburst.drop('Recovered_24h',axis=1)
    df_sunburst['Active'] = df_sunburst['Cases'] - df_sunburst['Deaths'] - df_sunburst['Recovered']
    df_sunburst['Home_Isolation'] = df_sunburst['Active'] - df_sunburst['Hospitalised'] - df_sunburst['ICU']
    df_sunburst = df_sunburst.fillna(method='ffill')
    df_sunburst = df_sunburst.loc[df_sunburst.groupby('Region').Date.idxmax()]
    df_sunburst['Country'] = 'Spain'

    df_sunburst = df_sunburst.drop('Date',axis=1).melt(id_vars=['Country','Region'],
                                                       value_vars=['Deaths','Hospitalised','ICU','Home_Isolation',
                                                                   'Recovered'])
    df_sunburst['Cases'] = 'Active Cases'
    df_sunburst[(df_sunburst.variable == 'Deaths') | (df_sunburst.variable == 'Recovered')] = \
    df_sunburst.query("variable == ['Deaths','Recovered']").replace('Active Cases','Closed Cases')

    return df_sunburst

#=============================================================================#
#=============================================================================#
