import logging
from datetime import datetime
from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator

log = logging.getLogger(__name__)

local_tz = pendulum.timezone("Asia/Seoul")

def return_list(**kwargs):
    return ['a', 'b']

# dag init
default_args = {
    'owner': 'wonji',
    'start_date': datetime(2021, 1, 1),
    'depends_on_past': True,
    'retries': 3,
    'retry_delay': timedelta(minutes=2),
}

dag = DAG(
    dag_id='test_daily_0015',
    default_args=default_args,
    catchup=False,
    schedule_interval='30 0 * * 1'
)

# task init
dummy_task = DummyOperator(task_id='dummy_task1', retries=0, dag=dag)
return_list = PythonOperator(
    task_id='return_list',
    python_callable=return_list,
    dag=dag
    )

print_xcom = BashOperator(
    task_id='print_xcom',
    bash_command="echo {{ task_instance.xcom_pull(task_ids='return_list') }}",
    dag=dag
    )

dummy_task >> return_list >> print_xcom

