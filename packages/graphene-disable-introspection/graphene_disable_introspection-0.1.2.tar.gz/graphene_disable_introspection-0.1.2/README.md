# Graphene Middleware to Disable Introspection

This middleware for Python's Graphene library disables introspection queries, enhancing the security of your GraphQL API by preventing clients from discovering the schema.

## Installation

To install the middleware, you can use pip:

```bash
pip install graphene-disable-introspection
```

## Usage
To use the middleware in your Graphene project, you need to add it to your GraphQL schema.

### Example
#### Python Usage
Import the middleware and add it to your schema.
```python
from graphene_disable_introspection import DisableIntrospectionMiddleware

GraphqlView.as_view(middleware=[DisableIntrospectionMiddleware()])
```

#### Django Usage
Add the middleware to your Django settings. I recommend to add it to the top of the middleware list.
```python
GRAPHENE = {
    ...
    "MIDDLEWARE": [
        "graphene_disable_introspection.DisableIntrospectionMiddleware",
        ...
    ],
}
```

Alternatively, you can deactivate Graphene introspection for the production system only.
```python
if os.environ.get("APP_SETTINGS") == "production":
    GRAPHENE["MIDDLEWARE"].insert(0, "graphene_disable_introspection.DisableIntrospectionMiddleware")
```

## License
This project is licensed under the GPL-3.0 License.

