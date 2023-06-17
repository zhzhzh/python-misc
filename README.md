# python-misc

python misc code, able to run in docker and local.

Python Version: 3.11

```bash
# crate the environment in local
conda create -n python-misc python=3.11

# activate the environment
conda activate python-misc

# deactivate the environment
conda deactivate
```

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
docker exec python-misc python LearnSQLALchemy/0_check_version.py
```
