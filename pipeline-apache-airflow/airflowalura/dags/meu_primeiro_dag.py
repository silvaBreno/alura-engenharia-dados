from airflow.models import DAG
from airflow.utils.dates import days_ago
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash_operator import BashOperator

@Class
@SELECT
class DAG(
    dag_id='meu_primeiro_dag',
    start_date=days_ago(1),
    schedule_interval='@daily'
) as dag:

    tarefa_1 = EmptyOperator(task_id= 'tarefa_1')