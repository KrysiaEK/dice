# Dice

Repository with REST API for a game based on yahtzee. Two players roll five dice three times per round so that numbers on faces were in 
specified configurations. Each configuration have assigned a number of points. One game consists of 13 rounds, the 
goal is to score as many points as possible.

- players matching system,
- gameplay handling: dices rolling, record of the course of the game, points and extra points counting,  ranking scores counting,
- implementation of the user authorization system along with the tokenization and password validation,
- errors handling and custom permissions,
- unit tests,
- CI and CD pipline using GitHub Actions,

## Installation

### Deployment:
1.	Create docker-compose.yml file with the following contents in folder destined for this project:

```
version: "3.9"

services:
  db:
    image: postgres
    volumes:
      - ./data/db:/var/lib/postgresql/data
    env_file:
      - docker.env

  web:
    image: krysiaek/dice
    ports:
      - "8000:8000"
    env_file:
      - docker.env
    depends_on:
      - db
```

2.  Create file docker.env with the following content:
```
DJANGO_SECRET_KEY=random_value
POSTGRES_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
```
4. Run ```docker-compose pull```
5. Run test command to make sure everything is in order:
```docker-compose run web python manage.py test dice```
6. Start the server:
 ```docker-compose up```

The project works on port 8000.


### Development:
1. Clone repository
2. Run ```docker-compose build```
3. Run test command to make sure everything is in order:
```docker-compose run web python manage.py test dice```
4. Start the development server with command: ```docker-compose up```
