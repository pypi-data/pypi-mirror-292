# Icosa Computing LangChain Package

[![PyPI version](https://img.shields.io/pypi/v/langchain_icosa.svg)](https://pypi.org/project/langchain-icosa/)

The Icosa Computing LangChain Library provides convenient access to our flagship Combinatorial Reasoning LLM pipeline with out of the box support and integration with the LangChain LLM application framework.

See our live demo website [here](https://demo.icosacomputing.com/)!

See our arXiv preprint [here](https://arxiv.org/abs/2407.00071)!

## Installation

```bash
pip install langchain_icosa
```

Because all processing occurs off-premises on Icosa Computing servers, this library only requires the LangChain core and OpenAI libraries.

You must also have a valid OpenAI API key that will be called by the LLM 212 times per request.
This can be done by storing the API key found on the [OpenAI API key page](https://platform.openai.com/api-keys).

## Usage

The Combinatorial Reasoning LLM provides support for all functions defined by the LangChain Runnable interface. However, streaming is limited to the final output after the final reasons have been selected by the optimizer.

### Initialization
```Python
from langchain_icosa.combinatorial_reasoning import CombinatorialReasoningLLM

llm = CombinatorialReasoningLLM(
    linear_sensitivity = 1.0, 
    thresh_param = 1.0, 
    risk_param = 1.0, 
    weight = 2, 
    openai_api_key = API_KEY, # can also be implicitly passed in via `OPENAI API KEY` environment variable
    model = 'gpt-4o' # defaults to gpt-4o-mini
)
```

The default hyper-parameters have already been tuned by the Icosa team, so using the default hyper-parameters should suffice for almost all use-cases.

### Basic Calls
```Python
llm = CombinatorialReasoningLLM(openai_api_key=API_KEY)
llm.invoke("There are six animals: lion, hyena, elephant, deer, cat and mouse. Separate them to three spaces to minimize conflict.", responseType='answerWithReasoning') # includes reasoning for solution
llm.invoke("There are six animals: lion, hyena, elephant, deer, cat and mouse. Separate them to three spaces to minimize conflict.") # excludes reasoning for solution
```

The invoke method supports 6 keyword arguments:
1. `linear_sensitivity` Overrides the linear sensitivity parameter.
2. `thresh_param`: Overrides the thresh parameter.
3. `risk_param`: Overrides the risk parameter.
4. `weight`: Overrides the weight parameter.
5. `responseType`: Whether or not to include the LLM's reasoning in the response. Must be one of `answer` (default) or `answerWithReasoning`.
6. `seed`: Sets the seed for the LLM. Defaults to 0.

### Streaming
```Python
llm = CombinatorialReasoningLLM(openai_api_key=API_KEY, model='gpt-4o')
for token in llm.stream("Should I buy AMZN stock today?"):
    print(token, end="", flush=True)
```

Like the invoke method, streaming supports the following keyword arguments:
1. `linear_sensitivity` Overrides the linear sensitivity parameter.
2. `thresh_param`: Overrides the thresh parameter.
3. `risk_param`: Overrides the risk parameter.
4. `weight`: Overrides the weight parameter.
5. `seed`: Sets the seed for the LLM. Defaults to 0.

However, unlike invoke, streaming does not support different response types. All streams will include the final reasoning.

### Callbacks

The LLM supports access to the sampled reasons, the distinct sampled reasons, and the final reasons selected in the annealing step via the `CombinatorialReasoningCallbackHandler`. Example usage is shown below. 

```Python
from langchain_icosa.combinatorial_reasoning import CombinatorialReasoningLLM, CombinatorialReasoningCallbackHandler

llm = CombinatorialReasoningLLM(openai_api_key=API_KEY)
callback = CombinatorialReasoningCallbackHandler()

prompt = "There are six animals: lion, hyena, elephant, deer, cat and mouse. Separate them to three spaces to minimize conflict."
print(llm.invoke(prompt, config = {'callbacks': [callback]}))

print(f"Statistics: {callback.stats}")
print(f"Raw reasons: {callback.data}")
```

### Using a Chain
```Python
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_icosa.combinatorial_reasoning import CombinatorialReasoningLLM

prompt = PromptTemplate.from_template("Should I buy {ticker} stock today?")
model = CombinatorialReasoningLLM(openai_api_key=API_KEY)
chain = prompt | model | StrOutputParser()

chain.invoke({'ticker': 'AAPL'})
```
