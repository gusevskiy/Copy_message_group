# Copy_message_group
Бот копирует все новые сообщения из группы и пересылает в (куда захотите)
реализована работа с massage_group_id для обьеденения альбомов.

## Установка для теста
1) копируем код
    ```bash
    mkdir project
    'open in gitbash dir project'
    git clone git@github.com:gusevskiy/Copy_message_group.git
    python3 -m venv venv
    pip install -r requirements.txt 
    ```
2) нужен клиент телеграмм  
    [инструкция здесь](https://telegramplayground.github.io/pyrogram/start/auth.html)

3) Создаем и заполняем файл `.env`
    ```bash
    FILESESSION=name
    DONOR=-1111111111111
    RECIPIENT=-222222222222222
    ```
4) запускаем  
    ```bash
    python3 main.py
    ```

#### Важно: вы должны быть подписаны/добавлены на группу или канал DONOR

## На сервере
#### Сервер конечно готовим под Docker инструкция [сдесь](https://docs.docker.com/engine/install/ubuntu/)
1) Заполнить переменные окружения Docker-compose.yml

    ```bash
    environment:
      DONOR: 1111111111111
      RECIPIENT: 2222222222222
      FILESESSION: "name"
    ```
2) отправляем все файлы на сервер 
    ```bash
    rsync -av -e "ssh -p 46567" ./ root@11.111.111.11:/root/name_dir
    ```
3) команды Docker compose подробнее [здесь](https://docs.docker.com/reference/cli/docker/compose/)
    ```bash
    docker compose up --build -d  # Собираем 
    Docker ps  # смотрим что все запущено
    # посмотреть логи
    docker volume ls
    docker volume inspect name_volume
    # далее переходим в папку указаную по пути "Mountpoint"
    ```
#### Важно:
Минимальные шаги по защите сервера.
* изменить порт ssh с 22 на любой другой
* ограничить доступ к файлу .session `shmod 600 name.session`
* отлючить ping
* отключить все порты на уровне файрвола кроме указаного для ssh

