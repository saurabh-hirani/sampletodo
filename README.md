### sampletodo

This is a sample python flask todo app. It builds on Miguel Grinberg's [post](https://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask) and [this serverless example](https://github.com/serverless/examples/tree/master/aws-node-rest-api-with-dynamodb)

#### Datastore

- This app uses DynamoDB as the backing store. 

#### Setup the local environment

- Install [pipenv](https://docs.pipenv.org/)

  ```
  # sudo pip install pipenv 
  ```

- Setup the local development environment

  ```
  # pipenv install -r requirements.txt 
  # pipenv shell 
  ```

- Run unit tests

  ```
  # SAMPLETODO_CONFIG_ENV=TestLocalRunConfig SAMPLETODO_TTY=True python setup.py test
  ```

#### Run the app locally without Docker

- Setup dynamodb locally - Follow this [post](http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html)

- In terminal 1 - Run dynamodb locally after following the above instructions.

  ```
  # java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar
  ```

- In terminal 2 - Start the flask app:

  ```
  # ./run_local_app.sh
  ```

- In terminal 3 - run the entire task lifecycle tests (delete table, create task, update task, search tasks, etc.)

  ```
  # ./run_lifecycle.sh
  ```
