
all: rm build setconf setimagejs pkg rm

build:
	docker-compose build
	mkdir -p build/images
	docker save cmp-vmware:v1.0 -o build/images/cmp-vmware-v1.0.tar.gz

setconf:
	cp conf/cmpvmware.conf build/
	cp docker-compose.yml build/
	ln -s build/cmpvmware.conf build/.env 

setimagejs:
	echo "#!/bin/bash" > build/install.sh
	echo "docker load -i images/cmp-vmware-v1.0.tar.gz" >> build/install.sh
	chmod +x build/install.sh

pkg:
	tar -cvf build.tar.gz build

rm:
	rm -dRf build
