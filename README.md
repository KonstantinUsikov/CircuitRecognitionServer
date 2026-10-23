# DiplomaServer

Серверная часть дипломного проекта по распознаванию компонентов на электрических схемах.

Сервер принимает схему (PDF или изображение), находит на ней компоненты, классифицирует их нейросетью, а компоненты, которые распознать не удалось, группирует в кластеры похожих по внешнему виду элементов.

## Архитектура

Проект состоит из трёх FastAPI-сервисов и фонового обработчика. Все они запускаются одной командой через `launch_all.py`.

| Сервис | Порт | Модуль | Назначение |
|---|---|---|---|
| database | 8000 | `database_module/api.py` | Работа с PostgreSQL (peewee): схемы, распознанные и нераспознанные компоненты, кластеры |
| predict | 8001 | `predict_module/api.py` | Поиск компонентов на схеме (OpenCV + EasyOCR для удаления текста) и их классификация CNN-моделью на Keras |
| cluster | 8002 | `cluster_module/api.py` | Извлечение признаков нераспознанных компонентов (ViT DINO) и кластеризация HDBSCAN |
| feature loop | — | `cluster_module/feature_client.py` | Фоновый цикл, который заранее считает признаки для новых нераспознанных компонентов |

Сервисы общаются между собой по HTTP. Адреса и порты задаются в `settings.py`.

```
клиент ──► predict ──► database ──► PostgreSQL
клиент ──► cluster ──► database
feature loop ──────► database
```

### Распознавание (`predict_module`)

1. Схема приходит в виде data URL (`data:application/pdf;base64,...` или изображение). У PDF обрабатывается только первая страница.
2. Если такая схема уже была загружена, старая запись удаляется вместе с её компонентами.
3. `unknown_search/` удаляет текст и линии соединений, затем находит прямоугольники компонентов.
4. `prediction/predict_lib.py` классифицирует вырезанные фрагменты моделью `prediction/Models/best_8_876.h5` (вход 64×64, оттенки серого). Классы: `Unknown`, `ACB_1`, `ACB_2`, `KM_1`, `SW`, `SW_2`, `ACB_MO1`, `ACB_PC1`.
5. Компоненты класса `Unknown` сохраняются как нераспознанные, остальные — как распознанные с уверенностью модели.

### Кластеризация (`cluster_module`)

1. Для каждого нераспознанного компонента считается вектор признаков моделью `vit_base_patch16_224.dino` (timm). Признаки сохраняются в БД, чтобы не считать их повторно.
2. Векторы нормализуются (`StandardScaler`) и кластеризуются HDBSCAN (`min_cluster_size=10`).
3. Старые кластеры удаляются и создаются заново. Если все компоненты уже распределены по кластерам, пересчёт не выполняется.

Фоновый цикл `run_feature_loop` берёт из БД до 20 компонентов без признаков за раз и считает их признаки. Если таких компонентов нет, он ждёт 10 секунд.

## Структура проекта

```
DiplomaServer/
├── launch_all.py          # запуск всех сервисов и фонового цикла
├── settings.py            # хосты и порты сервисов
├── docker-compose.yml     # PostgreSQL
├── pyproject.toml         # зависимости (Poetry)
├── test.py                # ручная проверка predict и cluster
├── database_module/
│   ├── api.py             # FastAPI-приложение сервиса БД
│   ├── apis/              # роутеры: circuit, component, cluster
│   ├── repositories/      # запросы к БД
│   └── database/          # подключение, таблицы, создание/удаление таблиц
├── predict_module/
│   ├── api.py             # FastAPI-приложение сервиса распознавания
│   ├── prediction/        # классификатор и веса модели
│   └── unknown_search/    # поиск компонентов на изображении
└── cluster_module/
    ├── api.py             # FastAPI-приложение сервиса кластеризации
    ├── cluster_lib.py     # извлечение признаков и HDBSCAN
    └── feature_client.py  # фоновый расчёт признаков
```

## Требования

- Python 3.12.7 (версия зафиксирована в `pyproject.toml`)
- [Poetry](https://python-poetry.org/)
- Docker и Docker Compose (для PostgreSQL)

Зависимости довольно тяжёлые (PyTorch, TensorFlow, EasyOCR). При первом запуске будут скачаны веса EasyOCR и модели DINO, поэтому нужен доступ в интернет.

## Установка и запуск

1. Запустить PostgreSQL:

   ```bash
   docker compose up -d
   ```

   База `diploma_db` будет доступна на `localhost:15432` (пользователь `postgres`, пароль `password`). Эти же параметры указаны в `database_module/database/core.py`.

2. Установить зависимости:

   ```bash
   poetry install
   ```

3. Создать таблицы (автоматически они не создаются):

   ```bash
   poetry run python -m database_module.database.create
   ```

4. Запустить все сервисы:

   ```bash
   poetry run python launch_all.py
   ```

   Каждый сервис можно запустить и отдельно:

   ```bash
   poetry run python -m database_module.api
   poetry run python -m predict_module.api
   poetry run python -m cluster_module.api
   poetry run python -m cluster_module.feature_client
   ```

   Сервисы predict и cluster обращаются к сервису database, поэтому он должен быть запущен.

Swagger-документация доступна по адресам:

- http://localhost:8000/docs — database
- http://localhost:8001/docs — predict
- http://localhost:8002/docs — cluster

## API

### Распознавание схемы

`POST /api/predict/run_prediction` (порт 8001)

```json
{
  "circuit_data": "data:application/pdf;base64,JVBERi0xLjcK...",
  "config": {}
}
```

Поле `config` обязательно, но все его параметры имеют значения по умолчанию, поэтому можно передать пустой объект. Список параметров приведён в описании схемы `PredictRequest` в Swagger.

Пример запроса с PDF-файлом:

```bash
echo "{\"circuit_data\": \"data:application/pdf;base64,$(base64 -w0 scheme.pdf)\", \"config\": {}}" > request.json
curl -X POST http://localhost:8001/api/predict/run_prediction \
     -H "Content-Type: application/json" \
     -d @request.json
```

Ответ:

```json
{
  "circuit_id": 1,
  "circuit_image": "<base64>",
  "recognized_components": [
    {"id": 1, "x": 0.41, "y": 0.27, "w": 0.05, "h": 0.04, "image": "<base64>", "class_name": "SW", "confidence": 0.97}
  ],
  "unknown_components": [
    {"id": 1, "x": 0.63, "y": 0.52, "w": 0.06, "h": 0.03, "image": "<base64>"}
  ]
}
```

Координаты `x`, `y` — центр компонента, `w`, `h` — его размеры. Все значения указаны в долях от ширины и высоты изображения схемы.

### Кластеризация

`POST /api/cluster/run_clusterization` (порт 8002), без тела запроса.

Возвращает `clusters` (у каждого кластера есть `id`, `name`, `label` и список `components`) и `unclustered_components`.

### Сервис базы данных (порт 8000)

| Метод | Путь | Описание |
|---|---|---|
| GET | `/api/db/get_circuits` | Все схемы (уменьшенные изображения) |
| POST | `/api/db/get_circuits_by_image` | id схем с таким же изображением |
| POST | `/api/db/delete_circuits_by_image` | Удалить схемы с таким же изображением |
| POST | `/api/db/add_circuit_and_components` | Добавить схему и её компоненты |
| GET | `/api/db/get_components_by_circuit_id` | Компоненты схемы |
| GET | `/api/db/get_components_full_by_circuit_id` | Компоненты схемы с разбивкой по кластерам |
| POST | `/api/db/delete_components_by_circuit_id` | Удалить схему и её компоненты |
| GET | `/api/db/get_recognized_components` | Все распознанные компоненты |
| GET | `/api/db/get_unknown_components` | Все нераспознанные компоненты |
| GET | `/api/db/get_unknown_components_without_features` | Нераспознанные компоненты без признаков (`limit`) |
| PUT | `/api/db/update_unknown_components_features` | Сохранить признаки компонентов |
| POST | `/api/db/delete_unknown_components_by_ids` | Удалить нераспознанные компоненты по id |
| POST | `/api/db/delete_unknown_components_by_cluster_ids` | Удалить нераспознанные компоненты по id кластеров |
| GET | `/api/db/get_clusters` | Все кластеры и компоненты без кластера |
| GET | `/api/db/get_clusters_by_circuit_id` | Кластеры компонентов одной схемы |
| POST | `/api/db/recreate_clusters` | Пересоздать кластеры |

## Настройка

- `settings.py` — хосты и порты сервисов.
- `database_module/database/core.py` — параметры подключения к PostgreSQL.
- `predict_module/unknown_search/unknown_search_config.py` — параметры поиска компонентов. При запросе к API они передаются в поле `config`.
- `cluster_module/cluster_lib.py` — минимальный размер кластера (`MIN_CLUSTER_LENGTH`).
- `cluster_module/feature_client.py` — размер пачки (`LIMIT`) и пауза (`SLEEP_SECONDS`) фонового цикла.

Удалить все таблицы:

```bash
poetry run python -m database_module.database.drop
```

## Ручная проверка

В `test.py` есть функции для вызова распознавания и кластеризации на запущенном сервере. Перед использованием нужно заменить путь к PDF-файлу на свой.
