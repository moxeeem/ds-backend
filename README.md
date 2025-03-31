# Домашнее задание к семинару "Основы backend-разработки"

## Инструкция по запуску
#### Собрать проект на виртуалке
1. зайти на виртуалку и склонировать на нее склонировать этот репозиторий
2. выполнить команду `docker build -t ds-backend .`
3. запустить сервис командой `./run.sh`

#### Тестирование

1. Получить номер
```
curl -s http://localhost:8080/read_plate/10022 | jq
```
2. Получить несколько номеров
```
curl -s -X POST -H "Content-Type: application/json" -d '{"image_ids": [10022, 9965]}' http://localhost:8080/batch_read_plates | jq
```
3. Невалидный URL
```
curl http://localhost:8080/read_plate/abc
```
4. Невалидная картинка
```
curl http://localhost:8080/read_plate/99999
```
5. Параллельное выполнение
```
curl -s http://localhost:8080/read_plate/10022 | jq & curl -s http://localhost:8080/read_plate/9965 | jq
```