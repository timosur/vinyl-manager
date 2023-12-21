# Run alembic migrations in docker backgend container

```bash
docker compose exec vinyl-backend alembic upgrade head
```

# Auto generate new migrations in docker backend container

```bash
docker compose exec vinyl-backend alembic revision --autogenerate -m "migration message"
```