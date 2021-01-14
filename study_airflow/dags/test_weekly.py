import logging
from datetime import datetime
from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator

log = logging.getLogger(__name__)

local_tz = pendulum.timezone("Asia/Seoul")

# dag init
default_args = {
    'owner': 'wonji',
    'start_date': datetime(2021, 1, 1),
    'depends_on_past': True,
    'retries': 3,
    'retry_delay': timedelta(minutes=2),
}

dag_id = 'test_weekly'
dag = DAG(
    dag_id,
    default_args=default_args,
    catchup=False,
    schedule_interval='30 0 * * 1'
)


def print_hello(**kwargs):
    print("execution_date: " + str(kwargs["execution_date"]))
    local_exec_date = local_tz.convert(kwargs["execution_date"])

    print("type of execution_date" + str(type(kwargs["execution_date"])))
    print("execution_date(local_tz):" + str(local_exec_date))

    print("ds: " + str(kwargs['ds']))
    print("ds(local_tz):" + str(local_exec_date.date()))

    print("yesterday_ds: " + str(kwargs['yesterday_ds']))
    print("yesterday_ds(local_tz):" +
          str(local_exec_date.date() + timedelta(days=-1)))

    print("tomorrow_ds: " + str(kwargs['tomorrow_ds']))
    print("tomorrow_ds(local_tz):" +
          str(local_exec_date.date() + timedelta(days=1)))

    print("ds_nodash: " + str(kwargs['ds_nodash']))
    print("ds_nodash(local_tz): " + local_exec_date.date().strftime("%Y%m%d"))
    print("yesterday_ds_nodasy(local_tz):" +
          (local_exec_date.date() + timedelta(days=-1)).strftime("%Y%m%d"))

    return 'Hello world!'


# task init
dummy_task = DummyOperator(task_id='dummy_task1', retries=0, dag=dag)
hello_operator = PythonOperator(task_id='hello_task',
                                python_callable=print_hello,
                                provide_context=True,
                                params={'type': 'aa'},
                                dag=dag)

dummy_task >> hello_operator