from filmapi.app import init_celery

app = init_celery()
app.conf.imports = app.conf.imports + ("filmapi.tasks.example", "filmapi.tasks.parser")
