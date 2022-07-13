# cmp-vmware

* Build OpenStack instance and VMware host relationship.


## Build

```bash
docker-compose build
```


## Deploy and run

* 1) create `.env` file

```bash
DATABASE=cmpvmware
DB_USER=cmpvmware
DB_PASSWORD=notpassword
# DB_HOST=10.67.85.128
DB_PORT=3306

VC_HOST=10.209.1.254
VC_USER=yhcmp@yhcmpvc7-dev.local
VC_PASSWORD=m#ss9ttm2E
VC_DC=dc
```

* 2) Run `docker-compose.yml`

```bash
docker-compose up -d
```
