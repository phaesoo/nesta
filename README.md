# Nesta


# Core concepts

- Scalable
- Asynchronous


# Todolist

- [x] Remote task call with Celery
- [x] Terminate running task with Celery (revoke, terminate=True)
- [x] Worker heartbeat, app.control.ping()
- [x] DB scheme (not with ORM, with mysql)
- [x] queue with RabbitMQ
- [x] Daemonize server process
- [x] Logging
- [ ] Testing
- [ ] Notification (email.. etc)
- [ ] External controller (telegram)
- [ ] Task reponse object
- [ ] Add region column on job db
- [ ] Exchange trading date information from external library
- [ ] Prepare for safe insert logic (schedule insert command)

# Server

- Send task
- Update result

# DB

- It better not to use ORM but SQL..

Undecided

- Worker heartbeat(ping)

# Setup

RabbitMQ (docker)
- sudo docker run -d --name rabbitmq -p 5672:5672 -p 8080:15672 --restart=unless-stopped -e RABBITMQ_DEFAULT_USER=test -e RABBITMQ_DEFAULT_PASS=test rabbitmq:management


# Note

- rsync -rvz ./ --include=*.py  --exclude=.venv/ --exclude=.git/ --exclude=*.log --exclude=*.pid hspark@aws_test:/usr/local/bin/nesta/