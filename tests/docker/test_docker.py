import os


def test_rabbitmq_host_env_var():
    rabbitmq_host = os.getenv('RABBITMQ_HOST')
    assert rabbitmq_host == 'localhost', f'Expected RABBITMQ_HOST=localhost, but got {rabbitmq_host}'
