# minibase
a small base package for full-stack development with python

the general goal of this package is to contain utils for my full-stack projects with python.
currently, it contains a nice and minimal pythonic wrapper around the MySQL package to remove
unnessesary boilerplate.

the package opens up a couple general classes for usage.

`Database` the main database wrapper
```python
db = Database({
    "host": ...,
    "user": ...,
    "password": ...,
    ... args to be fed into MySQLConnectionPool ...
})
tables = db.connect()
db.create(tables.users, {
    "id": 0,
    "username": "admin",
    "email": "admin@email.com"
})
print(db.read(tables.users, uid = 0))
db.delete(tables.users, uid = 0)
```

`DotDict` a stupidly simple read-only dot dict 
```python
session = DotDict({
    "session": 0,
    "colors": "dark"
})
print(session.colors)
print(session.colors)
```

honestly, you would be better off writing your own, but this is here just in case anyone else
wants to develop quick projects. consider it like the `Gallopsled/pwntools` of hackathons rather than
CTF problems.
