import pandas as pd
import streamlit as st
import plotly_express as px
import base64
import altair as alt
from io import StringIO, BytesIO

with st.echo(code_location='below'):
    def read_file(data_url):
        return pd.read_csv(data_url)
    ####DOWNLOAD EXCEL AND PLOT FUNCTIONS
    ### Adapted FROM: (https://discuss.streamlit.io/t/how-to-add-a-download-excel-csv-function-to-a-button/4474/5)
    def generate_excel_download_link(df):
        towrite = BytesIO()
        df.to_excel(towrite, encoding="utf-8", index=False, header=True)  # write to BytesIO buffer
        towrite.seek(0)  # reset pointer
        b64 = base64.b64encode(towrite.read()).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="data_download.xlsx">Download Excel File of the graph</a>'
        return st.markdown(href, unsafe_allow_html=True)
    ### END FROM
    ### Adapted FROM: (https://discuss.streamlit.io/t/download-plotly-plot-as-html/4426/2)
    def generate_html_download_link(fig):
        towrite = StringIO()
        fig.write_html(towrite, include_plotlyjs="cdn")
        towrite = BytesIO(towrite.getvalue().encode())
        b64 = base64.b64encode(towrite.read()).decode()
        href = f'<a href="data:text/html;charset=utf-8;base64, {b64}" download="plot.html">Download Plot of the graph</a>'
        return st.markdown(href, unsafe_allow_html=True)
    ### END FROM
    ####END DOWNLOAD

    df = read_file("suicide.csv")
    st.set_page_config(page_title='Suicide country info data visualization')
    st.title('Suicide country info data visualization')
    st.subheader('My initial dataset:')
    st.write(df)
    df_year_coun = df.groupby(by = ['country', 'year'], as_index=False)['suicides_no'].sum()
    countries = list(df_year_coun['country'].unique())
    """
    This database displays information on suicides committed in different countries by year, information on gdp, and segmentation of suicides.
    The first, and most important thing I would like to visualize, is the segmentation of suicide rates by various parameters. 
    This gives us an understanding of which groups of people are more susceptible to suicide and how exactly they are segmented. 
    Below you can visually compare the distribution of suicides by parameters such as age, gender, and generational affiliation.
    """
    ## Here tablet with different countries and years: st.write(df_year_coun)

    ##FIRST GRAPH
    groupby_column = st.selectbox(
        'Please, choose the category about which you will get analysis',
        ('sex', 'age', 'generation')
    )

    # GROUP DATAFRAME 1
    output_columns = ['suicides_no', 'suicides/100k pop']
    df_grouped = df.groupby(by=[groupby_column], as_index = False)[output_columns].sum()
    df_sum_pop = df.groupby(by=[groupby_column], as_index = False)['population'].sum()
    df_grouped['suicides/100k pop'] = df_grouped['suicides_no']/df_sum_pop['population']*100000

    #GROUPED DATAFRAME: st.dataframe(df_grouped)

    #PLOT DATAFRAME 1
    #FROM https://www.youtube.com/watch?v=ZDffoP6gjxc&t=116s
    fig = px.bar(
        df_grouped,
        x=groupby_column,
        y="suicides_no",
        labels={'suicides_no': 'Number of suicides',
                                    'suicides/100k pop': 'Number of suicides per 100k'},
        color='suicides/100k pop',
        color_continuous_scale=['green','yellow','red'],
        template='presentation',
        title=f'<b> Suicides number by {groupby_column}</b>'
    )
    st.plotly_chart(fig)
    #END FROM
    st.caption("You can download ALL these graphs and excel tablets on the bottom of the website.",
               unsafe_allow_html=False)
    ##END FIRST GRAPH

    """
    The next step was to look for a correlation between per capita gdp and suicide rates. 
    To do this, I discounted both indicators, so that I could get an overall dataset. 
    The best visual role was played by the scatter plot. I also plotted a line that would show the regression and relationship between the two indicators. 
    However, I was very surprised when I got the result. GDP and suicide rates were loosely related. 
    Apparently because the countries have different religions and cultures, which makes the relationship imperceptible.
    """

    ##SECOND GDP GRAPH
    df_gdp = df.groupby(by=['country'], as_index = False)['suicides/100k pop'].mean()
    df_sum_gdp = df.groupby(by=['country'], as_index = False)['gdp_per_capita ($)'].mean()
    df_gdp['gdp_per_capita ($)']=df_sum_gdp['gdp_per_capita ($)']

    #GDP DATAFRAME: st.dataframe(df_gdp)

    #PLOT
    df_gdp2 = df_gdp
    c = alt.Chart(df_gdp2, title='Scattered map of suicide rate and GDP with average line').mark_circle().encode(
        x=alt.X('gdp_per_capita ($)', title='GDP per capita'),
        y=alt.Y('suicides/100k pop', title='Number of suicides per 100k'),
        tooltip=['gdp_per_capita ($)', 'suicides/100k pop', 'country'],
        color="country"
    ).properties(title='Scattered map of suicide rate and GDP with average line')
    line = (
        alt.Chart(
            df_gdp2
        )
        .transform_loess('gdp_per_capita ($)', 'suicides/100k pop')
        .mark_line()
        .encode(x=alt.X('gdp_per_capita ($)'), y=alt.Y('suicides/100k pop'))
    )
    st.altair_chart(c+line, use_container_width=True)
    ##END SECOND GRAPH

    """
    Next, I decided to construct a necessary and probably most important graph - the number of suicides in countries over time. 
    It can give an insight into the fact that at certain points significant events occurred for a country and can help identify correlations. 
    """
    ##THIRD GRAPH
    #CHOSE OF COUNTRY FOR 3 GRAPH
    groupby_column1 = st.selectbox('Select country for analysis',
        countries, index = 75
    )
    df_year_coun_ch=df_year_coun[df_year_coun['country']==groupby_column1]
    #INTERMEDIATE DATA: st.write(df_year_coun_ch)

    #PLOT
    fig_product_sales = px.bar(
        df_year_coun_ch,
        x="year",
        y="suicides_no",
        orientation="v",
        title=f'<b>Suicides in {groupby_column1} by year</b>',
        color='year',
        labels={'suicides_no': 'Number of suicides',
                                    'year': 'Year'},
        template="plotly_white",
        facet_row_spacing=0.06,
        width = 800
    )
    st.plotly_chart(fig_product_sales)
    ## STOP

    """
    I also considered it important to show the countries in which the number of suicides was the highest in 1985-2016, 
    this information also provides an opportunity to analyze what was happening in certain countries at that time.
    """
    ##TOP 15 COUNTRIES FOURTH GRAPH 4
    df_sum = df.groupby(by=["country"], as_index = False)["suicides_no"].sum()
    df_sum = df_sum.sort_values(by='suicides_no', ascending=False)[:15]

    #SUM DATAFRAME: st.write(df_sum)

    #PLOT
    chart = (
        alt.Chart(
            df_sum,
            title="Number of suicides in 15 top countries from 1985 to 2016",
        )
        .mark_bar()
        .encode(
            x=alt.X("suicides_no", title="Suicides in 15 top countries"),
            y=alt.Y(
                "country",
                sort=alt.EncodingSortField(field="suicides_no", order="descending"),
                title="",
            ),
            color='country',
            tooltip=["country", "suicides_no"],
        )
    )
    st.altair_chart(chart, use_container_width=True)
    ##STOP

    ###MAP 5

    #COORDS DATA GET
    df_coord = read_file("coordinates.csv")
    df_gdp.replace({'country':{'Russian Federation':'Russia'}}, inplace=True)
    df_gdp.replace({'country':{'Republic of Korea':'South Korea'}}, inplace=True)
    df_gdp = df_gdp.merge(df_coord, on='country', how='left')
    st.subheader('My second dataset of coordinates of countries:')
    st.write(df_coord)
    df_gdp = df_gdp[['country', 'latitude', 'longitude', 'suicides/100k pop']]
    df_gdp = df_gdp.rename(columns={'latitude': 'lat', 'longitude': 'lon', 'suicides/100k pop': 'suicides_per_100k_pop'})
    listofnum = df_gdp.suicides_per_100k_pop.values.tolist()
    #FINAL COORD DATA: st.write(df_gdp)
    """
    It was very difficult to build this map. For this I had to adapt another database with coordinates to mine. 
    This map visually shows the countries and their suicide rates. 
    Great for those who need to get information quickly, qualitatively and clearly. 
    The size and color of the dots corresponds to the suicide rate. You can also hover over them and see the information.
    """
    ##PLOT
    fig1 = px.scatter_mapbox(df_gdp, lat='lat', lon='lon', zoom=0,
                            color="suicides_per_100k_pop", size="suicides_per_100k_pop",
                            hover_name='country',
                            labels={'country': 'Country', 'lon': 'Longitude', 'lat': 'Latitude',
                                    'suicides_per_100k_pop': 'Number of suicides per 100k'},
                            color_continuous_scale=px.colors.cyclical.IceFire,
                            title='Number of suicides per 100k in different countries average from 1985',
                            mapbox_style='open-street-map')
    st.plotly_chart(fig1)
    ###END MAP
    df_gdp3 = df_gdp
    """
    For the final graph, I decided to leave the distribution of suicides by country, which provides as much information as possible. 
    First, it is a great visual representation of the sample. 
    Second, it gives you the data you need for analysis without having to open a table. Such as median, maximum, minimum, lower and upper mean q1 q2.
    """
    ###FINAL GRAPH 6
    fig2 = px.violin(df_gdp3, y="suicides_per_100k_pop", box=True,
                    labels={'country': 'Country', 'lon': 'Longitude', 'lat': 'Latitude',
                                    'suicides_per_100k_pop': 'Number of suicides per 100k'},
                    points='all',
                    title="Violin plot, showing distribution of suicide rate among countries ",
                   )
    st.plotly_chart(fig2)
    """PS: You can observe that median number of suicides per 100k of population is 10.46 among countries
     and it's close to reality."""
    ###END
    #BOTTOM

    st.subheader('Downloads:')
    """1 GRAPH"""
    generate_excel_download_link(df_grouped)
    generate_html_download_link(fig)
    """2 GRAPH"""
    generate_excel_download_link(df_gdp2)
    """3 GRAPH"""
    generate_excel_download_link(df_year_coun_ch)
    generate_html_download_link(fig_product_sales)
    """4 GRAPH"""
    generate_excel_download_link(df_sum)
    """5 MAP"""
    generate_excel_download_link(df_gdp)
    generate_html_download_link(fig1)
    """6 GRAPH"""
    generate_excel_download_link(df_gdp3)
    generate_html_download_link(fig2)


    """Sources:
    1) https://plotly.com/
    2) My dataframe: https://www.kaggle.com/datasets/russellyates88/suicide-rates-overview-1985-to-2016
    3) https://streamlit.io/gallery
    4) https://altair-viz.github.io/
    """










    
