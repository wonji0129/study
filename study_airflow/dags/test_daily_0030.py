import logging
from datetime import datetime
from datetime import timedelta
from airflow.operators.python_operator import PythonOperator, ShortCircuitOperator, BranchPythonOperator
from airflow.sensors.external_task_sensor import ExternalTaskSensor
from airflow.operators.dummy_operator import DummyOperator
from airflow.exceptions import AirflowException
import pendulum
from airflow import DAG
import pendulum
from datetime import datetime, timedelta
import json

log = logging.getLogger(__name__)

local_tz = pendulum.timezone("Asia/Seoul")

# dag init
default_args = {
    'owner': 'wonji',
    'start_date': datetime(2021, 1, 6),
    'depends_on_past': True,
    'email': ['wonji0129@naver.com'],
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
}

dag_id = 'test_daily_0030'
dag = DAG(
    dag_id,
    default_args=default_args,
    # 로컬타임 기준 매일 00시 30분, 1월 13일엔 11일(UTC+0) 기준으로 돌게됨
    schedule_interval='30 00 * * *',
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


def branch_monthly(dt, fm='%Y%m%d'):
    date = datetime.strptime(dt, fm)
    if (date + timedelta(days=1)).day == 1:  # 월 말일 (매월 1일 배치)
        return 'wait_monthly'
    else:
        return 'mid'


def branch_weekly(dt, fm='%Y%m%d'):
    date = datetime.strptime(dt, fm)
    if date.weekday() == 6:  # 매주 일요일 (매주 월요일 배치)
        return 'wait_weekly'
    else:
        return 'mid'


# task init
start = DummyOperator(task_id='start', dag=dag)
check_weekly = BranchPythonOperator(
    task_id='check_weekly',
    python_callable=branch_weekly,
    op_kwargs={'dt': "{{ next_ds_nodash }}"},                            
    dag=dag
)
check_monthly = BranchPythonOperator(
    task_id='check_monthly',
    python_callable=branch_monthly,
    op_kwargs={'dt': "{{ next_ds_nodash }}"},                            
    dag=dag
)

wait_daily = ExternalTaskSensor(
    task_id='wait_daily',
    external_dag_id='test_daily_0015',
    external_task_id='hello_task', 
    execution_delta=timedelta(minutes=15),
    check_existence=True,
    dag=dag
)

wait_weekly = ExternalTaskSensor(
    task_id='wait_weekly',
    external_dag_id='test_weekly',
    external_task_id='hello_task', 
    check_existence=True,
    dag=dag
)

wait_monthly = ExternalTaskSensor(
    task_id='wait_monthly',
    external_dag_id='test_monthly',
    external_task_id='hello_task', 
    check_existence=True,
    dag=dag
)

mid = DummyOperator(task_id='mid', trigger_rule='none_failed_or_skipped', dag=dag)

hello_operator = PythonOperator(task_id='hello_task',
                                python_callable=print_hello,
                                provide_context=True,
                                params={'type': 'aa'},
                                dag=dag)


start >> [wait_daily, check_weekly, check_monthly]

check_monthly >> wait_monthly >> mid 
check_monthly >> mid
check_weekly >> wait_weekly >> mid
check_weekly >> mid

wait_daily >> mid >> hello_operator
