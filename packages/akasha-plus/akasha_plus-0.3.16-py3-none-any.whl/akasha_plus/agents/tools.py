import akasha
import pandas as pd
import os
import re
import json
import requests
import psycopg2
import sqlite3
import pymssql
import mysql.connector

from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Union
import akasha_plus.agents.default_prompts as dp

# display all rows and columns when printing dataframe
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

DEFAULT_MODEL = 'openai:gpt-4'
VERBOSE = True

def set_connection_config(
    sql_type:str, 
    database:str, 
    user:str='', 
    password:str='', 
    host:str='', 
    port:str=''
):
    connection_config = {}
    connection_config['SQL_TYPE'] = sql_type
    connection_config['DB_NAME'] = database
    if user:
        connection_config['DB_USER'] = user
    if password:
        connection_config['DB_PASSWORD'] = password
    if host:
        connection_config['DB_HOST'] = host
    if port:
        connection_config['DB_PORT'] = port
    return connection_config

def _get_data(
    sql_cmd:str, 
    connection_config:Dict[str, str]={}
) -> pd.DataFrame:
    sql_type = connection_config.get('SQL_TYPE', 'SQLITE').upper()
    database = connection_config.get('DB_NAME', 'database.db')
    user = connection_config.get('DB_USER', '')
    password = connection_config.get('DB_PASSWORD', '')
    host = connection_config.get('DB_HOST', '')
    port = connection_config.get('DB_PORT', '')
    if sql_type == 'POSTGRESQL':
        conn = psycopg2.connect(
            database=database, 
            user=user, 
            password=password, 
            host=host, 
            port=port
        ) 
    elif sql_type == 'MYSQL':
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
    elif sql_type == 'MSSQL':
        conn = pymssql.connect(
            server=f'{host}:{port}', 
            user=user, 
            password=password, 
            database=database
        )
    elif sql_type == 'SQLITE':
        conn = sqlite3.connect(database)
    else:
        raise ValueError(f'Unsupported SQL_TYPE={sql_type}')
    try:
        # Execute the SQL command and fetch the data
        df = pd.read_sql_query(sql_cmd, conn)
    finally:
        # Ensure the connection is closed
        conn.close()
    return df

def _get_table_schema(
    table_name:str, 
    connection_config:Dict[str, str]={}
) -> pd.DataFrame:
    sql_type = connection_config.get('SQL_TYPE', 'SQLITE').upper()
    database = connection_config.get('DB_NAME', 'database.db')
    if sql_type in ('POSTGRESQL', 'MSSQL'):
        sql = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}';"
    elif sql_type == 'MYSQL':
        sql = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}' and table_schema = '{database}';"
    elif sql_type == 'SQLITE':
        sql = f"SELECT name AS column_name, type AS data_type FROM pragma_table_info('{table_name}');"
    else:
        raise ValueError(f'Unsupported SQL_TYPE={sql_type}')
    return _get_data(sql, connection_config=connection_config)

def _modify_prompts(
    origin_prompts, 
    prompt_key:str, 
    modify_types:List[str]=['prompt', 'system_prompt'], 
    **custom_prompts
):
    if prompt_key in custom_prompts:
        if isinstance(custom_prompts[prompt_key], dict):
            for mt in modify_types:
                if mt in custom_prompts[prompt_key]:
                    modified = custom_prompts[prompt_key][mt]
                    origin_prompts.update({mt:modified})
    return origin_prompts

#%% Function
def db_query_func(
    question: str, 
    table_name: str, 
    column_description_json:Union[str, dict]=None, 
    simplified_answer:bool=False, 
    connection_config:Dict[str,str]={}, 
    model:str=DEFAULT_MODEL,
    **custom_prompts
):  
    ak = akasha.Doc_QA(model=model, verbose=VERBOSE)
    sql_type = connection_config.get('SQL_TYPE', 'SQLITE').upper()
    # table structure
    table_schema_df = _get_table_schema(
        table_name=table_name, 
        connection_config=connection_config
    )
    columns = ','.join(table_schema_df['column_name'].tolist())
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # column description
    if column_description_json is not None:
        try:
            if isinstance(column_description_json, dict):
                column_description = column_description_json
            elif isinstance(column_description_json, str): 
                if column_description_json.endswith('.json'):
                    with open(column_description_json, 'r') as f:
                        column_description = json.load(f)
                else:
                    column_description = json.loads(column_description_json)
        except Exception as e:
            print('Error:', e)
            column_description = {}
    else:
        column_description = {}
    # sample data
    ROW_LIMIT = 1
    ## row where fewest columns are null
    top_or_not = f'TOP {ROW_LIMIT}' if sql_type == 'MSSQL' else ''
    order_by_columns_fewest = 'ORDER BY (' + '+'.join([f'CASE WHEN {col} IS NULL THEN 1 ELSE 0 END' for col in table_schema_df['column_name']]) + ') ASC' if table_schema_df.shape[0] > 0 else ''
    limit_or_not = f'LIMIT {ROW_LIMIT}' if sql_type != 'MSSQL' else ''
    sql_fewest_null_records = f'SELECT {top_or_not} * FROM "{table_name}" {order_by_columns_fewest} {limit_or_not};'
    fewest_null_records = _get_data(sql_fewest_null_records, connection_config=connection_config).head(ROW_LIMIT)
    ## row where most columns are null
    order_by_columns_most = 'ORDER BY (' + '+'.join([f'CASE WHEN {col} IS NULL THEN 0 ELSE 1 END' for col in table_schema_df['column_name']]) + ') ASC' if table_schema_df.shape[0] > 0 else ''
    sql_most_null_records = f'SELECT {top_or_not} * FROM "{table_name}" {order_by_columns_most} {limit_or_not};'
    most_null_records = _get_data(sql_most_null_records, connection_config=connection_config).head(ROW_LIMIT)
    sample_data = pd.concat([fewest_null_records, most_null_records], axis=1)
    
    info = {'欄位說明': column_description, 
            '表格結構': dict(zip(table_schema_df['column_name'], table_schema_df['data_type'])),
            '範例資料': sample_data} # to_dict(orient='list') #orient='records'
    if not columns:
        columns = '*'
        columns_str = ''
    else:
        columns_str = f'包含{columns}之'
    
    count_sample_usage_str = '*'
    if isinstance(columns, list):
        if len(columns) >= 1:
            count_sample_usage_str = columns[0]
    
    max_retry = 5
    cnt = 0
    while True:
        prompts = {
            'prompt': dp.GENERATE_SQL_TASK['prompt'].format(
                table_name=table_name,
                current_datetime=current_datetime,
                question=question,
                columns_str=columns_str,
                sql_type=sql_type,
            ),
            'system_prompt': dp.GENERATE_SQL_TASK['system_prompt'].format(
                columns=columns,
                table_name=table_name,
                count_sample_usage_str=count_sample_usage_str,
            )
        }
        prompts = _modify_prompts(
            prompts, 
            prompt_key='sql_prompts', 
            modify_types=['prompt', 'system_prompt'], 
            **custom_prompts
        )
        sql = ak.ask_self(
            prompt=prompts['prompt'],
            info=str(info),
            system_prompt=prompts['system_prompt'],
            verbose=VERBOSE
        ) 
        cnt += 1
        # check if the sql statement is appropriate: all keywords are included
        column_names = [cn for cn in columns.replace(' ','').lower().split(',') if cn] 
        keywords = ["select", "from", table_name.lower()]
        if all([k in sql.lower() for k in keywords]) and (any([c in sql.lower() for c in column_names]) or columns == '*'):
            break
        if cnt > max_retry:
            raise ValueError(f'Exceed max retry times={max_retry} to generate appropriate sql statement')
    
    cnt = 0    
    while True:
        try:
            data = _get_data(sql, connection_config=connection_config)
            break
        except pd.errors.DatabaseError as e:
            print(f'Exception occurred when calling _get_data due to: {e}')
            # remove "group by", "having", "join", "union", "insert", "update", "delete", "all" keywords
            keywords = ["group by", "having", "join", "union", "insert", "update", "delete", "all"]
            pattern = r'\b(' + '|'.join(re.escape(keyword) for keyword in keywords) + r')\b'
            match = re.search(pattern, sql, re.IGNORECASE)
            if match:
                sql = sql[:match.start()]
            # remove "select" after the first one
            pattern = r'\bselect\b'
            matches = list(re.finditer(pattern, sql, re.IGNORECASE))
            if len(matches) >= 2:    
                sql = sql[:matches[1].start()]
            # remove other characters before "select"
            pattern = r'\bselect\b'
            match = re.search(pattern, sql, re.IGNORECASE)
            if match:
                sql = sql[match.start():]
            # remove all `
            sql = sql.replace('`', '')
            # add double quotes for table name if not exist
            if table_name in sql:
                if f'"{table_name}"' not in sql:
                    sql = sql.replace(table_name, f'"{table_name}"')
        
        cnt += 1
        if cnt > max_retry:
            raise ValueError(f'Exceed max retry times={max_retry} to get data from database')
    prompts = {
        'prompt': dp.GENERATE_ANSWER_TASK['prompt'].format(
            table_name=table_name,
            sql=sql,
            data=data,
            question=question
        ),
        'system_prompt': dp.GENERATE_ANSWER_TASK['system_prompt'].format()
    }
    prompts = _modify_prompts(
        prompts, 
        prompt_key='answer_prompts', 
        modify_types=['prompt', 'system_prompt'], 
        **custom_prompts
    )     
    answer = ak.ask_self(
        prompt=prompts['prompt'],
        info=str(info),
        system_prompt=prompts['system_prompt'],
        verbose=VERBOSE
    )
    
    if simplified_answer:
        prompts = {
            'prompt': dp.SIMPLIFY_ANSWER_TASK['prompt'].format(
                answer=answer,
            ),
            'system_prompt':dp.SIMPLIFY_ANSWER_TASK['system_prompt'].format(
                question=question  
            ),
        }
        prompts = _modify_prompts(
            prompts, 
            prompt_key='simplify_prompts', 
            modify_types=['prompt', 'system_prompt'], 
            **custom_prompts
        ) 
        answer = ak.ask_self(
            prompt=prompts['prompt'],
            system_prompt=prompts['system_prompt'],
            verbose=VERBOSE
        )
    return answer

def db_data_func(
    question: str, 
    table_name: str, 
    column_description_json:Union[str, dict]=None, 
    connection_config:Dict[str,str]={}, 
    model:str=DEFAULT_MODEL,
    **custom_prompts
):  
    ak = akasha.Doc_QA(model=model, verbose=VERBOSE)
    sql_type = connection_config.get('SQL_TYPE', 'SQLITE').upper()
    # table structure
    table_schema_df = _get_table_schema(
        table_name=table_name, 
        connection_config=connection_config
    )
    columns = ','.join(table_schema_df['column_name'].tolist())
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # column description
    if column_description_json is not None:
        try:
            if isinstance(column_description_json, dict):
                column_description = column_description_json
            elif isinstance(column_description_json, str): 
                if column_description_json.endswith('.json'):
                    with open(column_description_json, 'r') as f:
                        column_description = json.load(f)
                else:
                    column_description = json.loads(column_description_json)
        except Exception as e:
            print('Error:', e)
            column_description = {}
    else:
        column_description = {}
    # sample data
    ROW_LIMIT = 1
    ## row where fewest columns are null
    top_or_not = f'TOP {ROW_LIMIT}' if sql_type == 'MSSQL' else ''
    order_by_columns_fewest = 'ORDER BY (' + '+'.join([f'CASE WHEN {col} IS NULL THEN 1 ELSE 0 END' for col in table_schema_df['column_name']]) + ') ASC' if table_schema_df.shape[0] > 0 else ''
    limit_or_not = f'LIMIT {ROW_LIMIT}' if sql_type != 'MSSQL' else ''
    sql_fewest_null_records = f'SELECT {top_or_not} * FROM "{table_name}" {order_by_columns_fewest} {limit_or_not};'
    fewest_null_records = _get_data(sql_fewest_null_records, connection_config=connection_config).head(ROW_LIMIT)
    ## row where most columns are null
    order_by_columns_most = 'ORDER BY (' + '+'.join([f'CASE WHEN {col} IS NULL THEN 0 ELSE 1 END' for col in table_schema_df['column_name']]) + ') ASC' if table_schema_df.shape[0] > 0 else ''
    sql_most_null_records = f'SELECT {top_or_not} * FROM "{table_name}" {order_by_columns_most} {limit_or_not};'
    most_null_records = _get_data(sql_most_null_records, connection_config=connection_config).head(ROW_LIMIT)
    sample_data = pd.concat([fewest_null_records, most_null_records], axis=1)
    
    info = {'欄位說明': column_description, 
            '表格結構': dict(zip(table_schema_df['column_name'], table_schema_df['data_type'])),
            '範例資料': sample_data} # to_dict(orient='list') #orient='records'
    if not columns:
        columns = '*'
        columns_str = ''
    else:
        columns_str = f'包含{columns}之'
    
    count_sample_usage_str = '*'
    if isinstance(columns, list):
        if len(columns) >= 1:
            count_sample_usage_str = columns[0]
    
    max_retry = 5
    cnt = 0
    while True:
        prompts = {
            'prompt': dp.GENERATE_SQL_TASK['prompt'].format(
                table_name=table_name,
                current_datetime=current_datetime,
                question=question,
                columns_str=columns_str,
                sql_type=sql_type,
            ),
            'system_prompt': dp.GENERATE_SQL_TASK['system_prompt'].format(
                columns=columns,
                table_name=table_name,
                count_sample_usage_str=count_sample_usage_str,
            )
        }
        prompts = _modify_prompts(
            prompts, 
            prompt_key='sql_prompts', 
            modify_types=['prompt', 'system_prompt'], 
            **custom_prompts
        )
        sql = ak.ask_self(
            prompt=prompts['prompt'],
            info=str(info),
            system_prompt=prompts['system_prompt'],
            verbose=VERBOSE
        ) 
        cnt += 1
        # check if the sql statement is appropriate: all keywords are included
        column_names = [cn for cn in columns.replace(' ','').lower().split(',') if cn] 
        keywords = ["select", "from", table_name.lower()]
        if all([k in sql.lower() for k in keywords]) and (any([c in sql.lower() for c in column_names]) or columns == '*'):
            break
        if cnt > max_retry:
            raise ValueError(f'Exceed max retry times={max_retry} to generate appropriate sql statement')
    
    cnt = 0    
    while True:
        try:
            data = _get_data(sql, connection_config=connection_config)
            break
        except pd.errors.DatabaseError:
            # remove "group by", "having", "join", "union", "insert", "update", "delete", "all" keywords
            keywords = ["group by", "having", "join", "union", "insert", "update", "delete", "all"]
            pattern = r'\b(' + '|'.join(re.escape(keyword) for keyword in keywords) + r')\b'
            match = re.search(pattern, sql, re.IGNORECASE)
            if match:
                sql = sql[:match.start()]
            # remove "select" after the first one
            pattern = r'\bselect\b'
            matches = list(re.finditer(pattern, sql, re.IGNORECASE))
            if len(matches) >= 2:    
                sql = sql[:matches[1].start()]
            # remove other characters before "select"
            pattern = r'\bselect\b'
            match = re.search(pattern, sql, re.IGNORECASE)
            if match:
                sql = sql[match.start():]
            # remove all `
            sql = sql.replace('`', '')
        
        cnt += 1
        if cnt > max_retry:
            raise ValueError(f'Exceed max retry times={max_retry} to get data from database')
    
    return data

def webpage_summary_func(
    url:str, 
    summary_len:int=100, 
    extract_topics:List[str]=[], 
    list_result:bool=True, 
    model:str=DEFAULT_MODEL, 
    **custom_prompts
):
    # parse url
    try:
        response = requests.get(url)
        response.raise_for_status()  
        soup = BeautifulSoup(response.content, 'html.parser')
        article = soup.get_text()
        
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        article = '' 
        return '' 
    
    # summarize
    hint_extract_topics = ''
    if len(extract_topics) > 0:
        extract_topics_str = '\n'.join(f'* {extract_topics}')
        hint_extract_topics = f'重點論述擷取標的：\n{extract_topics_str}\n若無法擷取上述標的，請放棄擷取，否則罰你10000元。'
    if len(article) <= summary_len:
        summary = article
    else:
        chunk_size = 500
        prompts = {
            'system_prompt': dp.SUMMARY_TASK['system_prompt'].format(
                hint_extract_topics=hint_extract_topics
            )
        }
        prompts = _modify_prompts(
            prompts, 
            'summary_prompts', 
            modify_types=['system_prompt'], 
            **custom_prompts
        )
        sum_ak = akasha.summary.Summary(
            chunk_size=chunk_size, 
            model=model, 
            verbose=VERBOSE
        )
        summary = sum_ak.summarize_articles(
            articles=article, 
            summary_type="map_reduce", 
            summary_len=summary_len, 
            chunk_overlap=min(len(article)//10, chunk_size/2),
            system_prompt=prompts['system_prompt']
        ) 
    if summary and list_result:
        ak = akasha.Doc_QA(
            model=model, 
            verbose=VERBOSE
        )
        prompts = {
            'prompt': dp.SUMMARY_LIST_TASK['prompt'].format(),
            'system_prompt': dp.SUMMARY_LIST_TASK['system_prompt'].format(
                summary_len=summary_len
            ),
        }
        prompts = _modify_prompts(
            prompts, 
            prompt_key='list_summary_prompts', 
            modify_types=['prompt', 'system_prompt'], 
            **custom_prompts
        )
        summary = ak.ask_self(
            prompt=prompts['prompt'],
            info=summary,
            system_prompt=prompts['system_prompt']
        )    
    return summary
    
def collect_dialogue_info_func(
    dialogue_history:str, 
    collect_item_statement:str, 
    interview_background:str, 
    model:str=DEFAULT_MODEL, 
    **custom_prompts
):
    ak = akasha.Doc_QA(
        model=model, 
        verbose=VERBOSE
    )
    prompts = {
        'prompt': dp.LIST_COLLECT_ITEMS_TASK['prompt'].format(),
        'system_prompt': dp.LIST_COLLECT_ITEMS_TASK['system_prompt'].format(),
    }
    prompts = _modify_prompts(
        prompts, 
        'list_collect_item_prompts', 
        modify_types=['prompt', 'system_prompt'], 
        **custom_prompts
    )
    collect_items_comma_split_str = ak.ask_self(
        prompt=prompts['prompt'],
        info=collect_item_statement,
        system_prompt=prompts['system_prompt'],
    )    
    print(f'輸出的項目為:{collect_items_comma_split_str}')
    collect_items = collect_items_comma_split_str.split(',')
    
    collect_items_string = "\n".join([f"{i+1}. {c}" for i, c in enumerate(collect_items)])
    consecutive_invalid_reply_tolerance = 1
    end_dialogue_limit = 2
    ak = akasha.Doc_QA(
        model=model, 
        verbose=VERBOSE
    )
    prompts = {
        'prompt':dp.GENERATE_COLLECT_REPLY_TASK['prompt'].format(
            interview_background=interview_background,
            collect_items=collect_items,
        ),
        'system_prompt':dp.GENERATE_COLLECT_REPLY_TASK['system_prompt'].format(
            collect_items_string=collect_items_string,
            end_dialogue_limit=end_dialogue_limit,
            consecutive_invalid_reply_tolerance=consecutive_invalid_reply_tolerance, 
        )
    }
    prompts = _modify_prompts(
        prompts, 
        'reply_prompts', 
        modify_types=['prompt', 'system_prompt'], 
        **custom_prompts
    )
    reply = ak.ask_self(
        prompt=prompts['prompt'],
        info=str(dialogue_history),
        system_prompt=prompts['system_prompt']
    )
    return reply     
#%% Tools
db_query_tool = akasha.create_tool(
    tool_name='db_query_tool',
    tool_description='''
    This is the tool to answer question based on database query, the parameters are: 
    1. question: str, the question asked by the user, required
    2. table_name: str, the table name to query, required
    3. column_description_json: str, the path of json file which contains description of each columns in the table, 
       or the json string of the description for each column, eg. {"column1": "description1", "column2": "description2"}
       optional, default is None
    4. simplified_answer: bool, whether to simplify the answer, optional, default is False
    5. connection_config: Dict[str, str], the connection configuration of the database 
       including keys such as:(sql_type, database, user, password, host and port), 
       optional, default is {}\n''' + f'''
    6. model: str, the model to use for answering, optional, default is '{DEFAULT_MODEL}' 
    ---
    Please try to find the parameters when using this tool, required parameters must be found, optional parameters can be ignored and use default value if not found.
    the "question" MUST BE THE SAME through the whole process.
    ''',
    func=db_query_func
)

# db_data_tool = akasha.create_tool(
#     tool_name='db_data_tool',
#     tool_description='''
#     This is the tool to retrieve corresponding data based on user question, the parameters are: 
#     1. question: str, the question asked by the user, required
#     2. table_name: str, the table name to query, required
#     3. column_description_json: str, the path of json file which contains description of each columns in the table, 
#        or the json string of the description for each column, eg. {"column1": "description1", "column2": "description2"}
#        optional, default is None
#     4. connection_config: Dict[str, str], the connection configuration of the database 
#        including keys such as:(sql_type, database, user, password, host and port), 
#        optional, default is {}\n''' + f'''
#     5. model: str, the model to use for generating sql statement, optional, default is '{DEFAULT_MODEL}' 
#     ---
#     Please try to find the parameters when using this tool, required parameters must be found, optional parameters can be ignored and use default value if not found.
#     the "question" MUST BE THE SAME through the whole process.
#     ''',
#     func=db_data_func
# )

webpage_summary_tool = akasha.create_tool(
    tool_name='webpage_summary_tool',
    tool_description=f'''
    This is the tool to summary article crawled from a webpage, the parameters are: 
    1. url: str, the url of the webpage, required
    2. summary_len: str, the length of summary, optional, default is 100
    3. extract_topics: List[str], the key topics to extract, 
       eg. ["topic1", "topic2"], optional, default is []
    4. list_result: bool, whether to list the summarized result, optional, default is True
    5. model: str, the model to use for summarizing, optional, default is '{DEFAULT_MODEL}'
    ---
    Please try to find the parameters when using this tool, required parameters must be found, optional parameters can be ignored and use default value if not found.
    ''',
    func=webpage_summary_func
)

collect_dialogue_info_tool = akasha.create_tool(
    tool_name='webpage_summary_tool',
    tool_description=f'''
    This is the tool to collect information of assigned items from user through dialogue, the parameters are: 
    1. dialogue_history: str, the (previous) dialogue history from user and service-desk, required
    2. collect_item_statement: str, the target items to collect from user, required
    3. interview_background: str, the background of the interview, required
    4. model: str, the model to use for dialogue, optional, default is '{DEFAULT_MODEL}'
    ---
    Please try to find the parameters when using this tool, required parameters must be found, optional parameters can be ignored and use default value if not found.
    ''',
    func=collect_dialogue_info_func
)

#%% main
if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
    # # FUNCTION TEST
    ## DB QUERY
    question = '請問user_1在5/1用電量最多及最少的電器分別是誰?'
    table_name = 'daily_result_bth'
    column_description_json = '''{
        "user_id": "用戶帳號",
        "report_time": "數據統計日期",
        "kwh": "總用電度數，包含其他電器",
        "appliance_kwh": "各電器用電占比，為string，值內以逗號分隔依序為電視, 冰箱, 冷氣, 開飲機, 洗衣機"
    }'''
    connection_config = set_connection_config(
        sql_type='SQLITE', 
        database='database.db', 
        user='', 
        password='', 
        host='', 
        port=''
    )
    print(db_query_func(
            question, 
            table_name, 
            column_description_json, 
            simplified_answer=True, 
            connection_config=connection_config
        )
    )
    
    # ## SUMMARY
    # summarized_result = webpage_summary_func(url='https://www.ptt.cc/bbs/Tech_Job/M.1719665577.A.A92.html')
    # print(summarized_result)
    
    # ## DIALOGUE
    # reply = collect_dialogue_info_func(dialogue_history='''
    #                                    由於我們系統回報您的用電量異常升高，我們想了解一下您最近有開關哪些電器呢？'\n 
    #                                    我開了冷氣\n
    #                                    瞭解，您最近有開冷氣。請問您開冷氣的原因是什麼呢？\n
    #                                    天氣很熱\n
    #                                    請問除了冷氣以外，您還有開啟其他電器嗎？\n
    #                                    沒有\n
    #                                    ''', 
    #                                    collect_item_statement='想要蒐集使用者操作哪些電器，操作是開還是關，以及其背後的原因', 
    #                                    interview_background='系統回報用電量異常升高')
    # print(reply)
    
    # # AGENT TEST
    # ag = akasha.test_agent(verbose=VERBOSE,
    #                        tools=[
    #                            collect_dialogue_info_tool,
    #                            db_query_tool,
    #                            webpage_summary_tool,
    #                         ],
    #                        model=DEFAULT_MODEL,
    #                        # system_prompt='請勿重複',
    #                     )
    # questions = ['請告訴我網站 "https://www.ptt.cc/bbs/Tech_Job/M.1719665577.A.A92.html" 的重點',
    #              '''
    #              我要查詢一個"SQLITE"資料庫 名為 "database.db", 裡面有一個table="daily_result_bth",
    #              欄位意義說明如下:
    #              ---
    #              1. user_id: 用戶帳號,
    #              2. report_time": 數據統計日期,
    #              3. kwh: 總用電度數，包含其他電器,
    #              4. appliance_kwh: 各電器用電占比，為string，值內以逗號分隔依序為電視, 冰箱, 冷氣, 開飲機, 洗衣機
    #              ---
    #              請問user_1在5/1用電量最多及最少的電器分別是誰?
    #              ''',
    #              '我收到來自異常偵測模型的警示，發現使用者用電量異常升高，因此想要透過對話蒐集使用者操作哪些電器，操作是開還是關，以及其背後的原因'
    #              ]
    # for idq, q in enumerate(questions):
    #     print(f'原始問題：{q}\n---\n回答：{ag(q, messages=[])}\n\n')