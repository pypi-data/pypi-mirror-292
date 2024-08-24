# w3ai-sdk

## Description
Using w3ai-sdk package to querry some of data from W3AI Flatform using APIKey. For example , Getting user balance, creating a task, getting task result, getting statistics and history of models, checking API permission ...
## Installation
``` 
pip install w3ai-python-sdk
```
## Setup
To start, simply require the W3AI-SDK and set up an instance with your W3AI API Keys.Please checking out your W3AI Page. In the example below show you how to using the SDK.

```
from 'w3ai-python-sdk' import W3AIClient
client = W3AIClient(API_KEY, SERVER_ENDPOINT)
```

## Usage


### API Key Permission
```
client.checkApiKeyPermission(API_KEY)

```
Response :

```
{
  status: 'success',
  data: {
    limit_models: true,
    models: [ '7da922fe-02b9-4534-b218-c5b7c79d2195' ]
  }
}

```

### Models infomation

```
client.apiKeyGetModelInfo(MODEL_ID)
```

Response :
```
{
  status: 'success',
  data: {
    model_id: '7da922fe-02b9-4534-b218-c5b7c79d2195',
    api_price: 0.12342134,
    model_description: 'this is best model',
    commit_hash: 'd1c366e0c6bbfdd28cb31301852030c113013576',
    input_format: { input: [Object] },
    output_format: { output: [Object] }
  }
}
```


### Model serving info
```
client.apiKeyGetModelServings(MODEL_ID)
```

Response :
```
{ status: 'success', data: { consumers: 1, serving: true } }
```

### Task executing cost info
```
client.apiKeyGetModelCost(MODEL_ID)
```

Response :
```
{
  status: 'success',
  message: 'Success',
  data: { cost: 0.011000000000000001, symbol: '$', unit: 'USD' }
}
```

### Creating a task

Argument exmaple:
```
FILE_LIST = [
    {
      "key": "input",
      "data": "file_stotage_url",
      "name": "image.jpg"
    },
    {
      "key": "input2",
      "data": "file_stotage_url2",
      "name": "image2.jpg"
    }
  ]

INPUT_PARAMS = {
  "input": {
    "type": "file",
    "samples": [],
    "required": true,
    "mime_type": [
      "image/*"
    ]
  }
}

MODEL_ID = "7da922fe-02b9-4534-b218-c5b7c79d2195"
```


```
client.createTask(fileList= FILE_LIST, inputParam=INPUT_PARAMS, modelId= MODEL_ID)
```

Response :
```
{
  status: 'success',
  message: 'Success',
  data: "e52fa152-351d-4a40-a4ce-83a4ff11d87e"
}
```

### Getting task result
```
client.getTaskResult(taskId = TASK_ID)
```

Response :
```
{
  "result": {
    "additionalProp1": {}
  },
  "status": "sucess",
  "success": true
}
```