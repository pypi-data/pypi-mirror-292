# Pystacho ORM

## Setting up the model

```python
from pystacho.model import Model


class Person(Model):
    pass

```


## Find a record by its ID

Usage:
```python
person = Person.find(2)
print(person)
```

Result:
```text
<class 'models.person.Person'>
SQL--> SELECT * FROM people WHERE id = %s (2,)
Person({'id': 2, 'first_name': 'Paul Eduardo', 'last_name': 'Marclay', 'address': 'Mi address 1234'})
```

## Find a record by different field values

Usage:
```python
person = Person.find_by(id=2, first_name='Paul Eduardo')
```

Result:
```text
SQL-->  SELECT * FROM people WHERE id = %s AND first_name = %s [2, 'Paul Eduardo']
Person({'id': 2, 'first_name': 'Paul Eduardo', 'last_name': 'Marclay', 'address': 'Mi address 1234'})
```

## Creating a record

Usage:
```python
person = Person(first_name='John', last_name='Doe', address='Missing')
person.save()
```

Result:
```text
SQL-->  INSERT INTO people (first_name, last_name, address) VALUES (%s, %s, %s) ['John', 'Doe', 'Missing']
Person({'first_name': 'John', 'last_name': 'Doe', 'address': 'Missing'})
```

Another usage:
```python
person = Person()
person.first_name = 'Lars'
person.last_name = 'Ulrich'
person.address = 'No address'
person.save()
```

Result:
```text
SQL-->  INSERT INTO people (first_name, last_name, address) VALUES (%s, %s, %s) ['Lars', 'Ulrich', 'No address']
Person({'first_name': 'Lars', 'last_name': 'Ulrich', 'address': 'No address', 'id': 6})
```

And you could also do things like this:
```python
Person(first_name='Mike', last_name='Portnoy').save()
```

Result:
```text
SQL-->  INSERT INTO people (first_name, last_name) VALUES (%s, %s) ['Mike', 'Portnoy']
True
```

Another way to create a record and get it could be using `create()` on this way you don't need to to `save()`:
```python
Person.create(first_name='Jason', last_name='Newsted')
```

Result:
```text
SQL-->  INSERT INTO people (first_name, last_name) VALUES (%s, %s) ['Jason', 'Newsted']
Person({'first_name': 'Jason', 'last_name': 'Newsted', 'id': 8})
```

## Filtering
You can use multiple chained `where` clauses
```python
Person().where(first_name='Paul Eduardo').where(last_name='marclay')
```
Result:
```text
SQL-->  SELECT * FROM people WHERE first_name = %s AND last_name = %s ['Paul Eduardo', 'marclay']
Relation(results: [Person({'id': 2, 'first_name': 'Paul Eduardo', 'last_name': 'Marclay', 'address': 'P. del Castillo 480'})])
```

Even using `select` and `order` clauses mixed in
```python
Person.select('id, last_name').where(first_name='test').order(id='desc', last_name='asc')
```

Result:
```text
SQL-->  SELECT id, last_name FROM people WHERE first_name = %s ORDER BY id desc, last_name asc ['test']
Relation(results: [Person({'id': 10, 'last_name': 'test 2'}), Person({'id': 9, 'last_name': 'test 1'})])
```

If you need to check the results amount
```python
people = Person.select('id, last_name').where(first_name='test').order(id='desc', last_name='asc')
print(len(people))    
```
Result:
```text
SQL-->  SELECT id, last_name FROM people WHERE first_name = %s ORDER BY id desc, last_name asc ['test']
2
```
You could access to the first and last items from the results on an easy way
```python
people = Person.select('id, last_name').where(first_name='test').order(id='desc', last_name='asc')
print(people.first())
print(people.last())
```
Result:
```text
SQL-->  SELECT id, last_name FROM people WHERE first_name = %s ORDER BY id desc, last_name asc LIMIT 1 ['test']
Relation(results: [Person({'id': 10, 'last_name': 'test 2'})])
SQL-->  SELECT id, last_name FROM people WHERE first_name = %s ORDER BY id desc, last_name asc LIMIT 1 ['test']
Relation(results: [Person({'id': 10, 'last_name': 'test 2'})])
```

Or maybe you want to iterate over them
```python
people = Person.select('id, last_name').where(first_name='test')
for person in people:
    print(person)
```
Result:
```text
SQL-->  SELECT id, last_name FROM people WHERE first_name = %s ORDER BY id desc, last_name asc ['test']
Person({'id': 10, 'last_name': 'test 2'})
Person({'id': 9, 'last_name': 'test 1'})
```

Another way to do an iteration:
```python
for person in Person.where(first_name='test'):
    print(person)
```
Result:
```text
SQL-->  SELECT * FROM people WHERE first_name = %s ['test']
Person({'id': 9, 'first_name': 'test', 'last_name': 'test 1', 'address': None})
Person({'id': 10, 'first_name': 'test', 'last_name': 'test 2', 'address': None})
```

You've noticed you can limit queries?
```python
for person in Person.limit(2):
    print(person)
```
Result:
```text
SQL-->  SELECT * FROM people LIMIT 2 OFFSET 0 []
Person({'id': 2, 'first_name': 'Paul Eduardo', 'last_name': 'Marclay', 'address': 'P. del Castillo 480'})
Person({'id': 3, 'first_name': 'Duam Ignacio', 'last_name': 'Marclay', 'address': None})
```

On the same way, you cand do somethin like the following
```python
for person in Person.all().limit(2):
    print(person)
```
Result:
```text
SQL-->  SELECT * FROM people LIMIT 2 OFFSET 0 []
Person({'id': 2, 'first_name': 'Paul Eduardo', 'last_name': 'Marclay', 'address': 'P. del Castillo 480'})
Person({'id': 3, 'first_name': 'Duam Ignacio', 'last_name': 'Marclay', 'address': None})
```

Two ways of using `limit` and `offset`
```python
print(Person.all().limit(1, 2))
print(Person.all().limit(1).offset(2))
```
```text
SQL-->  SELECT * FROM people LIMIT 1 OFFSET 2 []
Relation(results: [Person({'id': 4, 'first_name': 'John', 'last_name': 'Doe', 'address': 'Missing'})])
SQL-->  SELECT * FROM people LIMIT 1 OFFSET 2 []
Relation(results: [Person({'id': 4, 'first_name': 'John', 'last_name': 'Doe', 'address': 'Missing'})])
```

Using `last()`
```python
print(Person.last())
print(Person.last(5))
print(Person.where(first_name='test').last())
print(Person.where(first_name='test').last(2))
```
Result:
```text
SQL-->  SELECT * FROM people ORDER BY id desc LIMIT 1 []
Relation(results: [Person({'id': 10, 'first_name': 'test', 'last_name': 'test 2', 'address': None})])
SQL-->  SELECT * FROM people ORDER BY id desc LIMIT 5 []
Relation(results: [Person({'id': 10, 'first_name': 'test', 'last_name': 'test 2', 'address': None}), Person({'id': 9, 'first_name': 'test', 'last_name': 'test 1', 'address': None}), Person({'id': 8, 'first_name': 'Jason', 'last_name': 'Newsted', 'address': None}), Person({'id': 7, 'first_name': 'Mike', 'last_name': 'Portnoy', 'address': None}), Person({'id': 6, 'first_name': 'Lars', 'last_name': 'Ulrich', 'address': 'No address'})])
SQL-->  SELECT * FROM people WHERE first_name = %s ORDER BY id desc LIMIT 1 ['test']
Relation(results: [Person({'id': 10, 'first_name': 'test', 'last_name': 'test 2', 'address': None})])
SQL-->  SELECT * FROM people WHERE first_name = %s ORDER BY id desc LIMIT 2 ['test']
Relation(results: [Person({'id': 10, 'first_name': 'test', 'last_name': 'test 2', 'address': None}), Person({'id': 9, 'first_name': 'test', 'last_name': 'test 1', 'address': None})])
```

Using `first()` is very similar
```python
print(Person.first())
print(Person.first(5))
print(Person.where(first_name='test').first())
print(Person.where(first_name='test').first(2))
```
Result:
```text
SQL-->  SELECT * FROM people ORDER BY id asc LIMIT 1 []
Relation(results: [Person({'id': 2, 'first_name': 'Paul Eduardo', 'last_name': 'Marclay', 'address': 'P. del Castillo 480'})])
SQL-->  SELECT * FROM people ORDER BY id asc LIMIT 5 []
Relation(results: [Person({'id': 2, 'first_name': 'Paul Eduardo', 'last_name': 'Marclay', 'address': 'P. del Castillo 480'}), Person({'id': 3, 'first_name': 'Duam Ignacio', 'last_name': 'Marclay', 'address': None}), Person({'id': 4, 'first_name': 'John', 'last_name': 'Doe', 'address': 'Missing'}), Person({'id': 5, 'first_name': 'John', 'last_name': 'Doe', 'address': 'Missing'}), Person({'id': 6, 'first_name': 'Lars', 'last_name': 'Ulrich', 'address': 'No address'})])
SQL-->  SELECT * FROM people WHERE first_name = %s ORDER BY id asc LIMIT 1 ['test']
Relation(results: [Person({'id': 9, 'first_name': 'test', 'last_name': 'test 1', 'address': None})])
SQL-->  SELECT * FROM people WHERE first_name = %s ORDER BY id asc LIMIT 2 ['test']
Relation(results: [Person({'id': 9, 'first_name': 'test', 'last_name': 'test 1', 'address': None}), Person({'id': 10, 'first_name': 'test', 'last_name': 'test 2', 'address': None})])
```

Do you need to get only ids from a query?, no worries at all!
```python
print(Person.ids())
print(Person.where(first_name='test').ids())
```
Result:
```text
SQL-->  SELECT id FROM people []
[2, 3, 4, 5, 6, 7, 8, 9, 10]
SQL-->  SELECT * FROM people WHERE first_name = %s ['test']
[9, 10]
```

Using count to get amount of records of a query
```text
print(Person.count())
print(Person.all().count())
print(Person.where(first_name='test').count())
```
Result:
```text
SQL-->  SELECT count(*) FROM people []
9
SQL-->  SELECT count(*) FROM people []
9
SQL-->  SELECT count(*) FROM people WHERE first_name = %s ['test']
2
```

Updating a record
```python
person = Person.find(2)
person.update(first_name='Paul', address='My house 123')
```
Result:
```text
SQL--> SELECT * FROM people WHERE id = %s (2,)
SQL-->  UPDATE people SET id = %s, first_name = %s, last_name = %s, address = %s WHERE id = 2; [2, 'Paul', 'Marclay', 'My house 123']
```

Deleting a record
```python
person = Person.find(5)
person.delete()
```
Result:
```text
SQL--> SELECT * FROM people WHERE id = %s (5,)
SQL-->  DELETE FROM people WHERE id = %s; [5]
```

