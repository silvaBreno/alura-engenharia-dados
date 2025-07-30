import pendulum
from airflow.models import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.decorators import task

with DAG(
    dag_id='atividade_aula_4',
    start_date=pendulum.today('UTC').add(days=-1),
    schedule_interval='@daily'
) as dag:

    tarefa_1 = EmptyOperator(task_id = 'tarefa_1')
    tarefa_2 = EmptyOperator(task_id = 'tarefa_2')
    tarefa_3 = EmptyOperator(task_id = 'tarefa_3')

    @task(task_id = 'cumprimentos')
    def cumprimentos():
            print("Boas-vindas ao Airflow!")

    cumprimentos_task = cumprimentos()

    tarefa_1 >> tarefa_2 >> tarefa_3 >> cumprimentos_task
