# Stickney

This repo contains the code for both containerization and deployment of a vLLM instance, it is part of a larger personal project.

The main goal of this repo is to provide 3 basic features over the standard deployment with VLLM´s base docker image:

- CPU inference (GPU also)
- Change model being used for inference in the fly
- A gradio app for testing purposes

While it is true that VLLM does not support model parallelism like other options (such as NVIDIA Triton Inference Server), this repo includes a workaround to change the model at inference time. However, the drawback is that the process running vllm will be finished. This is managed by using [Supervisor](https://supervisord.org/introduction.html) and a REST-API called `administrator`.

This project is intended to be used as a tool to deploy a set of models by using a `hub-repository` either custom or public, like [HuggingFace](https://huggingface.co/models). It allows quick testing reducing the need of creating more than one artifact's replicas. It can still be used in production, but as said earlier: this will not allow model parallelism: all users will have access to the same model.

IMPORTANT: Performance issues may arise, specially in CPU scenarios where of cores is needed.

- For CPU features please check: [https://docs.vllm.ai/en/stable/getting_started/installation/cpu/index.html#supported-features](https://docs.vllm.ai/en/stable/getting_started/installation/cpu/index.html#supported-features)
- For the VLLM list of supported models please check: [https://docs.vllm.ai/en/stable/models/supported_models.html#list-of-text-only-language-models](https://docs.vllm.ai/en/stable/models/supported_models.html#list-of-text-only-language-models)

#### Project Status: Active [WIP]

### Technologies
* Language: Python 3.10.12
* Dependencies: PIP
* Tokenization Framework: Huggingface
* Inference Engine: VLLM
* Hardware: CPU and GPU
* Model Serving Strategy: FastAPI/Uvicorn
* Container: Docker
* Target Platform: Kubernetes, Docker-Compose, Docker
* Model Repository: MinIO with Datashim

## 🛠 Getting Started

The application exposes three ports:
- 7860 (Gradio interface)
- 8000 (VLLM)
- 9000 (Administrator)

You can just pull the image to start working:

```bash
docker run -it --rm -p 8000:8000 -p 7860:7860 -e RUN_GRADIO='true' -e API_KEY='EMPTY' juampahc/stickney-cpu:latest
```

Once executed, both VLLM and gradio interface will be accessible in your local network. Please, note that if no api_key is needed you need to specify it with `'EMPTY'`. The container does not contain any model, you need to specify the configuration by either:

- using environment variables
- providing an .env file that should be mounted as `/workspace/stickney/.env` (although the application uses relative path)

The application will load default configuration when not provided. Please note that variables present in configuration file will override those passed by environment variables. Here are all the possible options available for configuration (and their default values):

```bash
CONFIG_FILE='./env'
RUN_GRADIO='false'
API_KEY='helloworld'
MODEL_ID='Qwen/Qwen2.5-0.5B-Instruct'
```

Feel free to pass the required arguments to vllm with the run command:

```bash
docker run -it --rm -p 8000:8000 -p 7860:7860 -e RUN_GRADIO='true' -e API_KEY='EMPTY' juampahc/stickney-cpu:latest --task=generate
```

For more information about the arguments, check the [docs](https://docs.vllm.ai/en/stable/serving/openai_compatible_server.html#cli-reference).

Note that there is also a cpu image with AVX512 ISA disabled in case support of them is absent in your processor:

```bash
docker run -it --rm -p 8000:8000 -p 7860:7860 -e RUN_GRADIO='true' -e API_KEY='EMPTY' juampahc/stickney-cpuz:latest
```

For using minIO as an s3 privisioner we first need to install an CSI driver comptaible with s3. I will use ...