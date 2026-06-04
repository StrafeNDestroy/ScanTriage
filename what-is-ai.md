# How does an AI model work

An AI model is trained on a large dataset and learns to make predictions from that
data. What it learns is stored in **weights**.

These weights are billions of numbers that get adjusted during training. Each time
the model predicts wrong, the numbers are nudged toward what would have been right.
Repeated across the whole dataset, those nudges accumulate into a set of weights that
encodes the patterns in the data: facts, grammar, associations, reasoning.

The weights are the model. Loading "the model" into VRAM means loading these numbers.
Training produces them once. Running the model, called inference, just reads them.


## What does a model predict

All a model does is try to predict the next **token**.

At each step it predicts a probability for every possible token in its vocabulary,
and something then picks one from that distribution. The sections below break that
down: what a token is, how the loop works, how it stops, and a worked example.

## What is a token and tokenization

A token is the basic unit of text that a model reads and writes. It is usually not a
whole word. Common words like "the" are one token, but longer words get split into
pieces, so "autocomplete" might become "auto" plus "complete". A space is normally
attached to the front of a word. A rough rule for English is about 4 characters per
token, or roughly three quarters of a word.

Tokenization is the step that converts text into tokens before the model sees it.
Each token maps to a number (an ID), because the model does math on numbers, not on
letters. So your input text becomes a list of token IDs going in, and the model's
output token IDs get converted back into text coming out.

This is why everything is counted in tokens, not words: the context window, the
model's speed in tokens per second, and API pricing. Tokens are the real unit the
model works in. Words are a human convenience.

## How prediction works

Once it predicts one token, it appends that token to the text so far and predicts the
next one, using the entire sequence as input each time, not just the original prompt.
It repeats this loop one token at a time.

This is called being autoregressive: each output becomes part of the input for the
next prediction.

Reading the entire sequence on every step is the key detail to carry forward. It is
what makes the loop coherent, but it is also expensive, and that cost is exactly what
the KV cache exists to manage.

### Example of a prediciton and autoregresstion
The model reads the prompt plus everything generated so far, predicts a
probability for the next token, picks the top one (at temperature 0), appends
it, and repeats. It stops when the end token wins.

| Step | Answer so far | Candidate tokens (probability) | Picked |
|------|---------------|--------------------------------|--------|
| 1 | (nothing yet) | Water 70%, Trees 15%, Sun 10%, A 5% | Water |
| 2 | Water | will 50%, and 20%, is 15%, helps 15% | will |
| 3 | Water will | make 45%, help 30%, cause 15%, allow 10% | make |
| 4 | Water will make | a 60%, trees 20%, the 15%, it 5% | a |
| 5 | Water will make a | tree 80%, plant 10%, seed 7%, sapling 3% | tree |
| 6 | Water will make a tree | grow 85%, thrive 8%, survive 5%, live 2% | grow |
| 7 | Water will make a tree grow | period 70%, taller 15%, big 10% | period |
| 8 | Water will make a tree grow. | [EOT] 90%, It 5%, Trees 3%, So 2% | [EOT] stop |


## KV cache

The KV cache is the model's working memory for the sequence it is currently
generating. It lives in VRAM, alongside the weights, and it exists to solve the cost
just described.

Doing that re-reading from scratch every step would repeat a huge amount of identical
work, because the earlier tokens have not changed. So the model saves the intermediate
results for the tokens it has already processed (these are called the keys and values,
hence KV) and reuses them on the next step instead of recomputing them.

The tradeoff is memory. The cache grows as the sequence gets longer, because every new
token adds its own entry. A short prompt uses little; a long conversation or a big
chunk of retrieved text uses a lot.

So your VRAM holds two things: the weights (a fixed size, set by the model and its
quantization) plus the KV cache (a growing size, set by how long the sequence gets).
That growing piece is why you leave headroom when picking a model size, and it raises
an obvious question: if the sequence keeps growing, is there a limit to how long it
can get? There is, and that limit is the context window.

## Context window

The context window is the maximum length of sequence a model can read at once,
measured in tokens. It is the ceiling on the growth the KV cache section just
described. It covers everything: the prompt, plus every token generated so far. The
whole thing has to fit inside the window.

This is a hard limit baked into the model, not a setting you can turn up. If the
sequence grows past the window, the oldest tokens fall off the front and the model
effectively forgets them. It only ever sees what is currently inside the window.

The window and the cache are two sides of the same sequence. The context window is the
limit on how long the sequence is allowed to get; the KV cache is the VRAM cost of the
sequence as it grows toward that limit. A bigger window lets you feed in more, but more
tokens in the window means a bigger cache, which means more VRAM.

This matters directly in retrieval (Phase 4). When you pull text from the knowledge
base and add it to the prompt, that retrieved text is spending your context window.
The finding, your instructions, and the retrieved context all share the same finite
space, so you cannot just stuff in everything. Choosing what to retrieve is partly a
question of what will fit.

## Example of VRAM layout

10 GB VRAM. One cell = 1 GB. W = weights (fixed), K = KV cache, . = free.

| Sequence length    | VRAM (10 cells)              | Weights | Cache | Free |
|--------------------|------------------------------|---------|-------|------|
| Short (~500 tok)   | `[W][W][W][W][W][K][.][.][.][.]` | ~4.5 GB | 1 GB  | 4 GB |
| Long (~8000 tok)   | `[W][W][W][W][W][K][K][K][K][.]` | ~4.5 GB | 4 GB  | 1 GB |

The W block never moves: the weights are a fixed size set by the model and its
quantization. The K block expands rightward as the token count grows, because a longer
sequence means a bigger KV cache. It eats the free space as it goes.

The context window is the hard limit on token count, so it caps how far K can spread.
Without that ceiling, a long enough sequence would push K past the free space and the
model would run out of VRAM.

## How does a model know its done outputting

The model does not decide when it is "done" as a separate step from token prediction. 
Stopping is just another prediction. The vocabulary includes a special end token, 
written <EOT>, and when the text so far makes "nothing left to say" the most likely 
next token, <EOT> wins, gets predicted, and the loop halts. A hard token limit can also 
force it to stop.


# Using open-weight AI

Open-weight models are models whose trained weights are made available for anyone to
download. Because you have the weights, you can run the model on your own hardware
instead of sending requests to a third party's servers.

This is the main contrast with closed or API-only models (the kind you reach over the
internet) like claude,chatgpt and gemini. Where the weights stay private and you can only 
use the model through someone else's service. Running open-weight gives you privacy 
(your data never leaves your machine), no per-use cost, and offline capability, at the price 
of supplying your own hardware resources.

## Ollama

Ollama is a manager that runs on top of the llama.cpp inference engine.

### What is an inference engine?

It is the program that takes a model's weights, loads them into VRAM, and runs the
matrix math (the model itself) to produce the next token.

On its own, a weights file does nothing. It is just numbers on disk. The inference
engine is what loads those numbers and runs them. Ollama is not that engine. It is a
manager on top of the engine that downloads the weights, picks the quantization, and
exposes an API, then hands the actual running to llama.cpp.

### What is quantization?

A model is billions of weights the numbers that determine its output. Each weight
is normally stored in 16 bits. Quantization stores each weight in fewer bits (for
example 4), which shrinks the model's memory footprint by a large factor, at a small
cost to accuracy. Models ship already quantized, as a GGUF file. Ollama downloads that file and
llama.cpp runs it.

## Sizing: fitting a model and its context into VRAM

Model size and context size are not two separate questions. They are one decision,
because both spend the same VRAM budget. VRAM has to hold three things at once:

  weights (fixed by the model and its quantization)
  KV cache (grows with how many tokens you allow, set by num_ctx)
  runtime overhead (the working memory the inference engine needs to run)

The whole job is choosing a model and a num_ctx so all three fit with headroom. You
make it in order: find your budget, pick the model (that fixes the weight cost), then
size the context into whatever VRAM is left.

### What num_ctx is

num_ctx is Ollama's setting for the context window: the maximum number of tokens the
model may read at once, prompt plus generated output combined. The name is short for
"number of context tokens." It is Ollama's concrete dial for the context window
concept: the context window is the what, num_ctx is the how.

It matters because it is the one knob in this whole problem that you set. The weights
are fixed by the model, the per-token cache cost is fixed by the model's architecture,
but num_ctx is yours to choose, and choosing it sets how large the KV cache grows. So
sizing your VRAM really comes down to picking the right num_ctx.

Setting num_ctx is not free. Ollama pre-allocates KV cache space for that many tokens
up front, so a larger num_ctx reserves more VRAM whether or not you fill it. That is
why the steps below are about choosing it deliberately, not maxing it out.

### Step 1: find your real VRAM budget

Start from total VRAM and subtract what is already in use. On a 10 GB card with a
desktop running (browser, etc.) about 1.4 GB is already spoken for on my computer,
leaving roughly 8.5 GB usable. On linux you can use `nvida-smi'

### Step 2: pick the model size

Now that we know about 8.5 GB is usable, we need to fit two things into it: the model
weights and the potential KV cache.

Model size is measured in parameters, written as a number followed by B for billion
(7B means 7 billion weights). More parameters usually means a more capable model, but
also a larger memory footprint and slower output.

A model has to fit in VRAM to run fast. If it does not fit, the engine spills the
overflow into system RAM and runs that part on the CPU, which is much slower. So pick
the largest model that fits in VRAM with headroom left over, because the weights are
not the only thing in VRAM. The KV cache needs room too (Step 3).

```bash
weights = number of parameters * bytes per parameter

parameters     = 7 billion
q4 = 4 bits    = 0.5 bytes per parameter

7,000,000,000 * 0.5 bytes = 3,500,000,000 bytes = ~3.5 GB
```

That 3.5 GB is the ideal case. In practice q4_K_M does not drop every weight to 4
bits, it keeps some at higher precision (mixed precision), so the real footprint is
closer to 4 to 4.5 GB. You do not have to estimate this exactly: Ollama reports the
actual quantized model size when you pull it, so use that number for budgeting.

### Step 3: size num_ctx into what is left

With the weights accounted for, the rest of the budget goes to the KV cache. A
comfortable target on this card is about 2 GB of cache, enough context for this
project without crowding the weights.

The KV cache is linear in tokens: every token costs a fixed slice of memory, so total
cache = num_ctx times the cost per token. That per-token cost is set by the model's
architecture (its layers and hidden dimension), not by you. For a 7B to 8B model it is
roughly a quarter of a megabyte per token. You do not set the rate, you set the token
count.

Worked example for one value:

```bash
per-token cost = ~256 KB   (set by the model architecture, ~0.25 MB for a 7-8B model)
num_ctx        = 2048      (the token ceiling you choose)

KV cache = 2048 * 256 KB = ~524,288 KB = ~512 MB = ~0.5 GB
```

The table below just does that same multiplication across a range of num_ctx values,
which is why it doubles cleanly: double the tokens, double the cache.

| num_ctx | KV cache | weights | total   | fits 10 GB card?  |
|---------|----------|---------|---------|-------------------|
| 2048    | ~0.5 GB  | ~4.5 GB | ~5.0 GB | yes, lots of room |
| 4096    | ~1.0 GB  | ~4.5 GB | ~5.5 GB | yes, comfortable  |
| 8192    | ~2.0 GB  | ~4.5 GB | ~6.5 GB | yes, good default |
| 16384   | ~4.0 GB  | ~4.5 GB | ~8.5 GB | tight, may spill  |
| 32768   | ~8.0 GB  | ~4.5 GB | ~12.5 GB | no, exceeds VRAM |

Add back the ~1.4 GB the desktop uses, and 16384 already lands near the ceiling, so
8192 is the safe default (about 2 GB of cache, matching the target above) and roughly
12288 is the practical max on this card.

### Step 4: but size to your need, not the maximum

Bigger num_ctx is not better. It just costs VRAM, and it costs it up front because
Ollama pre-allocates. Pick the smallest value that fits what you put in plus what you
expect out:

  system prompt + the finding + retrieved knowledge (Phase 4) + room for the answer

If that adds up to about 3000 tokens, a num_ctx of 4096 is plenty and wastes no VRAM.
Only raise it when your inputs actually grow. In Phase 4 your pipeline defines this
number: measure what a finding plus its retrieved knowledge runs, and that is your
num_ctx. You are not guessing a context size in the abstract, you are sizing to a
measured need and then checking it fits.

### Step 5: verify, do not trust the math

The table is an estimate. Confirm reality with `ollama ps`, which shows the model size
and context actually loaded. The warning sign is speed: if output suddenly drops from
tens of tokens per second to single digits, the cache spilled to system RAM and
num_ctx is too high.


# Types of AI models and their use cases

"AI model" is not one thing. Models fall into a few kinds, each built for a different
job. Knowing which kind you need is half of using them well.

## Generation models

These take text and predict the next token, producing new text. This is the kind
behind chatbots and assistants: read some input, write a response. They are the
models people usually mean by "LLM."

Within generation models there is a split worth knowing:

A base model is only trained to autocomplete text. Give it "The capital of France is"
and it continues the pattern. It does not follow instructions, it just predicts.

An instruct model is a base model given extra training to follow instructions and
behave like an assistant. This is the one you usually want, because you are giving it
tasks, not asking it to autocomplete. Reach for instruct unless you have a specific
reason not to.

Use case: any task that produces text. Answering questions, summarizing, writing,
classifying, reasoning over input.

## Embedding models

These do not generate text. They take a piece of text and turn it into a vector, a
list of numbers that captures its meaning, so that similar meanings produce similar
vectors. You never read the output; you compare vectors to find which texts are
closest in meaning.

This is the engine of search and retrieval. You embed a body of documents once, then
embed a query and find the nearest documents to it. nomic-embed and bge are common
choices, and they are small and fast compared with a generation model.

Use case: semantic search, retrieval, clustering, recommendations, deduplication.
Anything about measuring how similar two pieces of text are.

A generation model and an embedding model are different tools. You may run both: one
to understand and write, one to measure similarity. Do not try to make one do the
other's job.

## Reranker models

A reranker sometimes joins a retrieval pipeline. After an embedding search returns a
handful of candidates, a reranker re-scores those candidates against the query more
carefully and reorders them, so the best one ends up on top. Embeddings give fast,
rough retrieval; a reranker gives slower, sharper ordering of the few results
embeddings found.

Use case: a refinement on top of embedding search when retrieval quality matters and
the candidate list is already small.

## Other types you will run into

The kinds above are the common ones. Many more exist. These are worth recognizing by
name, even if you never use them.

Reasoning models are generation models trained to "think" before answering, producing
a chain of intermediate reasoning steps and then a final answer. Not a separate
architecture, just a generation model tuned for harder multi-step problems. Flagged as
"reasoning" or "thinking" variants. DeepSeek-R1 was the well known open one.
Use case: math, logic, planning, anything needing multiple steps of work.

Code models are generation models specialized on code: completion, generation, bug
fixing. Same architecture as a text LLM, trained heavily on code. Qwen-Coder is one.
Use case: coding assistants, autocompletion, code search and review.

Classifiers output a label, not free text: positive or negative, spam or not, safe or
harmful. Often small encoder models, much cheaper than a full LLM, and for a fixed set
of categories they can beat one.
Use case: sentiment, content moderation, routing, any fixed-category decision.

Video and 3D generation extend image generation into more dimensions: text to video,
image to video, text to 3D. Mostly diffusion based like image generation, just heavier.
Use case: generating or extending video and 3D assets from a prompt.

Time-series and tabular models forecast numbers (demand, prices, sensor readings) or
learn from spreadsheet-style data. Often these are not neural networks at all:
gradient-boosted trees like XGBoost still win on many tabular problems. A useful
reminder that "AI model" is broader than "LLM."
Use case: forecasting, fraud detection, and most classic business data problems.

## Models for other modalities

Everything above is about text. Models also exist for images, audio, and speech, and
they split into the same two motions you already know: understanding input, and
generating output.

### Vision: image understanding

These take an image (often plus text) and produce text about it: describe it, answer
a question about it, read the text in it, locate objects. A generation model with this
ability is called multimodal or a vision language model (VLM), because it accepts more
than one type of input. Examples include LLaVA and the vision variants of Qwen and
Gemma.

Use case: image captioning, document and screenshot understanding, visual question
answering, OCR-style reading.

### Image generation

The reverse direction: text goes in, a new image comes out. These are usually a
different architecture from LLMs, called diffusion models, which start from noise and
repeatedly refine it into an image that matches the prompt. Stable Diffusion and Flux
are common open-weight examples.

Use case: making images from a description, editing or extending existing images.

### Speech to text (ASR)

Audio of speech goes in, text comes out. This is automatic speech recognition, ASR.
Whisper is the well known open-weight model here.

Use case: transcription, captions, voice input, meeting notes.

### Text to speech (TTS)

The reverse: text goes in, spoken audio comes out. These are text to speech models,
and modern ones can clone a voice or control tone and emotion.

Use case: voiceovers, read-aloud, voice for assistants.

### The pattern to notice

Across every modality the same two roles repeat: a model that understands an input
(image to text, speech to text) and a model that generates an output (text to image,
text to speech). Text generation is just the most familiar instance of the second
role. Once you see that, a new model type is easy to place: ask what goes in, what
comes out, and whether the job is understanding or generating.

## Two architecture terms you will see

These describe how a model is built internally. You do not need them to use a model,
but they explain the labels on model cards.

Dense vs MoE (mixture of experts). In a dense model every parameter is used for every
token. In an MoE model the parameters are split into "experts" and only a few are
activated per token, so a model can have a huge total parameter count but only run a
small active fraction each step. That is why you will see models listed as something
like "120B total / 12B active": the first number is its size on disk and in memory,
the second is roughly its compute cost per token. For sizing, the total is what has to
fit in VRAM.

Context length and attention tricks. Models advertise a maximum context length (the
trained ceiling on num_ctx). Longer ones often use attention shortcuts (sliding-window
or hybrid local/global attention) so that very long context does not get prohibitively
expensive. You do not configure this; it is baked into the model. It just explains how
some models offer 128K context without enormous cost.


# Giving models tools: function calling, agents, and MCP

A model on its own only reads text and predicts text. It cannot check today's date,
search a database, send an email, or run code. Tool use is the layer that lets a model
reach outside itself and act. These terms build on each other.

## Function calling (tool use)

The base capability. You describe some functions to the model (their names, what they
do, what inputs they take). When the model decides it needs one, instead of answering
in prose it outputs a structured request to call that function, for example "call
get_weather with city = Austin." Your code sees that request, actually runs the
function, and feeds the result back into the model, which then continues.

Key point: the model never runs anything itself. It only emits a request saying which
tool to call and with what arguments. Your code does the real work and returns the
answer. The model is the decider, not the doer.

Use case: letting a model answer with live or private data (weather, your files, a
calculation) instead of only what is baked into its weights.

## Agents

An agent is what you get when you put tool use in a loop and give the model a goal.
Instead of one tool call, the model can call a tool, see the result, decide on the
next action, call another tool, and keep going until the goal is met. The loop is the
defining feature: model decides, tool runs, result goes back, model decides again.

A plain model answers in one shot. An agent works toward an outcome over multiple
steps, choosing its own actions along the way.

Use case: multi-step tasks where the steps are not known in advance, such as "find the
highest severity finding, look up its CVE, and draft a summary," where each step
depends on the last.

Note: agents need guardrails. A loop that can take actions can loop forever, take a
wrong action, or be steered off course by malicious input. Bounding the steps and
validating each action before running it is part of building one.

## MCP (model context protocol)

MCP is a standard for how a model connects to tools and data sources. Function calling
defines that a model can call tools; MCP defines a common way to expose those tools so
any compatible model can use them without custom glue for each one.

Think of it like a universal plug. Before MCP, wiring a model to your files, your
database, or an external service meant bespoke integration each time. MCP gives a
shared format: a tool provider runs an "MCP server" exposing its capabilities, and any
"MCP client" (the model's side) can connect and use them. Write the integration once,
any MCP-aware model can use it.

Use case: connecting a model to real systems (file systems, GitHub, databases,
internal APIs) through one standard interface instead of one-off code per tool.

## How they stack

These are layers, not alternatives:

  function calling : the model can request a tool
  agent            : tool requests in a loop, working toward a goal
  MCP              : a standard way to expose tools so any model can use them

The model underneath is still just predicting tokens. Tool use is the scaffolding
that turns those predictions into a request to act, an agent turns that into a
sequence of actions, and MCP standardizes how the tools on the other end are wired in.
