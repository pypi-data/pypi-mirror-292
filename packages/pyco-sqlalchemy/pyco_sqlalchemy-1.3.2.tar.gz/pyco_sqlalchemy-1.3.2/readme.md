# pyco-sqlalchemy

- Base On `SqlAlchemy`, according to regular web sevices, encapsulate A interface class(`CoModel`), expanded general APIs
  for CURD, which makes SqlAlchemy's ORM even simpler for humans, support with Flask/Django/OtherWebFrames.

---

## Release:

```text
GitCommit=${GitCommit}
PublishAt=${PublishAt}
PublishVersion=${PublishVersion}
```

---
## General APIs:

-  Pyco-Sqlalchemy v1.2.*

|:-:|:---:|:---:|:---:|:---:|
|:-:|:---:|:---:|:---| :--- |
|   |<td colspan=3> Pyco-Sqlalchemy v1.2.*
| \ |  @语义    | @HTTP-Method | @Self-API             | @Cls-API | 
| C |  Create | POST      |  self.save()          | insert(form, **kws) | 
| R | Read    | GET       |  self.to_dict(**kws)  | filter_by, page_items, getOr404, lastOrNone | 
| U | Update  | PUT/POST  |  self.update(**kws)   | upsert_one(filter_cond:dict, **updated_kws) |
| D | Delete  | DELETE    |  self.remove()        | discard(filter_cond=None, limit=1, **kws) |
 

<p style="display:none">
基于`sqlalchemy`， 基于web常规业务，封装接口类`CoModel`，提供自定义的通用接口。
</p>  

## Usage Samples:

```python
from pyco_sqlalchemy._flask import BaseModel, db


class User(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32))
    email = db.Column(db.String(64), unique=True)


form = dict(name="dev")
u1 = User.insert(form, email="dev@pypi.com")
u3 = User.upsert_one(form, email="dev@oncode.cc")
assert u1.id == u3.id

```
