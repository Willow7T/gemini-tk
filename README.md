# Running Application
Running the application was kept to be the same as the demo.
The original start repository can be found [here](https://github.com/Arize-ai/gemini-hackathon).

# Prerequisites

- Python 3.10–3.12
- [uv](https://docs.astral.sh/uv/)
- Google auth for Gemini: either `GOOGLE_API_KEY` **or** Vertex (`gcloud auth application-default login` + project/location)
- Phoenix Cloud API key ([Phoenix](https://app.phoenix.arize.com))

# 10-minute quickstart

1. **Clone and install**
  ```bash
   cd gemini-hackathon
   cp .env.example .env
   # Edit .env: PHOENIX_API_KEY, PHOENIX_COLLECTOR_ENDPOINT (Hostname with /s/...), and either GOOGLE_API_KEY or Vertex settings.
   uv sync
  ```
2. **Run a traced shopping turn**
  ```bash
   make run MESSAGE='Find a floral dress in size M'
  ```
3. **Open Phoenix** — project name defaults to `PHOENIX_PROJECT_NAME` (`gemini-hackathon`). Confirm LLM and tool spans appear.
4. **(Optional) ADK CLI**
  ```bash
   make run-adk
   # Find a floral dress in size M
  ```
   This path also loads `.env` and initializes Phoenix tracing.


# Inspiration
Agriculture feeds the world, but disease silently destroys up to 40% of global crop yields every year — costing farmers over $220 billion annually. What struck us wasn't just the scale of the problem, but the asymmetry of it: a farmer in a rural field has no access to the agronomists, labs, or diagnostic tools that could save their harvest.
What pushed us further was a frustration with how most AI tools are deployed. They're trained once, shipped, and left to quietly degrade in production. The moment a new disease strain emerges or image conditions shift, the model falls behind and nobody knows until crops are already failing.
The convergence of PyTorch, Google Cloud Gemini, and Arize Phoenix made us believe a truly self-improving pipeline was achievable within a hackathon. That belief became ArcticPlant AI.

# What it does
ArcticPlant AI is an end-to-end plant disease detection system that diagnoses diseases from leaf photos and gets smarter with every prediction.
A farmer uploads a photo. Our PyTorch CNN (MobilenetV3Large weighted with ImageNet1kV2) trained on 54,306 images across 38 disease classes identifies the disease with over 89% accuracy. That result flows to Google Cloud's Gemini via MCP, which transforms a raw label into a full natural-language diagnosis: disease name, severity, probable causes, and actionable treatment steps. Arize Phoenix monitors every prediction in the background, tracks model confidence and embedding drift, and automatically triggers a retraining cycle when performance degrades, without human intervention.
It's not just a classifier. It's a system that learn over time.

# How we built it
We started with the model. Using the PlantVillage dataset from Kaggle, we trained a custom MobileNet-based CNN in PyTorch with data augmentation such as random flips, rotations, and color jitter to improve robustness against real-world image variation.
From there we built the intelligence layer. We integrated Gemini 2.5 Flash via MCP (Model Context Protocol), passing structured CNN outputs into Gemini as context so it could generate rich, human-readable diagnoses without losing the precision of the underlying classification.
The final piece was the self-improving loop. We wired Arize Phoenix into the pipeline as our observability backbone. Phoenix logs every prediction, monitors embedding drift, and flags degradation automatically and triggering retraining and closing the feedback loop with no manual steps required.

# Challenges we ran into
Orchestrating three different paradigms. PyTorch is imperative and research-oriented, Gemini is conversational and probabilistic, Arize Phoenix is observability-focused. Making them work as one coherent system required careful design of the data contracts between each stage.
Speed vs. depth. Gemini's richer diagnostic outputs take longer than a simple label, and farmers in the field need fast answers. We had to tune our MCP prompts carefully to get concise, actionable responses without sacrificing the quality that makes the tool genuinely useful.
Calibrating the retraining trigger. Defining the right confidence threshold in Phoenix was harder than expected. Too sensitive and you're retraining constantly on noise; too conservative and you miss real drift. We landed on a confidence-window approach that felt robust, but it's something we'd refine further with real-world data.

# Accomplishments that we're proud of
We're proud that we didn't just build a demo we built a production-ready foundation. The self-improving loop works end-to-end: Phoenix detects drift, triggers retraining, and the model updates without a single manual step. That's the part that felt genuinely hard and genuinely new.
We're proud of the Gemini MCP integration. Turning a CNN classification into a contextual, human-readable diagnosis complete with treatment recommendations is the difference between a research tool and something a farmer can actually use.
And we're proud of the 89%+ accuracy on 38 disease classes across 14 crop species. Starting from a Kaggle dataset and reaching that level of reliability within a hackathon, with a pipeline that can keep improving after deployment, felt like the right proof point for what ArcticPlant AI is meant to be.





