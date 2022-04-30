docker.cleanup:
	docker rm $(docker ps -aq)

