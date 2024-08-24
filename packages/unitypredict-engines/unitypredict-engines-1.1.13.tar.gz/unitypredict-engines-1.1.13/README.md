# UnityPredict Local App Engine Creator

## Introduction

The **`unitypredict-engines` python sdk** is designed to help accelerate the testing and debugging of **App Engines** for deployment on the `UnityPredict` platform.

On `UnityPredict`, **"Engines"** are the underlying compute framework that is executed, at scale, to perform inference or run business logic. In contrast, **"Models"** define the interface for these Engines. **Every Engine must be connected to a "Model"** because the Model serves as the interface that defines how `UnityPredict` communicates with the Engine. The Model specifies variable names and data types for inputs and outputs. Additionally, `UnityPredict` uses the Model definition to auto-generate APIs and user interfaces.

**"App Engines"** are specialized extensions of `UnityPredict` Engines that allow developers to write custom Python code, which the platform will execute at scale. These custom-defined Engines offer developers the flexibility needed to create complex applications. Within an App Engine, developers can access various platform features through code. For instance, **App Engine code can easily invoke other models (aka. chaining) or define cost calculations**. App Engines also enable developers to choose specific hardware types for running their code.

This guide focuses on the local development and testing of custom App Engine code.

For a full guide on how to use App Engine(s) on UnityPredict, please visit our complete help documentation here [UnityPredict Docs](https://console.unitypredict.com).

## Installation
* You can use pip to install the ```unitypredict-engines``` library.
```bash
pip install unitypredict-engines
```

## Usage

### EntryPoint.py

#### What is `EntryPoint.py`

`EntryPoint.py` is the script created by the **user** to provide the platform a well-defined function that can be invoked as the **starting point** for the **inference code**. It also acts as a gateway to access the **"platform"** object containing various features provided by UnityPredict

### Create an example `EntryPoint.py`

Create a custom entrypoint of your App Engine under the file **`EntryPoint.py`** containing the inference logic.

**NOTE:** The name of the file should be **`EntryPoint.py`**. If not followed, during the actual deployment on `UnityPredict` repository, the created file might not get invoked due to anincorrect name.

Given below is an example of a simple **`EntryPoint.py`**


```python
from unitypredict_engines.Platform import IPlatform, InferenceRequest, InferenceResponse, OutcomeValue, InferenceContextData
import datetime



def run_engine(request: InferenceRequest, platform: IPlatform) -> InferenceResponse:

    

    platform.logMsg("Running User Code...")
    response = InferenceResponse()

    try:
        prompt = request.InputValues['InputMessage']

        currentExecTime = datetime.datetime.now()
        currentExecTime = currentExecTime.strftime("%d-%m-%YT%H-%M-%S")
        resp_message = "Echo message: {} Time:: {}".format(prompt, currentExecTime)   
        
        response.Outcomes['OutputMessage'] = [OutcomeValue(value=resp_message, probability=1.0)]

    except Exception as e:
        response.ErrorMessages = "Entrypoint Exception Occured: {}".format(str(e))

    print("Finished Running User Code...")
    return response

```

### Running the `EntryPoint.py`

In order to run the `EntryPoint.py` locally, add the following `main` section to the file itself.

```python
#### For Local testing ###

if __name__ == "__main__":

    from unitypredict_engines import UnityPredictHost
    
    # Initialize the UnityPredict Platform
    platform = UnityPredictHost()

    testRequest = InferenceRequest()
    testRequest.InputValues = {}
    testRequest.InputValues["InputMessage"] = "Hi, this is an echo message"
    results: InferenceResponse = run_engine(testRequest, platform)

    # Print Outputs
    if (results.Outcomes != None):
        for outcomKeys, outcomeValues in results.Outcomes.items():
            print ("\n\nOutcome Key: {}".format(outcomKeys))
            for values in outcomeValues:
                infVal: OutcomeValue = values
                print ("Outcome Value: \n{}\n\n".format(infVal.Value))
                print ("Outcome Probability: \n{}\n\n".format(infVal.Probability))
    
    # Print Error Messages (if any)
    print ("Error Messages: {}".format(results.ErrorMessages))

```
Now run the `EntryPoint.py`

```bash
python EntryPoint.py
```

### Output

The output should be the message added as the `InputMessage` in the main, appended with the timestamp of the execution.

```bash
Config file detected, loading data from: D:\Documents\SelfProjects\UPTAzure\unitypredict-sdks\mainFolder\config.json

Running User Code...

Finished Running User Code...


Outcome Key: OutputMessage
Outcome Value:
Echo message: Hi, this is an echo message Time:: 18-08-2024T18-56-33


Outcome Probability:
1.0
```


While running the script for the **first time**, you may also encounter a log message as follows.

```bash
Config file not detected, creating templated config file: {project-current-folder}\config.json
```
This marks the auto-creation of the config file template `config.json`, along with the tree-structure following the templated config of the project which is the **mock building block** for the APIs of `UnityPredict` used under `EntryPoint.py`.



### Config File and the project tree structure

The templated `config.json` looks like this:
```json
{
    "ModelsDirPath": "{userPWD}/unitypredict_mocktool/models",
    "RequestFilesDirPath": "{userPWD}/unitypredict_mocktool/requests",
    "SAVE_CONTEXT": true,
    "TempDirPath": "{userPWD}/unitypredict_mocktool/tmp",
    "UPT_API_KEY": ""
}
```

And the tree structure of the generated directory will be:
```plaintext
{userPWD}/
|-- unitypredict_mocktool/
|  |-- models/
|  |-- requests/
|  |-- tmp/
|-- EntryPoint.py
|-- config.json
```

Details of the JSON settings:

* **ModelsDirPath**: Local model files/binaries to be uploaded to AppEngine for using during the execution can be added under the specified **ModelsDirPath**

* **RequestFilesDirPath**: Files or Folders to be uploaded to AppEngine for using during the execution can be added under the specified **RequestFilesDirPath**

* **SAVE_CONTEXT**: Retains context across multiple requests. Disable it using ```"SAVE_CONTEXT" : false```

* **UPT_API_KEY**: API Key token generated from the UnityPredict profile of the user.

* **TempDirPath**: Temporary directory which can be used for writing or reading extra files or folders depending on the requirements of the App Engine




## License
Copyright 2024 Unified Predictive Technologies

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.