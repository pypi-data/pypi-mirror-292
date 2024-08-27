# n8n_py

The n8n_py SDK connects the [n8n-nodes-python-function](https://www.npmjs.com/package/n8n-nodes-python-function) custom node with your python functions.

## Examples

### Hello World

Returns a hello world json response

```python
from n8n_py import expose_function, String
from n8n_py.handler import handle

@expose_function("Hello World", "returns a friendly greeting", {
	"name": String(friendly_name="Name", description="Name of person to greet", required=True, default="Alice")
})
def hello_world(name: str): dict[str, str]: # Exposed functions must return a JSON serializable dictionary
	return {
		"greeting": f"Hello {name}!"
	}

handle() # Starts the n8n_py server and exposes the function declared above
```

### Multi-File Projects

n8n_py can handle functions from anywhere as long as they are imported into the handler, and have the @expose_function decorator

#### File Structure

```
multi-file/
	mapping.py
	hello_world.py
```

_hello_world.py_

```python
from n8n_py import expose_function, String

@expose_function("Hello World", "returns a friendly greeting", {
	"name": String(friendly_name="Name", description="Name of person to greet", required=True, default="Alice")
})
def hello_world(name: str): dict[str, str]: # Exposed functions must return a JSON serializable dictionary
	return {
		"greeting": f"Hello {name}!"
	}
```

_mapping.py_

```python
from n8n_py.handler import handle
import hello_world as _ # Includes the exposed function.

handle() # Starts the n8n_py server and exposes all imported functions
```
