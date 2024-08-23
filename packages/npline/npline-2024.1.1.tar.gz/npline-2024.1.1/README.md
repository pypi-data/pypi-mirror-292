# NP LINE
A helper package to send a LINE notification message to your team

### Prerequisites
- Please use this [guide](https://youtu.be/_iSSOUFANyk) to create your token

### Installation
`pip install npline`

### Example
```python
from npline import LINE

if __name__ == "__main__":
    my_token = 'asdfasdfasdfasfasdfasdfasdfasdfsadf'
    line = LINE(token_id=my_token,instance_id=1)
    line.send_msg('Hello World!')
```