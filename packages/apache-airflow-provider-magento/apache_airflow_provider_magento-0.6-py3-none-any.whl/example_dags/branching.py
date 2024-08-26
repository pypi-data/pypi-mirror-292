from airflow import DAG
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.utils.dates import days_ago
from apache_airflow_provider_magento.operators.rest import MagentoRestOperator

def check_customer_exists(email: str, **kwargs) -> bool:
    op = MagentoRestOperator(
        task_id='check_customer_exists_op',
        endpoint=f'customers/search?searchCriteria[filterGroups][0][filters][0][field]=email&searchCriteria[filterGroups][0][filters][0][value]={email}',
        method='GET'
    )
    response = op.execute(context=kwargs)
    # Debugging print
    print(f"check_customer_exists response: {response}")
    return len(response.get('items', [])) > 0

def generate_customer_token(email: str, password: str, **kwargs) -> str:
    op = MagentoRestOperator(
        task_id='generate_customer_token_op',
        endpoint='integration/customer/token',
        method='POST',
        data={
            'username': email,
            'password': password
        }
    )
    response = op.execute(context=kwargs)
    print(f"generate_customer_token response: {response}")  # Debugging print
    return response  # Customer OAuth token

def create_customer(email: str, password: str, **kwargs) -> str:
    op = MagentoRestOperator(
        task_id='create_customer_op',
        endpoint='customers',
        method='POST',
        data={
            "customer": {
                "email": email,
                "firstname": "John",
                "lastname": "Doe",
                "website_id": 1,
                "store_id": 1,
                "group_id": 1
            },
            "password": password
        }
    )
    response = op.execute(context=kwargs)
    print(f"create_customer response: {response}")  # Debugging print
    return response.get('id')

def choose_path(**kwargs):
    ti = kwargs['ti']
    customer_exists = ti.xcom_pull(task_ids='check_customer_exists_op')
    print(f"choose_path decision based on customer_exists: {customer_exists}")  # Debugging print
    if customer_exists:
        return 'generate_customer_token_task'
    return 'create_customer_task'

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'retries': 1,
}

with DAG(
    'customer_management_dag',
    default_args=default_args,
    description='A DAG to manage customer creation and token generation',
    schedule_interval=None,
    catchup=False,
) as dag:

    check_customer_exists_task = PythonOperator(
        task_id='check_customer_exists_op',
        python_callable=check_customer_exists,
        op_args=['customer@example.com'],
    )

    branch_task = BranchPythonOperator(
        task_id='branch_task',
        python_callable=choose_path,
        provide_context=True
    )

    create_customer_task = PythonOperator(
        task_id='create_customer_task',
        python_callable=create_customer,
        op_args=['customer@example.com', 'Airflow@123'],
    )

    generate_customer_token_task = PythonOperator(
        task_id='generate_customer_token_task',
        python_callable=generate_customer_token,
        op_args=['customer@example.com', 'Airflow@123'],
    )

    check_customer_exists_task >> branch_task
    branch_task >> [generate_customer_token_task, create_customer_task]
    

