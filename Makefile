.PHONY: InitMariaDB

#Temporary Makes

tempstart:
	@echo "Starting Dev Env"
	@sudo docker start ubuntudev
	@echo "Starting MariaDB"
	@sudo docker start mariadb
	@echo "Starting JupyterLab"
	-@sudo docker exec -i -u root ubuntudev jupyter lab 

tempstop:
	@echo "Stopping everything."
	@sudo docker stop ubuntudev
	@sudo docker stop mariadb	

#Temporary Makes

ExecutableBash:
	@echo "Marking Bash Scripts in Bash SubFolder as Executable..."
	@find Bash -type f -name '*.sh' -exec sudo chmod +x {} + && \
		echo "Done Marking Bash Scripts as Executable." || \
		echo "There was a Problem with Marking Bash Scripts as Executable."

FillEnvFile:
	@./Bash/MariaDBContainerIPPort.sh

SetupMariaContainer:
	@./Bash/SetupMariaContainer.sh

BackfillMariaDB:
	@python3 ./Scripts/backfillmariadb.py


