## Как запустить

```bash
docker compose up --build
# в отдельном терминале — наполнить справочники (movement_type и demo-данные)
docker compose exec api python -m app.seed
```


Сервис — `http://localhost:8000`, документация — `http://localhost:8000/docs`.


