# Maxim Python Library

Python SDK to integrate Maxim AI. More info at [Maxim Site](https://getmaxim.ai). 
Maxim is an enterprise grade evaluation and monitoring platform for your GenAI applications.

## Version changelog

### v1.4.4

- Improvement - langchain becomes optional dependency

### v1.4.3

- Fix - connection pooling for network calls.
- Fix - connection close issue.


### v1.4.2 (🚧 Yanked)

- Fix - connection close issue

### v1.4.1

- Adds validation for provider in generation

### v1.4.0

- Now generation.result accepts 
   - OpenAI chat completion object
   - Azure OpenAI chat completion object
   - Langchain LLMResult, AIMessage object

### v1.3.4

- Fixes message_parser

### v1.3.2

- Fixes utility function for langchain to parse AIMessage into Maxim logger completion result

### v1.3.1

- Adds tool call parsing support for Langchain tracer

### v1.3.0

- Adds support for ChatCompletion in generations
- Adds type safety for retrieval results

### v1.2.7

- Bug fix where input sent with trace.config was getting overridden with None

### v1.2.6

- Adds `trace.set_input` and `trace.set_output` methods to control what to show in logs dashboard

### v1.2.5

- Removes one no_op command while creating spans
- Minor bug fixes

### v1.2.1

- Fixed MaximLangchainTracer error logging flow.

### v1.2.0

- Adds langchain support
- Adds local parsers to validate payloads on client side

### v1.1.0

- Minor bug fixes around log writer cleanup

### v1.0.0

- Public release
