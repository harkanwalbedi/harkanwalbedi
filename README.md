Staff Forward Deployed AI Engineer at Google in Seattle. I work on low-latency LLM inference and production AI agents.

**Merged upstream**

- **[ggml-org/llama.cpp #30779](https://github.com/ggml-org/llama.cpp/pull/30779)**: `llama-server` now visits parent slots before their child slots, so requests that share a prompt prefix no longer need a third forward pass. Released in `b12188`.
- **[AI-Hypercomputer/maxdiffusion #476](https://github.com/AI-Hypercomputer/maxdiffusion/pull/476)**: skips the CUDA-only `nvidia-cuda-cccl` dependency on macOS, where no wheels exist, so local installs no longer fail on Apple Silicon.

**Writing**

- [Inside System 1 Models](https://harkanwalbedi.medium.com/inside-system-1-models-e36c0b30c8a9): how a transformer stops writing text and starts providing calibrated decisions.
- [Thinking, Fast and Slow for Production Agents](https://harkanwalbedi.medium.com/thinking-fast-and-slow-for-production-agents-03e5d0f87cc2): pairing open-weights System 1 decision models with an LLM so every model plays to its strengths.

[Website](https://harkanwalbedi.github.io) · [Medium](https://medium.com/@harkanwalbedi) · [LinkedIn](https://www.linkedin.com/in/harkanwalbedi/)
