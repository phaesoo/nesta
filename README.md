# Regista


# Core concepts

- Scalable
- Asynchronous


# Check list

- [x] Remote task call with Celery
- [x] Terminate running task with Celery (revoke, terminate=True)
- [x] Worker heartbeat, app.control.ping()
- [x] DB scheme (not with ORM, with mysql)
- [x] queue with RabbitMQ
- [ ] Server as a daemon

# Server

- Send task
- Update result

# DB

- It better not to use ORM but SQL..

Undecided

- Worker heartbeat(ping)