# KMG Parser

* Склонируйте репозиторий
```shell
$ git clone git@github.com:seidakhmet/kmg.git kmg
```

* Перейдите в склонированную директорию
```shell
$ cd ./kmg
```

* Запустите контейнер Postgresql
```shell
$ docker-compose up -d
```

* Перейдите в директорию с кодом
```shell
$ cd ./api
```

* Создайте изолированную среду Python и установите зависимости
```shell
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```


* Инициализируйте БД
```shell
$ python main.py -i
```

* Спарсите требуемые данные
```shell
$ python main.py -f path_to_file # Парсинг файла по пути
```

* Запустите API
```shell
$ uvicorn api:app --host 0.0.0.0 --port 8000
```

* Откройте в браузере адрес http://localhost:8000/
Документация API в swagger



### Аргументы парсера
```shell
$ python main.py -h # Помощь
$ python main.py -i # Инициализация БД (migration up)
$ python main.py --drop_database # Уничтожение базы (migration down)
$ python main.py -f path_to_file # Парсинг файла по пути
$ python main.py -d path_to_directory # Парсинг директории по пути
$ python main.py -u -f path_to_file # -u ключ обновляющий данные, которые уже существуют
```