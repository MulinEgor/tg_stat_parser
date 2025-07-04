build-exe:
	docker build --tag tg-start-parser .
	docker run -d --name tg-start-parser tg-start-parser
	docker cp tg-start-parser:/app/dist/main ./dist/main
	docker rm -f tg-start-parser
