from ast import literal_eval
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import textwrap as tr
from utilities.fixed_params import page_setup
from utilities.colours import linear_gradient

# Set page configuration
page_setup('wide')

# Need to change to globally set school depending on login
school = st.selectbox(
    'School', ['School A', 'School B', 'School C', 'School D',
               'School E', 'School F', 'School G'])

# Import the scores and the proportion each response
df_scores = pd.read_csv('data/survey_data/aggregate_scores_rag.csv')
df_prop = pd.read_csv('data/survey_data/aggregate_responses.csv')

###############################################################################
# Breakdown of question responses chart
# Basic example
# TO DO: how deal with multiple questions with different responses categories

# Create selectbox with available topics (excluding demographic)
topics = df_prop['group'].drop_duplicates().to_list()
topics.remove('demographic')
chosen_variable = st.sidebar.radio('Topic', topics)

# Title and header
st.title(chosen_variable)
st.header('Breakdown of responses for your school')

# Filter to chosen variable and school
chosen = df_prop[
    (df_prop['group'] == chosen_variable) &
    (df_prop['school_lab'] == school) &
    (df_prop['year_group_lab'] == 'All') &
    (df_prop['gender_lab'] == 'All') &
    (df_prop['fsm_lab'] == 'All') &
    (df_prop['sen_lab'] == 'All')]

# Extract the lists with results stored in the dataframe
# e.g. ['Yes', 'No'], [20, 80], [2, 8] in the original data will become
# seperate columns with [Yes, 20, 2] and [No, 80, 8]
df_list = []
for index, row in chosen.iterrows():
    df = pd.DataFrame(zip(literal_eval(row['cat'].replace('nan', 'None')),
                          literal_eval(row['cat_lab']),
                          literal_eval(row['percentage']),
                          literal_eval(row['count'])),
                      columns=['cat', 'cat_lab', 'percentage', 'count'])
    # Replace NaN with max number so stays at end of sequence
    df['cat'] = df['cat'].fillna(df['cat'].max()+1)
    # Add measure label (don't need to extract as string rather than list in df)
    df['measure_lab'] = row['measure_lab']
    df_list.append(df)
chosen_result = pd.concat(df_list)

# Get colour spectrum between the provided colours, for all except one category
# Use 'cat_lab' rather than 'cat' as sometimes cat is 0-indexed or 1-indexed
start_colour = '#2A52BE'
end_colour = '#D4DCF2'
n_cat = chosen_result['cat_lab'].drop_duplicates().size
colours = linear_gradient(start_colour, end_colour, n_cat-1)['hex']
# Add final colour of grey for the last category, which will be "missing"
colours += ['#DDDDDD']

# Convert labels to wrapped lines, with max length and new lines \n
def wrap_text(string, width):
    '''
    Wrap the provided string to the specified width, producing a single string
    with new lines indicated by '<br>'. If string length is less than the
    specified width, add blank space to the start of the string (so it will
    still occupy the same amount of space on the chart)
    '''
    wrap = '<br>'.join(tr.wrap(string, width=width))
    if len(wrap) < width:
        blank = width - len(wrap)
        wrap=(' '*blank) + wrap
    return(wrap)


chosen_result['measure_lab_wrap'] = chosen_result['measure_lab'].apply(
    lambda x: wrap_text(x, 50))

# Create plot
fig = px.bar(
    chosen_result, x='percentage', y='measure_lab_wrap', color='cat_lab',
    text_auto=True, hover_data=['count', 'measure_lab'], orientation='h',
    color_discrete_sequence=colours)

# Add percent sign to the numbers labelling the bars
fig.for_each_trace(lambda t: t.update(texttemplate = t.texttemplate + ' %'))

# Remove x and y axes as they are redundant
fig.update_layout(yaxis_title=None, xaxis_title='Percentage')

# Find number of variables being plot, then set height of figure based on that
# so the bars appear to be fairly consistent height between different charts
n_var = chosen_result['measure_lab'].drop_duplicates().size
height = 100 * n_var
if height <= 200:
    height += 100
elif height >=700:
    height -= 100
fig.update_layout(autosize=True, height=height)

# Make legend horizontal and center on 0.5, and lower on y so not overlapping
# with the title
fig.update_layout(legend=dict(
    orientation='h',
    x=0.5,
    xanchor='center',
    y=-0.15))

# Disable zooming and panning
fig.layout.xaxis.fixedrange = True
fig.layout.yaxis.fixedrange = True

# Show plot
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

###############################################################################
# Initial basic example of doing the comparator chart between schools...

# Set up columns
cols = st.columns(2)

# Create dataframe based on chosen variable
between_schools = df_scores[
    (df_scores['variable'].str.replace('_score', '') == chosen_variable) &
    (df_scores['year_group_lab'] == 'All') &
    (df_scores['gender_lab'] == 'All') &
    (df_scores['fsm_lab'] == 'All') &
    (df_scores['sen_lab'] == 'All')]

# Add box with RAG rating
devon_rag = between_schools.loc[between_schools['school_lab'] == school, 'rag'].to_list()[0]
with cols[0]:
    st.header('Comparison to other schools in Northern Devon')
    if devon_rag == 'below':
        st.error('↓ Below average')
    elif devon_rag == 'average':
        st.warning('~ Average')
    elif devon_rag == 'above':
        st.success('↑ Above average')

# Add colour for bar based on school
between_schools['colour'] = np.where(
    between_schools['school_lab']==school, '#004E7C', '#6699CC')

# Plot the results
fig = px.bar(between_schools, x='school_lab', y='mean',
             color='colour', color_discrete_map='identity')

# Reorder x axis so in ascending order
fig.update_layout(xaxis={'categoryorder':'total ascending'})

# Set y axis limits so the first and last bars of the chart a consistent height
# between different plots - find 15% of range and adj min and max by that
min = between_schools['mean'].min()
max = between_schools['mean'].max()
adj_axis = (max - min)*0.15
ymin = min - adj_axis
ymax = max + adj_axis
fig.update_layout(yaxis_range=[ymin, ymax])

# Extract lower and upper rag boundaries amd shade the RAG areas
# (Colours used were matched to those from the summary page)
lower = between_schools['lower'].to_list()[0]
upper = between_schools['upper'].to_list()[0]
fig.add_hrect(y0=ymin, y1=lower, fillcolor='#F8DCDC', layer='below',
              line={'color': '#9A505B'}, line_width=0.5,
              annotation_text='Below average', annotation_position='top left')
fig.add_hrect(y0=lower, y1=upper, fillcolor='#F8ECD4', layer='below',
              line={'color': '#B3852A'}, line_width=0.5,
              annotation_text='Average', annotation_position='top left')
fig.add_hrect(y0=upper, y1=ymax, fillcolor='#E0ECDC', layer='below',
              line={'color': '#3A8461'}, line_width=0.5,
              annotation_text='Above average', annotation_position='top left')

# Prevent zooming and panning, remove grid, and hide plotly toolbar
fig.layout.xaxis.fixedrange = True
fig.layout.yaxis.fixedrange = True
fig.update_yaxes(showgrid=False)

# Show figure within column
with cols[1]:
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})