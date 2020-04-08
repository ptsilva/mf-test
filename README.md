# MF - Test project

## setup
```$ git clone https://github.com/ptsilva/mf-test```

```$ cd mf-test```

## Starting development server
```$ docker-compose up```

## Starting production server
```$ docker-compose -d -f docker-compose.prod.yml up```

## Seeding database
#### production environment:
```$ docker-compose -f docker-compose.prod.yml run web python manage.py db_seed```
#### development environment
```$ docker-compose run web python manage.py db_seed```

## Client web
#### Production environment
<a href="http://localhost:1337/graphql">http://localhost:1337/graphql

#### Development environment
<a href="http://localhost:1337/graphql">http://localhost:5000/graphql

## Client Command line
```docker-compose run web python manage.py query "{ users (limit: 2) {id, name}}"```
```json
{
  "data": {
    "users": [
      {
        "id": "VXNlcjozMQ==",
        "name": "Jessica Watson"
      },
      {
        "id": "VXNlcjozMg==",
        "name": "Scott Sanchez"
      }
    ]
  }
}
``` 

## Running automated tests
```$ docker-compose run web python -m unittest```