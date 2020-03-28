all: build

build:
	docker-compose up --build

clean:
	@./clean_saves ./save
