from celery import Celery

app = Celery("tasks", broker="amqp://localhost")

app.conf.update(
    task_serializer="json",
    result_serializer="json",
)
