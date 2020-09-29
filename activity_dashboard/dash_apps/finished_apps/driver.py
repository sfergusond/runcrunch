# -*- coding: utf-8 -*-
"""
Created on Tue May 26 15:10:04 2020

@author: sferg
"""
import stravalib
import psycopg2 as psy
import os
import datetime
import numpy as np
import asyncio
import aiohttp
import json

from scripts import helper
from scripts import gap
from scripts import riegel
from scripts import postgres as db

from . import activities_chart
from . import pace_gap_elev
from . import map_charts
from . import splits_chart
from . import last7
from . import trend_graphs
from . import pace_zones

'''
Add New User
'''
def add_new_athlete(username, code):
    # Get API Auth info from DB
    conn = psy.connect(os.environ['DATABASE_URL'], sslmode='prefer')

    # Authenticate athlete
    client = stravalib.Client()
    codes = client.exchange_code_for_token(int(os.environ['STRAVA_CLIENT_ID']),
                                           os.environ['STRAVA_CLIENT_SECRET'], code)

    # Get athlete info from Strava
    client = stravalib.Client(access_token=codes['access_token'])
    athlete = client.get_athlete()
    created_at = athlete.created_at
    if athlete.country == 'United States':
        unit = 'imperial'
    else:
        unit = 'metric'

    # Default PR value: 6:30 mile, insert athlete
    vals = f"{athlete.id}, '{codes['access_token']}', '{codes['refresh_token']}', {codes['expires_at']}, '{unit}', '{created_at}', 390, 1609, '{username}', '{athlete.profile}', 'pro', 'N', NULL, NULL"

    try:
        db.INSERT(table='athletes', vals=vals, conn=conn)
    except:
        conn.close()
        return False

    conn.close()
    return True

'''
Authenticate Athlete
'''
def authenticate(athlete, return_token=False):
    import time

    access_token = athlete['access_token']

    if time.time() > athlete['expires_at'] - 100:
        try:
            codes = helper.refresh_token(athlete['refresh_token'])
        except:
            pass

        db.UPDATE('athletes', where=f"a_id = {athlete['a_id']}",
                  numCols=3, cols="access_token, refresh_token, expires_at",
                  vals=f"'{codes['access_token']}', '{codes['refresh_token']}',     {codes['expires_at']}")

        access_token = codes['access_token']
    try:
        client = stravalib.Client(access_token=access_token)
    except:
        return None

    if return_token: return access_token

    return client

def get_athlete(username, activity_id=0):
    conn = psy.connect(os.environ['DATABASE_URL'], sslmode='prefer')

    # Load athlete info and set environ vars
    athlete = db.SELECT('athletes', where=f"username = '{username}'", conn=conn)

    if activity_id:
        activity = db.SELECT('activities', where=f"activity_id = {activity_id}", conn=conn)
        if activity['a_id'] != athlete['a_id']:
            raise LookupError

    # If subscription has a date field, change tier status if past date
    try:
        expiration = datetime.datetime.strptime(athlete['subscription'], '%Y-%m-%d')
        if expiration <= datetime.datetime.today():
            db.UPDATE('athletes', where=f"username = '{username}'", numCols=2,
                      cols="tier, subscription", vals="'free', NULL", conn=conn)
            athlete['tier'] = 'free'
    except:
        pass

    conn.close()

    return athlete

def quick_links(data):
    import calendar
    today = datetime.datetime.today().date()
    quick_item = int(data['quick_items'])

    if quick_item == 0:
        if data['quick_links'] == 'this_week':
            f = helper.next_sunday(today)
            s = f - datetime.timedelta(days=6)
        elif data['quick_links'] == 'this_month':
            monthrange = calendar.monthrange(today.year, today.month)
            f = datetime.date(today.year, today.month, monthrange[1])
            s = datetime.date(today.year, today.month, 1)
        else:
            f = datetime.date(today.year, 12, 31)
            s = datetime.date(today.year, 1, 1)
    else:
        if data['unit'] == 'weeks':
            f = helper.next_sunday(today)
            s = f - datetime.timedelta(days=((quick_item)*7-1))
        elif data['unit'] == 'months':
            import pandas as pd
            cur_month = calendar.monthrange(today.year, today.month)
            s_date = today - pd.DateOffset(months=quick_item-1)
            f = datetime.date(today.year, today.month, cur_month[1])
            s = datetime.date(s_date.year, s_date.month, 1)
        else:
            f = datetime.date(today.year, 12, 31)
            s = datetime.date(today.year - quick_item + 1, 1, 1)
    return s, f

'''
Activity Dashboard View
'''
def activity_dashboard(athlete, after, before):
    import datetime

    conn = psy.connect(os.environ['DATABASE_URL'], sslmode='prefer')
    a_id = athlete['a_id']
    unit = athlete['unit']

    delta = (before - after).days
    runs = db.SELECT('activities',
                 where=f"a_id = {a_id} AND date BETWEEN '{after}' AND '{before}'", conn=conn)
    runs_dict = helper.organize_dict(runs, 'date')

    # Barcharts
    if runs: # runs != []
        graphs_dict = asyncio.run(dashboard_charts(runs, runs_dict, before, delta, unit))
    else:
        graphs_dict = {}

    graphs = (
            graphs_dict.get('dist', ''),
            graphs_dict.get('time', ''),
            graphs_dict.get('elev', ''),
            graphs_dict.get('velocity', ''),
            graphs_dict.get('avg_hr', ''),
            graphs_dict.get('intensity', ''),
            graphs_dict.get('achievement_count', ''),
            graphs_dict.get('kudos_count', ''),
            graphs_dict.get('tod', ''),
            graphs_dict.get('table', '')
            )

    # Last7
    last7_runs = db.SELECT('activities', where=f"a_id = {a_id} AND date BETWEEN '{datetime.datetime.today()-datetime.timedelta(days=6)}' AND '{datetime.datetime.today()}'", conn=conn)
    last7_stats = last7.last7(last7_runs, unit)

    # Month stats
    import calendar
    today = datetime.datetime.today()
    mo_range = calendar.monthrange(today.year, today.month)
    mo_start = datetime.datetime.strftime(datetime.date(today.year, today.month, 1), '%Y-%m-%d')
    mo_end = datetime.datetime.strftime(datetime.date(today.year, today.month, mo_range[1]), '%Y-%m-%d')
    month_runs = db.SELECT('activities', where=f"a_id = {a_id} AND date BETWEEN '{mo_start}' AND '{mo_end}'", conn=conn)
    month_stats = last7.last7(month_runs, unit)

    yr_runs = db.SELECT('activities', where=f"a_id = {a_id} AND date BETWEEN '{today.year}-01-01' AND '{today}'", conn=conn)
    yr_stats = last7.last7(yr_runs, unit)

    # View stats
    view_stats = last7.last7(runs, unit)

    conn.close()

    # Display info
    info = {
            'date_end': before.strftime('%a, %b %d, %Y'),
            'date_start': after.strftime('%a, %b %d, %Y'),
            'date_end_abv': before.strftime('%m/%d/%y'),
            'date_start_abv': after.strftime('%m/%d/%y')
            }

    return graphs + (info, last7_stats, view_stats, month_stats, yr_stats)

async def dashboard_charts(runs, runs_dict, before, delta, unit):
    tasks = []
    metrics = ['dist', 'time', 'elev', 'velocity', 'avg_hr', 'intensity', 'achievement_count', 'kudos_count']
    graphs = {}

    '''
    Find max number of runs in one day
    '''
    stacks = max(list(map(lambda x : len(x), runs_dict.values())))

    base = before
    begin = before-datetime.timedelta(days=delta)

    index = [(begin + datetime.timedelta(days=x)).strftime('%Y-%m-%d') for x in range(0, (base-begin).days + 1)]

    for m in metrics:
        tasks.append(activities_chart.unpack_runs(runs_dict, stacks, index, m, unit))

    stack_dict_list = await asyncio.gather(*tasks)

    tasks = [activities_chart.tod_chart(runs, before, delta),
             activities_chart.activities_table(runs, unit)]

    for i in stack_dict_list:
        tasks.append(activities_chart.activities_chart(stacks, i[0], i[1],
                                                        i[2], index, before, delta,
                                                        i[-1], unit))

    graph_list = await asyncio.gather(*tasks, return_exceptions=True)

    for graph in graph_list:
        try:
            graphs[graph[1]] = graph[0]
        except:
            pass

    return graphs

'''
Activity Detail View
'''
def activity_details(athlete, activity_id):
    # Get athlete info from DB
    conn = psy.connect(os.environ['DATABASE_URL'], sslmode='prefer')
    unit = athlete['unit']
    weather, streams, streams_laps, map_stream = None, None, None, None

    # Authenticate athlete
    client = authenticate(athlete)

    # Get run stats
    try:
        run = client.get_activity(activity_id).to_dict()
    except:
        try: # hit rate limit, try getting data from DB
            run = db.SELECT('activities', where=f"activity_id = {activity_id}")
            stats = last7.last7([run], unit)
            stats['name'] = run['name']
            stats['date'] = run['date']
            try:
                weather = helper.weather(run['datetime'], run['start_lat'], run['start_lng'])
            except:
                weather = ''
            return (stats, weather) + (None, )*3
        except:
            return (None, )*5

    dt = datetime.datetime.strptime(run['start_date_local'].replace('T', ' '), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
    try:
        weather = helper.weather(dt, run['start_latitude'], run['start_longitude'], unit)
    except:
        weather = ''

    # Collect streams and udpate DB
    try:
        streams_laps, streams, map_stream = helper.get_run_streams(client, activity_id)
        stats = helper.run_stats(run, athlete, streams=streams)
        conn.close()
    except:
        conn.close()
        stats = helper.run_stats(run, athlete, streams=None)

    return stats, weather, streams, streams_laps, map_stream

async def graphs(athlete, stats, streams, streams_laps, map_stream):
    unit = athlete['unit']
    graphs = {}
    tables = []

    try:
        df = {**streams}
    except:
        raise TypeError

    df['total_distance'] = stats['meters']
    splits_info_auto = gap.splits_GAP(streams, int(stats['distance']+.95), unit, False)
    if len(stats['laps']) == 1:
        splits_info_device = gap.splits_GAP(streams, stats['laps'], unit, laps=True)
    else:
        splits_info_device = gap.splits_GAP(streams_laps, stats['laps'], unit, laps=True)

    tasks = [
            map_charts.trace_map(map_stream, streams_laps, stats, athlete),
            map_charts.profile3D(map_stream, stats, athlete),
            pace_gap_elev.pace_gap_elev_chart(df, athlete),
            pace_zones.zone_chart(streams, stats, athlete),
            pace_zones.grades(streams, stats, athlete),
            map_charts.map_pic(map_stream),
            splits_chart.laps_barchart(streams, splits_info_auto, stats, athlete, auto=True),
            splits_chart.laps_barchart(streams_laps, splits_info_device, stats, athlete, auto=False)
            ]

    graphs_objs = await asyncio.gather(*tasks, return_exceptions=True)
    for g in graphs_objs:
        try:
            if g[-1] == 'g3' or g[-1] == 'g4':
                graphs[g[-1]] = g[0]
                tables.append(g[1])
            else:
                graphs[g[-1]] = g[0]
        except:
            pass

    return graphs, tables

'''
Heatmap
'''
def heatmap(athlete):
    from scripts import polyline
    import zlib
    import time
    RAW_MAP = {8:r'\b', 7:r'\a', 12:r'\f', 10:r'\n', 13:r'\r', 9:r'\t', 11:r'\v'}
    t0 = time.time()

    # Get athlete info from DB
    conn = psy.connect(os.environ['DATABASE_URL'], sslmode='prefer')
    a_id = athlete['a_id']

    # Get runs/streams
    raw = db.SELECT('polylines', where=f'a_id = {a_id}', conn=conn)
    print('FETCHED:', time.time()-t0)
    latlng = raw['polyline'].split(',')
    lat = []
    lng = []
    print('SPLIT:', time.time()-t0)

    # Decode
    for line in latlng:
        raw = r''.join(i if ord(i) > 32 else RAW_MAP.get(ord(i), i) for i in line)
        decoded = polyline.decode(raw, precision=5)
        if not decoded: continue
        lat += list(map(lambda x : x[0], decoded))
        lng += list(map(lambda x: x[1], decoded))
    print('DECODED:', time.time()-t0)

    # Get map
    heatmap = map_charts.global_heatmap(lat, lng)
    print('MAP:', time.time()-t0)

    return heatmap

def trends(athlete, metric):
    import pandas as pd
    import math
    import datetime

    # Select runs
    conn = psy.connect(os.environ['DATABASE_URL'], sslmode='prefer')
    cur_year = datetime.datetime.today().year
    all_runs = db.SELECT('activities', where=f"a_id = {athlete['a_id']}", conn=conn)
    conn.close()

    try:
        # Create and group DataFrame
        if metric == 'pace':
            df = pd.DataFrame(all_runs, columns=['date', 'dist', 'time'])
            pace = list(map(lambda t, d: d/t if t > 0 else math.nan, df['time'],
                            df['dist']))
            df.insert(loc=0, column='pace', value=pace)
        else:
            df = pd.DataFrame(all_runs, columns=['date', metric])

        df.dropna(axis=0)
        df['date'] = pd.to_datetime(df['date'])
        cr_year = min(df['date']).year

        if metric in ['dist', 'time', 'elev']:
            monthly = df.groupby([df['date'].dt.year, df['date'].dt.month]).sum()
            weekly = df.groupby([df['date'].dt.year, df['date'].dt.strftime('%W')]).sum()
        else:
            monthly = df.groupby([df['date'].dt.year, df['date'].dt.month]).mean()
            weekly = df.groupby([df['date'].dt.year, df['date'].dt.strftime('%W')]).mean()

        monthly_trends, monthly_table = trend_graphs.trend(monthly, 12, range(cr_year, cur_year + 1), athlete['unit'])

        weekly_trends, weekly_table = trend_graphs.trend(weekly, 52, range(cr_year, cur_year+1), athlete['unit'])

        mega_h = trend_graphs.mega_hist(df, metric, athlete['unit'])
        mega_b = trend_graphs.mega_box(df, metric, athlete['unit'])
    except:
        return (None, )*4 + ('', '')

    return (monthly_trends, weekly_trends, mega_h, mega_b, monthly_table, weekly_table)