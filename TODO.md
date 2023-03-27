TODO
----

General
=======
- Implement a task queue (e.g. Celery, rq) for executing long running actions.
- Rate limiting of frequently triggered modules.
- Validate username to be alphanumeric (or at least close) only.
- Add checks for redirect safety.
- Robust logging support.
- Fault tolerance for server/client.
  - Client.
    - Pickle responder objects loaded by client.
      - Write to file?
      - Write to database?
    - Track last seen submission/comment.
    - Cache the last n number of seen submissions/comments.
    - Send heartbeat to server.
      - If server has not heard from client after x amount of time, relaunch client in recovery mode.
      - Send two initial heartbeats incase first heartbeat is lost.
    - Recovery.
      - Load all pickled responders.
      - Load all submissions/comments in the cache created after the timestamp of the last seen submission/comment.
      - Feed loaded submissions/comments to loaded responders.
      - Start normal program loop.
  - Server.
    - Send heartbeat to clients.
      - If clients have not heard from server after x amount of time, switch to backup server.
- Add tooltips to triggered items to display full content
- Use time.monotonic() instead of time.time()???

Triggers
========
- ML models
- Filter by flair
- Use Trigger/Rule notation instead of Trigger/Component notation???

Actions
=======
- Share post (crosspost?)
- Hooks for training ML models

Priority
========
- TESTS
- Restructure
  - Packages
    - "cli.py"
      - Setuptools entrypoints. Launch web app with built-in server (app.run) and engine.
        - roveit start (launch local server (app.run) and engine)
        - roveit engine (launch engine)
        - roveit web (launch local web server)
    - app
    - engine
- Add db migrations support (Alembic, Flask-Migrate)
- Change worker heartbeating to use PUB/SUB instead of PUSH/PULL
  - or set linger to 0???
- Broker publisher messages through manager instead of sending directly to workers
- Client side and server side form validation
- Anonymous module creation
