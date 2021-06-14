import logging
from datetime import datetime
from datetime import timedelta
import os
import pendulum
from airflow import DAG
from airflow.providers.amazon.aws.operators.ec2_stop_instance import EC2StopInstanceOperator
from airflow.providers.amazon.aws.operators.ec2_start_instance import EC2StartInstanceOperator
from airflow.contrib.operators.ecs_operator import ECSOperator
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

dag = DAG(
    dag_id='test_ecs',
    default_args=default_args,
    catchup=False,
    schedule_interval='30 0 * * 1'
)

# task init
dummy_task = DummyOperator(task_id='dummy_task1', retries=0, dag=dag)

hello_world = ECSOperator(  # https://airflow.apache.org/docs/apache-airflow/1.10.5/_api/airflow/contrib/operators/ecs_operator/index.html
    task_id="hello_world",
    dag=dag,
    aws_conn_id="aws_ecs",
    cluster="c",
    task_definition="hello-world",
    launch_type="EC2",  # 'EC2' or 'FARGATE'
    overrides={
        "containerOverrides": [
            {
                "name": "hello-world-container",
                "command": ["echo", "hello", "world"],
            },
        ],
    },
    network_configuration={
        "awsvpcConfiguration": {
            "securityGroups": ['sg-07511349f5dd09086'],
            "subnets": ['subnet-ccd7f880'],
        },
    }
)

dummy_task >> hello_world
