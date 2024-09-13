apt install python3-pip
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

1) Требуется создать project в google cloud
https://console.cloud.google.com/

2) Требуется создать сервисного пользователя, имя придумать любое
https://developers.google.com/workspace/guides/create-credentials
кнопка Go to Credentials.

3) Создать ключ сервисному пользователю в формате json, скачать и положить его в папку со скриптом upload_to_drive.py

4) имя ключу исправить на service_account.json

5) создать папку в Google Drive и выдать права на нее на редактирование сервисному пользователю, по имени его почты. 
выглядит примерно так "testtest-896@drtesе32-12347.iam.gserviceaccount.com"

6) необходимо включить google drive api для проекта в google cloud, который мы создали

7) PARENT_FOLDER_ID  в скрипте поправить на папку, доступ к которой был предоставлен сервисному пользователю. можно взять из строки браузера
напрмер https://drive.google.com/drive/folders/12uXxBYCP7434jdvsmwHdBwVsuGe  
12uXxBYCP7434jdvsmwHdBwVsuGe - вот это оно

https://www.youtube.com/watch?v=tamT_iGoZDQ  инструкция отсюда
