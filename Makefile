all: build

build:
	docker-compose up --build

test:
	env PYTHONPATH=. python3 tests/equipment_test.py

clean:
	docker rm -v `docker ps --filter status=exited -q 2>/dev/null` 2>/dev/null
	docker rmi `docker images --filter dangling=true -q 2>/dev/null` 2>/dev/null

clobber:
	@./clean_saves ./save
