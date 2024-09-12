import faicons as fa
import plotly.express as px
from shinywidgets import render_plotly, render_widget, output_widget

from shiny import reactive, render, req
from shiny.express import input, ui

import pandas as pd
import os

root_path = ''
data_path = os.path.join(root_path, "data")

data = pd.read_csv(os.path.join(data_path, 'parsed_students_data.csv'))
response_data = pd.read_csv(os.path.join(data_path, 'parsed_response_data.csv'))

unique_schools = list(set(data['school'].tolist()))
unique_schools.sort()

unique_subjects = list(set(data['subject'].tolist()))
unique_subjects.sort()

possible_scores = ['50', '49', '48', '47', '46', '45', '44', '43', '42', '41', '40']

unique_students = list(set(data['name'].tolist()))
unique_students.sort()

ICONS = {
    "school": fa.icon_svg("school"),
}

ui.page_opts(title='VCE Statistics Tool', fillable=True)

with ui.nav_panel('Welcome'):
    with ui.layout_columns():
        with ui.card():
            @render.text
            def intro_text():
                return 'Welcome to my VCE Statistics Tool! Select a visualization from the dropdown below to learn more about what it represents.'
            ui.input_selectize(
                'welcome_select', 'Select a type of visualization.',
                ['Popular subjects', 'No. of students by score (by subject)', 'Rank schools by subject', 'Student results search', 'Pie charts for response data', 'Linear bar charts for response data'],
                multiple=False
            )
            @render.text
            def vcaa_text():
                return 'Data sourced from the VCAA website in August 2024 at https://www.vcaa.vic.edu.au/students/support/Pages/Index.aspx'
        with ui.card():
            @render.text
            def select_text():
                choice = input.welcome_select()
                if choice == 'Popular subjects':
                    return 'You can filter by school and subject. It shows which subjects had the most students getting scores over 40, and you can compare different schools by clicking \'show colors\'. (Mind that if you have a lot of schools or all of them selected, showing colors will be very slow.)'
                elif choice == 'No. of students by score (by subject)':
                    return 'You can filter by school (multiple select), subject (multiple select) and score (single select). It shows the number of students getting that specific score in the subjects you select.'
                elif choice == 'Rank schools by subject':
                    return 'You can select schools (multiple) and select a single subject. The graph will show which schools had the most students getting scores over 40 in that specific subject. It will also show you, down the bottom, the names and scores of students achieving over 40 in the top school.'
                elif choice == 'Student results search':
                    return 'Select a single student - this will show you which school they\'re from, as well as any scores over 40 they achieved for any subject.'
                elif choice == 'Pie charts for response data':
                    return 'This data is sourced from a group of students, teachers and parents who voluntarily provided information for this statistics tool. Select either All, Parent, Student or Teacher to view results for individual groups.'
                elif choice == 'Linear bar charts for response data':
                    return 'This data is sourced from a group of students, teachers and parents who voluntarily provided information for this statistics tool. There is no input for these charts - simply click on any group in the key to show or hide it, and mouseover any bar to view individual results.'
                else:
                    return 'That\'s not a valid option. How did you even make this appear!?'

with ui.nav_panel('Popular subjects'):
    with ui.layout_columns():
        with ui.card():
            ui.input_selectize(
                'school_popular', 'Select school',
                ['All'] + unique_schools,
                multiple=True
            )
            ui.input_selectize(
                'subject_popular', 'Select subject to filter',
                ['All'] + unique_subjects,
                multiple=True
            )
            ui.input_slider('top_popular', 'Show top x', 5, len(unique_subjects), 10)
            ui.input_checkbox('show_colors_popular', 'Show colors?', False)
        with ui.card():
            @render_plotly
            def popular_subjects():
                import plotly.express as px

                schools = input.school_popular()
                subjects = input.subject_popular()

                specific = pd.DataFrame(columns=['subject', 'student_count'])

                if 'All' in schools: schools = unique_schools
                if 'All' in subjects: subjects = unique_subjects

                for subject in subjects:
                    temp_data = data.loc[(data['subject'] == subject) & (data['school'].isin(schools))]
                    count = temp_data.shape[0]

                    specific.loc[len(specific)] = [subject, count]

                specific = specific.sort_values('student_count', ascending=False)

                if input.show_colors_popular() == False:
                    plot_specific = specific.head(input.top_popular())

                    return px.bar(plot_specific, x='student_count', y='subject').update_yaxes(categoryorder='total ascending')
                else:
                    top_subjects_df = specific.head(input.top_popular())
                    top_subjects = list(set(top_subjects_df['subject'].tolist()))

                    plot_specific = pd.DataFrame(columns=['subject', 'student_count', 'school'])

                    for subject in top_subjects:
                        for school in schools:
                            temp_data = data.loc[(data['subject'] == subject) & (data['school'] == school)]
                            count = temp_data.shape[0]

                            plot_specific.loc[len(plot_specific)] = [subject, count, school]

                    return px.bar(plot_specific, x='student_count', y='subject', color='school').update_yaxes(categoryorder='total ascending').update_layout(showlegend=False)


with ui.nav_panel('No. of students by score (by subject)'):
    with ui.layout_columns():
        with ui.card():
            ui.input_selectize(
                'school_students_by_score', 'Select school',
                ['All'] + unique_schools,
                multiple=True
            )
            ui.input_selectize(
                'subject_students_by_score', 'Select subject to filter',
                ['All'] + unique_subjects,
                multiple=True
            )
            ui.input_selectize(
                'score_students_by_score', 'Select score to filter',
                possible_scores,
                multiple=False
            )
            ui.input_slider('top_students_by_score', 'Show top x', 5, len(unique_subjects), 10)
        with ui.card():
            @render_plotly
            def students_by_score():
                import plotly.express as px

                schools = input.school_students_by_score()
                subjects = input.subject_students_by_score()
                score = str(input.score_students_by_score())

                specific = pd.DataFrame(columns=['subject', 'student_count'])

                if 'All' in schools: schools = unique_schools
                if 'All' in subjects: subjects = unique_subjects

                for subject in subjects:
                    temp_data = data.loc[((data['scores'] == int(score)) & (data['subject'] == subject)) & (data['school'].isin(schools))]
                    count = temp_data.shape[0]

                    specific.loc[len(specific)] = [subject, count]

                specific = specific.sort_values('student_count', ascending=False)

                plot_specific = specific.head(input.top_students_by_score())

                return px.bar(plot_specific, x='student_count', y='subject').update_yaxes(categoryorder='total ascending')
            
with ui.nav_panel('Rank schools by subject'):
    with ui.layout_columns():
        with ui.card():
            ui.input_selectize(
                'school_rank_school_by_subject', 'Select school',
                ['All'] + unique_schools,
                multiple=True
            )
            ui.input_selectize(
                'subject_rank_school_by_subject', 'Select subject to filter',
                unique_subjects,
                multiple=False
            )
            ui.input_slider('top_rank_school_by_subject', 'Show top x', 5, len(unique_schools), 10)

            with ui.value_box(showcase=output_widget("names_line"), showcase_layout="bottom"):
                "Top school"
                @render.express
                def school_showcase_box():
                    subject = input.subject_rank_school_by_subject()
                    schools = input.school_rank_school_by_subject()

                    if 'All' in schools: schools = unique_schools

                    top_school = ''
                    top_count = 0
                    names_and_scores = pd.DataFrame(columns=['name', 'score'])
                    
                    for school in schools:
                        temp_data = data.loc[(data['subject'] == subject) & (data['school'] == school)]
                        count = temp_data.shape[0]

                        temp_names_and_scores = pd.DataFrame(columns=['name', 'score'])
                        for index, row in temp_data.iterrows():
                            data_name, data_school, data_subject, data_score = row[:4]
                            temp_names_and_scores.loc[len(temp_names_and_scores)] = [data_name, int(data_score)]

                        if count > top_count:
                            top_school = school
                            top_count = count
                            names_and_scores = temp_names_and_scores
                    
                    top_school

                    with ui.hold():
                        @render_widget
                        def names_line():
                            import plotly.express as px

                            fig = px.bar(names_and_scores, x='name', y='score')
                            fig.update_xaxes(visible=False, showgrid=False, categoryorder='total ascending')
                            fig.update_yaxes(visible=False, showgrid=False, range=[39, 50])
                            fig.update_layout(
                                height=100,
                                hovermode="x",
                                margin=dict(t=0, r=0, l=0, b=0),
                                plot_bgcolor="rgba(0,0,0,0)",
                                paper_bgcolor="rgba(0,0,0,0)",
                            )
                            
                            return fig
            
        with ui.card():
            @render_plotly
            def rank_school_by_subject():
                import plotly.express as px

                subject = input.subject_rank_school_by_subject()
                schools = input.school_rank_school_by_subject()

                specific = pd.DataFrame(columns=['school', 'student_count'])

                if 'All' in schools: schools = unique_schools

                for school in schools:
                    temp_data = data.loc[(data['subject'] == subject) & (data['school'] == school)]
                    count = temp_data.shape[0]

                    specific.loc[len(specific)] = [school, count]

                specific = specific.sort_values('student_count', ascending=False)

                plot_specific = specific.head(input.top_rank_school_by_subject())
                
                fig = px.bar(plot_specific, x='student_count', y='school')
                fig.update_yaxes(categoryorder='total ascending')

                return fig
            
with ui.nav_panel('Student results search'):
    with ui.layout_columns(col_widths=[5, 7]):
        
        with ui.card():
            ui.input_selectize(
                'student_student_lookup', 'Select a student',
                unique_students,
                multiple=False
            )
        
            with ui.value_box(showcase=ICONS["school"]):
                "School"
                @render.express
                def student_school_box():
                    student = input.student_student_lookup()
                    student_data = data.loc[data['name'] == student]
                    school_list = list(set(student_data['school'].tolist()))
                    school_list.append('No student selected')
                    school_list[0]

        with ui.card():
            @render_plotly
            def student_lookup():
                import plotly.express as px

                student = input.student_student_lookup()

                student_data = data.loc[data['name'] == student]

                return px.bar(student_data, x='scores', y='subject').update_yaxes(categoryorder='total ascending').update_xaxes(range=[39, 50])
            
with ui.nav_panel('Pie charts for response data'):
    with ui.layout_column_wrap(width=1/2):
        with ui.card():
            @render.text
            def piechart_response_text():
                return 'This data is sourced from a group of students, teachers and parents who voluntarily provided information for this statistics tool.'
            ui.input_selectize(
                'response_group_select', 'Select a group to see data.',
                ['All', 'Parent', 'Student', 'Teacher'],
                multiple=False
            )
        with ui.card():
            @render_plotly
            def comparing_schools_interested():
                import plotly.express as px

                group = input.response_group_select()

                comparing_schools_interested_data = response_data.loc[response_data['question'] == 'comparing_schools_interested']
                if group != 'All':
                    comparing_schools_interested_data = comparing_schools_interested_data.loc[comparing_schools_interested_data['group'] == group]

                return px.pie(comparing_schools_interested_data, values='count', names='answer', title='Percent interested in comparing schools by specific subjects.')
        with ui.card():
            @render_plotly
            def location_useful():
                import plotly.express as px

                group = input.response_group_select()

                comparing_schools_interested_data = response_data.loc[response_data['question'] == 'location_useful']
                if group != 'All':
                    comparing_schools_interested_data = comparing_schools_interested_data.loc[comparing_schools_interested_data['group'] == group]

                return px.pie(comparing_schools_interested_data, values='count', names='answer', title='Percent interested in comparing schools by location.')
        with ui.card():
            @render_plotly
            def website_or_app():
                import plotly.express as px

                group = input.response_group_select()

                comparing_schools_interested_data = response_data.loc[response_data['question'] == 'website_or_app']
                if group != 'All':
                    comparing_schools_interested_data = comparing_schools_interested_data.loc[comparing_schools_interested_data['group'] == group]

                return px.pie(comparing_schools_interested_data, values='count', names='answer', title='Website or app preferred for accessing a tool.')
            
with ui.nav_panel('Linear bar charts for response data'):
    with ui.layout_column_wrap(width=1/2):
        with ui.card():
            @render.text
            def linear_response_text_1():
                return 'This data is sourced from a group of students, teachers and parents who voluntarily provided information for this statistics tool.'
            @render.text
            def linear_response_text_2():
                return 'Click on any group in the key to hide or show it.'
        with ui.card():
            @render_plotly
            def access_data_importance():
                import plotly.express as px

                comparing_schools_interested_data = response_data.loc[response_data['question'] == 'access_data_importance']

                return px.bar(comparing_schools_interested_data, x='answer', y='count', color='group', title='Level of interest in school student performance data')
        with ui.card():
            @render_plotly
            def often_academic_compare():
                import plotly.express as px

                comparing_schools_interested_data = response_data.loc[response_data['question'] == 'often_academic_compare']

                return px.bar(comparing_schools_interested_data, x='answer', y='count', color='group', title='How often people need to compare student data')
        with ui.card():
            @render_plotly
            def privacy_concern():
                import plotly.express as px

                comparing_schools_interested_data = response_data.loc[response_data['question'] == 'privacy_concern']

                return px.bar(comparing_schools_interested_data, x='answer', y='count', color='group', title='Level of concern about student data privacy')