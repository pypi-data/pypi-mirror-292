from google.cloud import bigquery as bq
from pandas_gbq import to_gbq


def get_worlds_team_ids(world_name):
    client = bq.Client()

    teams_sql = f'''
    select wts.team_id
    from hoops_dynasty.worlds_to_schools wts
    left join hoops_dynasty.worlds w
        on wts.world_id = w.id
    where lower(w.world_name) = "{world_name.lower()}"
    group by wts.team_id
    '''

    query_job = client.query(teams_sql)

    results = query_job.result()

    for row in results:
        yield row.team_id


def df_to_bq(df, project, table):
    to_gbq(df, table, project_id=project, if_exists='append')
