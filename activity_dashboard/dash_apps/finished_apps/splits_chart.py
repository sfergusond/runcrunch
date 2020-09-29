# -*- coding: utf-8 -*-
"""
Created on Wed May 27 17:14:26 2020

@author: sferg
"""
import plotly.graph_objects as go

from scripts import helper
from scripts import constants

COLORS = constants.COLORS
INTENSITYSCALE = constants.INTENSITYSCALE

async def laps_barchart(streams, laps, stats, athlete, auto=True):
    '''
    Helper Vars
    '''
    unit = athlete['unit']
    if unit == 'imperial':
        c = (1609.34, 3.28084, 'mi', 'ft', 'mins/mile')
    else:
        c = (1000, 1, 'km', 'm', 'mins/km')

    df = {**streams}
    df['elev'] = list(map(lambda x : x*c[1], df['elev']))
    df['dist'] = list(map(lambda x : x*(1/c[0]), df['dist']))

    PR_TIME = athlete['pr_time']
    PR_DISTANCE = athlete['pr_dist']
    numLaps = len(laps['dist'])
    offsets = [0]+[sum(laps['dist'][0:i]) for i in range(1, numLaps)]
    tickInfoPace = helper.tickInfo(streams, 'velocity',
                               space_list=[-3,-2,-1.5,-1,-.5,0,.5,1,1.5,2,3])

    def intensity_color(auto):
        '''
        returns a list of colors for each lap in the chart
        '''
        from scripts import riegel
        colors = ['']*numLaps
        text = ['']*numLaps
        accum_dist = 0

        for i in range(numLaps):
            if auto:
                accum_dist += laps['dist'][i] # accumulate laps
            else:
                accum_dist = laps['dist'][i] # use splits dist

            pct = riegel.riegel(PR_TIME,
                                PR_DISTANCE,
                                laps['gap'][i],
                                accum_dist, # accumulate laps
                                ret_type=int,
                                easy_pace=True)
            pct *= 2

            if pct > 190:
                colors[i], text[i] = ('#fc0dec', 'Race')
            elif pct > 180:
                colors[i], text[i] = ("#fa0c0c", 'VO2 Max')
            elif pct > 160:
                colors[i], text[i] = ("#f29624", 'Tempo')
            elif pct > 140:
                colors[i], text[i] = ("#f5e616", 'Threshold')
            elif pct > 115:
                colors[i], text[i] = ("#3dd44c", 'Endurance - Hard')
            elif pct > 85:
                colors[i], text[i] = ("#6de3db", 'Endurance - Moderate')
            elif pct > 60:
                colors[i], text[i] = ("#75acff", 'Endurance - Easy')
            else:
              colors[i], text[i] = ('#5c5c5c', 'Recovery')

        return (colors, text)
    intensity_colors, intensity_text = intensity_color(auto)

    def hovertext(metrics):
        '''
        Assembles a list of text elements to display on each bar
        '''
        result = ['']*numLaps

        for i in range(numLaps):
            text = {
            'dist': (round(laps['dist'][i]/c[0], 1), f' {c[2]}<br>'),
            'velocity': (helper.velocity_to_pace(laps['velocity'][i], _to=c[4]),
                         f' /{c[2]}<br>'),
            'gap': (helper.velocity_to_pace(laps['gap'][i], _to=c[4]),
                    f' /{c[2]} GAP<br>'),
            'elev': (int(round(laps['elev'][i]*c[1], 0)), f' {c[3]}<br>'),
            'intensity': (intensity_text[i], '')
            }
            for m in metrics:
                try:
                    result[i] += f'{text[m][0]}{text[m][1]}'
                except:
                    result[i] += ''
        return result

    def splits_table(header, laps, unit='imperial'):
        '''
        Formats laps as a table
        '''
        import pandas as pd

        convert = {
                'imperial': [3.28084, 0.000621371, "mins/mile", "ft", 'mi'],
                'metric': [1, .001, "mins/km", "m", 'km']
                }

        rows=[
            list(range(1, numLaps + 1)),
            [f'{round(i*convert[unit][1],2)} {convert[unit][-1]}' if i*convert[unit][1] < .96 or i*convert[unit][1] > 1.03 else f'{round(i*convert[unit][1],1)} {convert[unit][-1]}' for i in laps['dist']],
            [helper.format_time(laps['dist'][i]/laps['velocity'][i]) if laps['velocity'][i] > 1 and (laps['dist'][i]*convert[unit][1] < .97 or laps['dist'][i]*convert[unit][1] > 1.03) else helper.velocity_to_pace(laps['velocity'][i], _to=convert[unit][2]) for i in range(numLaps)],
            [f"{helper.velocity_to_pace(laps['velocity'][i], _to=convert[unit][2])} /{convert[unit][-1]}" for i in range(numLaps)],
            [f"{helper.velocity_to_pace(laps['gap'][i], _to=convert[unit][2])} /{convert[unit][-1]}" for i in range(numLaps)],
            [f'{int(i*convert[unit][0])} {convert[unit][3]}' for i in laps['total_gain']],
            [f'{int(i)} {convert[unit][3]}' for i in helper.convert_stream(laps['elev'], _to=convert[unit][3])],
            ['{:+.0f}'.format(i) + '%' for i in laps['avg_grade']],
            [f'{int(i*convert[unit][0])} {convert[unit][3]}' for i in laps['min_elev']],
            [f'{int(i*convert[unit][0])} {convert[unit][3]}' for i in laps['max_elev']],
            intensity_text
            ]

        df = pd.DataFrame(list(zip(*rows)), columns=header)
        df_html = df.to_html(index=False, escape=False) # replace <th> flags
        df_html = df_html[df_html.find('<tbody>'):df_html.find('</tbody>')]
        df_html = df_html.replace('<tr>0</tr>', '<tr></tr>').replace('NaN', '')

        return df_html + '</tbody>'

    fig = go.Figure()

    '''
    Figure Objects
    '''
    elev_check = sum(df['elev']) > 1
    gap_marker = dict(
                    color=COLORS['orangeT'].format('.3'),
                    line=dict(
                            width=2,
                            color=COLORS['orange']
                            )
                    )
    pace_marker = dict(
                    color=COLORS['blueT'].format('.3'),
                    line=dict(
                            width=2,
                            color=COLORS['blue']
                            ),
                    showscale=False
                    )

    elev = go.Scatter(
            name='Elevation',
            x=df['dist'],
            y=df['elev'],
            fill='tozeroy',
            mode='lines',
            opacity=sum(df['elev'])>1,
            line=dict(
                    shape='spline',
                    smoothing=1,
                    color=COLORS['green'],
                    simplify=True
                    ),
            hoverinfo='skip',
            visible=elev_check
            )
    GAP = go.Bar(
            x=[i for i in range(numLaps)],
            y=laps['gap'],
            width=[laps['dist'][i] for i in range(numLaps)],
            offset=offsets,
            opacity=.6,
            hoverinfo='text',
            hovertext=hovertext(['dist', 'gap', 'elev', 'intensity']),
            marker=gap_marker,
            visible=False
            )
    pace = go.Bar(
            x=[i for i in range(numLaps)],
            y=laps['velocity'],
            width=[laps['dist'][i] for i in range(numLaps)],
            offset=offsets,
            opacity=.6,
            hoverinfo='text',
            hovertext=hovertext(['dist', 'velocity', 'elev', 'intensity']),
            marker=pace_marker,
            visible=True
            )
    avg_pace = stats['velocity'] #stat.mean(streams['velocity'])
    avg_pace_line = go.Scatter( # Average Pace Line
            name='Avg Pace',
            x=[df['dist'][0], df['dist'][-1]],
            y=[avg_pace]*2,
            mode='lines',
            line=dict(
                    width=1.5,
                    shape='linear',
                    dash='dash',
                    color=COLORS['blue']
                    ),
            hoverinfo='name+text',
            hovertext=helper.velocity_to_pace(avg_pace, _to=c[4]),
            visible=True
            )
    avg_gap = stats['gap'] #stat.mean(df['gap'])
    avg_GAP_line = go.Scatter( # Average GAP Line
            name='Avg GAP',
            x=[df['dist'][0], df['dist'][-1]],
            y=[helper.pace_to_velocity(avg_gap, _from=c[4])]*2,
            mode='lines',
            line=dict(
                    width=1.5,
                    shape='linear',
                    dash='dash',
                    color=COLORS['orange']
                    ),
            hoverinfo='name+text',
            hovertext=avg_gap,
            visible=True
            )

    header=['Lap',
            'Distance',
            'Time',
            'Avg Pace',
            'Avg GAP',
            'Total Gain',
            'Elev Change',
            'Avg Grade',
            'Min Elev',
            'Max Elev',
            'Intensity']

    table = splits_table(header, laps, unit=unit)

    '''
    Draw Objects
    '''
    fig.add_trace(elev)
    fig.add_trace(GAP)
    fig.add_trace(pace)
    fig.add_trace(avg_GAP_line)
    fig.add_trace(avg_pace_line)

    '''
    Manipulate Axes
    '''
    fig['data'][1].update(yaxis='y2')
    fig['data'][2].update(yaxis='y2')
    fig['data'][3].update(yaxis='y2')
    fig['data'][4].update(yaxis='y2')
    fig['data'][1].update(xaxis='x2')
    fig['data'][2].update(xaxis='x2')

    max_elev = max(df['elev']) + ((max(df['elev']) - min(df['elev'])) * .4)
    if max_elev < 10:
        lpad = 20
    elif max_elev < 1000:
        lpad = 25
    elif max_elev < 10000:
        lpad = 30
    else:
        lpad = 35

    if numLaps >= 10:
        bpad = 25
    else:
        bpad = 15

    fig.update_layout(
            autosize=False,
            width=520,
            height=460,
            showlegend=False,
            plot_bgcolor=COLORS['transparent'],
            margin=dict(
                    pad=1,
                    l=lpad,
                    r=35,
                    t=0,
                    b=bpad,
                    autoexpand=False
                    ),
            xaxis=dict(
                    showgrid=False,
                    visible=False
                    ),
            yaxis=dict(
                    range=[min(df['elev'])*.99,
                           max_elev*1.1],
                    side='left',
                    showgrid=False,
                    visible=elev_check
                    ),
            xaxis2=dict(
                    showgrid=False,
                    overlaying='x',
                    tickvals= [offsets[i]+laps['dist'][i]/2 for i in range(numLaps)],
                    ticktext=[str(i+1) for i in range(numLaps)],
                    ),
            yaxis2=dict(
                    range=[min(laps['velocity'])*.8, max(laps['velocity'])*1.2],
                    showgrid=False,
                    overlaying='y',
                    side='right',
                    anchor='x2',
                    position=0,
                    visible=True,
                    tickvals=tickInfoPace,
                    ticktext=[f'{helper.velocity_to_pace(v, _to=c[4])} /{c[2]}' for v in tickInfoPace]
                    )
            )
    '''
    Buttons
    '''
    fig.update_layout(
            updatemenus=[dict(
                    type='buttons',
                    direction='left',
                    buttons=list([
                            dict(   args=['visible', [True, False, True, True, True]],
                                    args2= ['visible', [True]*5],
                                    label='Toggle GAP',
                                    method='restyle'
                                    )
                            ]),
                    pad={"r": 10, "t": 10},
                    bordercolor=COLORS['blue'],
                    bgcolor=COLORS['gray1'],
                    borderwidth=1.5,
                    showactive=True,
                    x=0.1,
                    xanchor="left",
                    y=1,
                    yanchor="top",
                    ), dict(
                    type='buttons',
                    direction='left',
                    buttons=list([
                            dict(
                                    args=[{'marker.color': [None,
                                                      COLORS['orangeT'].format('.3'),
                                                      COLORS['blueT'].format('.3')]}],
                                    args2=[{'marker.color': [None,
                                                      intensity_colors,
                                                      intensity_colors]}],
                                    label='Toggle Intensity',
                                    method='restyle'
                                    )
                            ]),
                    pad={"r": 10, "t": 10},
                    bordercolor=COLORS['blue'],
                    bgcolor=COLORS['gray1'],
                    borderwidth=1.5,
                    showactive=True,
                    x=.325,
                    xanchor="left",
                    y=1,
                    yanchor="top"
                    )
                ]

    )

    if auto: g_id = 'g3'
    else: g_id = 'g4'

    return fig.to_html(include_plotlyjs='cdn', include_mathjax='cdn', full_html=False,
                       config=dict(displayModeBar=False)), table, g_id