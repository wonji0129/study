import logging
from datetime import datetime
from datetime import timedelta
from airflow.operators.python_operator import PythonOperator
import pendulum
from airflow import DAG

log = logging.getLogger(__name__)

local_tz = pendulum.timezone("Asia/Seoul")

# dag init
default_args = {
    'owner': 'wonji',
    'start_date': datetime(2021, 1, 6),
    'depends_on_past': True,
    'email': ['wonji'],
    'retries': 3,
    'retry_delay': timedelta(minutes=2),
}

dag_id = 'test_daily_1530'
dag = DAG(
    dag_id,
    default_args=default_args,
    # 로컬타임 기준 매일 24시 30분, 1월 13일엔 12일(UTC+0) 기준으로 돌게됨
    schedule_interval='30 15 * * *',
    catchup=False
)


def print_hello(**kwargs):
    print(kwargs['params'])
    print("execution_date: " + str(kwargs["execution_date"]))
    local_exec_date = local_tz.convert(kwargs["execution_date"])
    print("execution_date(local_tz):" + str(local_exec_date))

    print("ds: " + str(kwargs['ds']))
    print("ds(local_tz):" + str(local_exec_date.date()))

    print("yesterday_ds: " + str(kwargs['yesterday_ds']))
    print("yesterday_ds(local_tz):" +
          str(local_exec_date.date() + timedelta(days=-1)))
    print("yesterday_ds_nodasy(local_tz):" +
          (local_exec_date.date() + timedelta(days=-1)).strftime("%Y%m%d"))

    print("tomorrow_ds: " + str(kwargs['tomorrow_ds']))
    print("tomorrow_ds(local_tz):" +
          str(local_exec_date.date() + timedelta(days=1)))

    print("ds_nodash: " + str(kwargs['ds_nodash']))
    print("ds_nodash(local_tz): " + local_exec_date.date().strftime("%Y%m%d"))

    return 'Hello world!'


# task init
hello_operator = PythonOperator(task_id='hello_task',
                                python_callable=print_hello,
                                provide_context=True,
                                params={'type': 'aa'},
                                dag=dag)
