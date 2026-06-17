from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

from tomorrow.conf import settings
from tomorrow.models.constants import ModelType


def get_model() -> ChatHuggingFace:
    model_config = settings.MODEL.get(ModelType.HUGGINGFACE, {})
    llm = HuggingFaceEndpoint(
        endpoint_url=model_config.get("url"),
        repo_id=model_config.get("model"),
        task="text-generation",
        huggingfacehub_api_token=model_config.get("api_key"),
        temperature=model_config.get("temperature", 0.1),
    )
    return ChatHuggingFace(llm=llm)
