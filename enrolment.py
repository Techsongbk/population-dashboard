#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

#######################
# Page configuration
st.set_page_config(
    page_title="Student Enrolment Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")


#######################
# Load data
df_reshaped = pd.read_csv('data/student.csv')


#######################
# Sidebar
with st.sidebar:
    st.title('🏂 Secondary Student Dashboard')
    
    year_list = list(df_reshaped.year.unique())[::-1]
    
    selected_year = st.selectbox('Select a year', year_list)
    df_selected_year = df_reshaped[df_reshaped.year == selected_year]
    df_selected_year_sorted = df_selected_year.sort_values(by="enrol", ascending=False)

    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)


#######################
# Plots

# Heatmap
def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
    heatmap = alt.Chart(input_df).mark_rect().encode(
            y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="Year", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
            x=alt.X(f'{input_x}:O', axis=alt.Axis(title="", titleFontSize=18, titlePadding=15, titleFontWeight=900)),
            color=alt.Color(f'max({input_color}):Q',
                             legend=None,
                             scale=alt.Scale(scheme=input_color_theme)),
            stroke=alt.value('black'),
            strokeWidth=alt.value(0.25),
        ).properties(width=900
        ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
        ) 
    # height=300
    return heatmap

# Choropleth map
def make_choropleth(input_df, input_id, input_column, input_color_theme):
    choropleth = px.choropleth(input_df, locations=input_id, color=input_column, locationmode="USA-states",
                               color_continuous_scale=input_color_theme,
                               range_color=(0, max(df_selected_year.population)),
                               scope="usa",
                               labels={'population':'Population'}
                              )
    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )
    return choropleth


# Donut chart
def make_donut(input_response, input_text, input_color):
  if input_color == 'blue':
      chart_color = ['#29b5e8', '#155F7A']
  if input_color == 'green':
      chart_color = ['#27AE60', '#12783D']
  if input_color == 'orange':
      chart_color = ['#F39C12', '#875A12']
  if input_color == 'red':
      chart_color = ['#E74C3C', '#781F16']
    
  source = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100-input_response, input_response]
  })
  source_bg = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100, 0]
  })
    
  plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          #domain=['A', 'B'],
                          domain=[input_text, ''],
                          # range=['#29b5e8', '#155F7A']),  # 31333F
                          range=chart_color),
                      legend=None),
  ).properties(width=130, height=130)
    
  text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{input_response} %'))
  plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          # domain=['A', 'B'],
                          domain=[input_text, ''],
                          range=chart_color),  # 31333F
                      legend=None),
  ).properties(width=130, height=130)
  return plot_bg + plot + text

# Convert population to text 
def format_number(num):
    if num > 1000000:
        if not num % 1000000:
            return f'{num // 1000000} M'
        return f'{round(num / 1000000, 1)} M'
    return f'{num // 1000} K'

# Calculation year-over-year population migrations
def calculate_enrolment_difference(input_df, input_year):
  selected_year_data = input_df[input_df['year'] == input_year].reset_index()
  previous_year_data = input_df[input_df['year'] == input_year - 1].reset_index()
  selected_year_data['enrolment_difference'] = selected_year_data.enrol.sub(previous_year_data.enrol, fill_value=0)
  return pd.concat([selected_year_data.level, selected_year_data.enrol, selected_year_data.enrolment_difference], axis=1).sort_values(by="enrolment_difference", ascending=False)


#######################
# Dashboard Main Panel
col = st.columns((1.5, 4.5, 2), gap='medium')

with col[0]:
    st.markdown('#### Increase/Decrease')

    df_enrolment_difference_sorted = calculate_enrolment_difference(df_reshaped, selected_year)

    if selected_year > 1980:
        first_level_name = df_enrolment_difference_sorted.level.iloc[0]
        first_level_enrolment = df_enrolment_difference_sorted.enrol.iloc[0]
        first_level_delta = df_enrolment_difference_sorted.enrolment_difference.iloc[0])
    else:
        first_level_name = '-'
        first_level_enrolment = '-'
        first_level_delta = ''
    st.metric(label=first_level_name, value=first_level_enrolment, delta=first_level_delta)

    if selected_year > 1980:
        last_level_name = df_enrolment_difference_sorted.level.iloc[-1]
        last_level_enrolment = df_enrolment_difference_sorted.enrol.iloc[-1]
        last_level_delta = df_enrolment_difference_sorted.enrolment_difference.iloc[-1]) 
    else:
        last_level_name = '-'
        last_level_enrolment = '-'
        last_level_delta = ''
    st.metric(label=last_level_name, value=last_level_population, delta=last_level_delta)

    
    st.markdown('#### Enrolment Delta of more than 5000')

    if selected_year > 1980:
        # Filter states with population difference > 50000
        # df_greater_50000 = df_population_difference_sorted[df_population_difference_sorted.population_difference_absolute > 50000]
        df_greater_5000 = df_enrolment_difference_sorted[df_enrolment_difference_sorted.enrolment_difference > 5000]
        df_less_5000 = df_enrolment_difference_sorted[df_enrolment_difference_sorted.enrolment_difference < -5000]
        
        # % of level with enrolment difference > 50000
        level_diff_greater = round((len(df_greater_5000)/df_enrolment_difference_sorted.level.nunique())*100)
        level_diff_less = round((len(df_less_5000)/df_enrolment_difference_sorted.level.nunique())*100)
        donut_chart_greater = make_donut(level_diff_greater, 'Increase Enrolment', 'green')
        donut_chart_less = make_donut(level_diff_less, 'Decrease Enrolment', 'red')
    else:
        level_diff_greater = 0
        level_diff_less = 0
        donut_chart_greater = make_donut(level_diff_greater, 'Increase Enrolment', 'green')
        donut_chart_less = make_donut(level_diff_less, 'Decrease Enrolment', 'red')

    level_diff_col = st.columns((0.2, 1, 0.2))
    with level_diff_col[1]:
        st.write('Increase Enrolment')
        st.altair_chart(donut_chart_greater)
        st.write('Decrease Enrolment')
        st.altair_chart(donut_chart_less)

with col[1]:
    st.markdown('#### Enrolment')
    
    # choropleth = make_choropleth(df_selected_year, 'states_code', 'population', selected_color_theme)
    # st.plotly_chart(choropleth, use_container_width=True)
    
    heatmap = make_heatmap(df_reshaped, 'year', 'level', 'enrol', selected_color_theme)
    st.altair_chart(heatmap, use_container_width=True)
    

with col[2]:
    st.markdown('#### Top Levels')

    st.dataframe(df_selected_year_sorted,
                 column_order=("level", "enrol"),
                 hide_index=True,
                 width=None,
                 column_config={
                    "level": st.column_config.TextColumn(
                        "level",
                    ),
                    "enrol": st.column_config.ProgressColumn(
                        "enrol",
                        format="%f",
                        min_value=0,
                        max_value=max(df_selected_year_sorted.enrol),
                     )}
                 )
    
    with st.expander('About', expanded=True):
        st.write('''
            - Data: Data.gov.sg.
            - :orange[**Increase/Decrease**]: Levels with high/low enrolment difference for selected year.
            - :orange[**Enrolment Delta of more than 5000**]: Percentage of levels with enrolment difference  > 5,000.
            ''')