## LLM experience

* **`llama3-groq-tool-use`**
    * +Small, but pretty fast
    * +Runs locally
    * +Works with the function calling quite well
    * +Was following instructions pretty well
    * -Had some problems with understanding high amounts of data

* **`gemma2:27b`**
    * -Was not quite useful, as it couldn't work with function calling

* **`qwen2.5:32b`** <-- *used right now*
    * +Provided the best performance so far
    * +Runs locally on 4080
    * +Follows instructions pretty well
    * +Almost always selects the correct algorithm
    * -Has some limitations of the context window

* **`llama3:70b`**
    * +Theoretically has better performance out of all
    * -Doesn't follow the rules from the first time
    * -Isn't trained to work with function tools
    * -Runs a bit slower than qwen

* **`llama3:405b`**
    * -Runs visibly slower than all other models