# LLM agents demystified

By now, we all know that LLMs (ChatGPT, etc.) are autoregressive and just spit out tokens one by one in a loop, eating their incomplete output in each iteration. We might also have read about how tokenizers are trained and what the implementation of Attention layers roughly looks like.

But agents (and RAG) might still be a bit enigmatic. Let's demystify them (using oversimplified pseudo-Python code).

First, a quick refresher of the basics:

```python
class LLM:
    weights: ...
    def invoke(self, context: List[int]) -> List[float]:
        """Returns the logits for the next token. All the GPU things happen here."""
        ...

def softmax(logits: List[float]) -> List[float]:
    """Converts to probabilities."""
    ...

def infer_next_token(context: List[int]) -> int:
    token_probabilities = softmax(llm.invoke(context))
    return argmax(token_probabilities)  # In reality, temperature and top-k/top-p make it somewhat random.

def tokenize(text: str) -> List[int]:
    """Splits the string and returns the tokens."""
    ...

def detokenize(tokens: List[int]) -> str:
    """Converts tokens back to text."""
    ...

def inference(input_text: str) -> str:
    """Autoregressively extracts a response from the LLM"""
    input_tokens = tokenize(input_text)
    output_tokens: List[int] = []
    next_token = None
    while True:
        context: List[int] = input_tokens + output_tokens
        next_token = infer_next_token(context)
        if next_token == EOS or len(output_tokens) >= max_tokens:
            break
        output_tokens.append(next_token)
    return detokenize(output_tokens)
```

So, with `inference`, we have a function that takes input (user prompt, a full conversation, whatever), and returns the response.

Letting the model respond with an object of a specific schema can be sketched like this:

```python
def structured_inference(input_text: str, schema: Schema) -> Dict:
    """Generates output that conforms to the given schema (e.g., JSON schema)."""
    prompt = input_text + "\nRespond with valid JSON matching this schema: " + str(schema)
    # In reality, constrained decoding would ensure validity token-by-token.
    json_string = inference(prompt)
    return json.loads(json_string)
```

Retrieval-Augmented Generation (RAG) is, on an abstract level, also not too fancy. It just enriches the context (`prompt`) before the actual LLM inference with text from documents:

```python
def rag(user_query: str, knowledge_base: List[str]) -> str:
    """Retrieval Augmented Generation - answers using relevant documents."""
    # Uses embeddings to find semantically similar documents from a vector database
    relevant_docs = retrieve_most_relevant(user_query, knowledge_base)
    prompt = f"{'\n'.join(relevant_docs)}\n\n{user_query}"
    return inference(prompt)
```

Let's tackle agentic AI with tool calls next. It's basically just a loop around an LLM giving (structured) responses. When such a response requests a tool call, the selected tool is executed, its result is concatenated to the context (`conversation`), and thrown into the LLM again. Once the LLM no longer "wants" to call any tool, but gives the final answer instead, the loop is done.

The key insight: the agent builds up a conversation history where tool results become part of the context for the next LLM call, allowing it to "see" what it learned and decide what to do next.

```python
def agent(user_input: str) -> str:
    """Agent that can use tools to answer questions."""

    # We accumulate tool calls and results here.
    conversation: List[Dict] = [{"role": "user", "content": user_input}]
    
    while True:  # In practice, add max_iterations to prevent infinite loops
        # format_conversation turns the list of messages into a single prompt string.
        prompt = format_conversation(conversation) + "\nAvailable tools: " + str(tools)
        prompt += "\nRespond with either a tool call or a final answer."
        
        response_schema = {
            "type": "one_of",
            "options": [
                {"action": "tool_call", "tool": "string", "arguments": "dict"},
                {"action": "final_answer", "answer": "string"}
            ]
        }
        response = structured_inference(prompt, response_schema)
        
        if response["action"] == "final_answer":
            return response["answer"]

        # call_tool looks up the tool by name and calls it with the arguments.
        tool_result = call_tool(response["tool"], response["arguments"])

        conversation.append({"role": "assistant", "tool_call": response})
        conversation.append({"role": "tool", "content": tool_result})
```

And, provided the right tools like these

```python
tools = [
    {
        "name": "get_weather",
        "description": "Gets the current weather for a location",
        "parameters": {"location": "string"}
    },
    {
        "name": "search_web",
        "description": "Searches the web for information",
        "parameters": {"query": "string"}
    }
]
# RAG could also be a tool.
```

we already have an agent that we can ask things like

> How's the weather at El Portet beach?

If we're lucky, the agent uses
- `search_web` to find out that it's a beach in Moraira
- and then `get_weather` to get the current weather at the Costa Blanca.

Here's what the conversation might look like internally for this query:

1. **Initial state:**
   ```python
   [
    {"role": "user", "content": "How's the weather at El Portet beach?"}
   ]
   ```

2. **LLM responds with tool call:** The agent calls `search_web` to find the location.

3. **After first tool execution:**
   ```python
   [
    # ... previous messages ...
    {"role": "assistant", "tool_call": {"action": "tool_call", "tool": "search_web", "arguments": {"query": "El Portet beach location"}}},
    {"role": "tool", "content": "El Portet is a beach in Moraira, Spain."}
   ]
   ```

4. **LLM responds with another tool call:** Seeing the location, it calls `get_weather`.

5. **After second tool execution:**
   ```python
   [
    # ... previous messages ...
    {"role": "assistant", "tool_call": {"action": "tool_call", "tool": "get_weather", "arguments": {"location": "Moraira"}}},
    {"role": "tool", "content": "Moraira: Sunny, 22°C"}
   ]
   ```

6. **LLM responds with final answer:** Now having all the information, it returns `{"action": "final_answer", "answer": "It's sunny and 22°C in Moraira."}`, and the loop exits.

For more sophistication, we could add reasoning capabilities,
which can be handy for synthesizing results from multiple tool calls inside our agent loop from above.

```python
def reasoning(user_input: str) -> str:
    """Generate an answer using step-by-step reasoning."""
    prompt = user_input + "\nLet's think step by step:"
    reasoning_and_answer = inference(prompt)
    # The LLM naturally produces reasoning steps followed by the answer.
    # This works because LLMs are trained on Chain of Thought data.
    # For inspection/validation, use structured_inference with
    # reasoning_schema = {"reasoning_steps": "list[str]", "final_answer": "string"}
    return reasoning_and_answer  # We could also return just the final_answer here.
```

And that's it. I hope agents are boring now. :)
