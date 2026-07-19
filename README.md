## Как запустить

```bash
docker compose up -d --build
# в отдельном терминале — наполнить справочники (movement_type и demo-данные)
docker compose exec api python -m app.seed

sudo docker compose logs -f outbox-relay

```


Сервис — `http://localhost:8000`, документация — `http://localhost:8000/docs`.


