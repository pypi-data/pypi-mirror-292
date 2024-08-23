# Odeta

A simple NoSQL-like interface for SQLite.

## Installation

```bash
pip install odeta
```

## Usages
### Importing the Library

```
from odeta import database
```

Initializing the Database and create a table in it.

```
db = database("my_database.db")
users = db("users")
```

## Fetching Data
### Fetch all records from the table:

```
print(users.fetch())
```

### Fetch records that match a specific query:

```
print(users.fetch({"name": "Bob Johnson"}))

print(users.fetch({"name?contains": "Bob"}))

# for all the records with OR condition
print(users.fetchall({"name?contains": "Bob", "age" : 30}))

# for all the records with AND condition
print(users.fetch({"name?contains": "Bob", "age" : 30}))
```

# Inserting Data
## Insert a new record into the table:
```
new_user_id = users.put({"name": "Alice Smith", "age": 30})
print(new_user_id)
```

## Updating Data

### Update an existing record in the table:
```
users.update({"name": "Alice Johnson", "age": 31}, new_user_id)
```

## Deleting Data
### Delete a record from the table:
```
users.delete(new_user_id)
```
