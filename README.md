# python-misc

python misc code, able to run in docker and local

## How to build & run

```Bash
# build & start container (docker-compose.yml)
docker-compose up -d --build
# docker-compose -f docker-compose.yml up -d --build
```

### cleanup none images

```Bash
docker rmi $(docker images -f "dangling=true" -q)
```

## How to execute the python module with docker

for example to execute `hello.py` under module `Hello`

```bash
docker exec python-misc python Hello/hello.py

# more examples:
docker exec python-misc python LearnSQLALchemy/check_version.py
```
