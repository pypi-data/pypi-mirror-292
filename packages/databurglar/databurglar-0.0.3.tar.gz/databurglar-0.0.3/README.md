# DataBurglar

<p>
  <b>SOMETHING</b> happened at <b>SOMETIME</b> and we would like to <b>STORE</b> it in <b>Postgres</b>.
</p>

<hr />

### 1. Install

```
    pip install databurglar
```

### 2. Include Tables
```python
from databurglar.models import setup_data_collection, setup_surveys

engine: Engine = ...

## setup tables to collect data based on a `UserEvent`
setup_data_collection(
    engine,
    UserEvent
)

## <optional>: setup tables to build dynamic data collection forms/surveys
setup_surveys(engine)
```

### 3. Queries

### 4. Commands



## Local Project Development
#### windows
```
  python -m venv env
  .\env\Scripts\activate

  pip install -r requirements.txt
```
