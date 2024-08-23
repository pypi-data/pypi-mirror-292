from enum import Enum
from pydantic import BaseModel, Field
from typing import Literal, List

class ChatCompletionRole(str, Enum):
    user = 'user'
    assistant = 'assistant'

class ChatCompletionMessage(BaseModel):
    role: ChatCompletionRole
    content: str = Field(..., max_length=5000)

class ChatCompletionModel(BaseModel):
    model: Literal["mixtral-7b", "mistral-7b-chat", "zephyr-7b-alpha", "mistral-7b-chat-trt-llm"]
    messages: List[ChatCompletionMessage]
    stream: bool = False

class EmbeddingsModel(BaseModel):
    model: Literal["nomic-embed-v1.5"]
    inputs: List[str]
    dimensions: Literal[64, 128, 256, 512, 768]
    encoding_format: Literal["float", "base64"] = "float"

class PrivacyModel(BaseModel):
    input: str
    compliance: List[str]
    custom: List[str]

class ModerationsModel(BaseModel):
    input: str
    guardrails: List[str]

class CompetitorsModel(BaseModel):
    input: str
    competitors: List[str]

class RestrictToTopicModel(BaseModel):
    input: str
    valid_topics: List[str]
    invalid_topics: List[str]
    threshold: float

class SensitiveTopicsModel(BaseModel):
    input: str
    sensitive_topics: List[str]
    threshold: float

class DrugsCheckModel(BaseModel):
    input: str
    drugs: List[str]

class DetectSecretsModel(BaseModel):
    input: str

class CheckProfanityModel(BaseModel):
    input: str

class GibberishTextModel(BaseModel):
    input: str
    method: Literal["full", "sentence"]

class FinancialToneModel(BaseModel):
    input: str

class NSFWTextModel(BaseModel):
    input: str
    method: Literal["full", "sentence"]

class UnusualPromptModel(BaseModel):
    input: str

class EvaluateResponseModel(BaseModel):
    question: str
    answer: str

class EvaluatePolitenessModel(BaseModel):
    input: str

class MetricDescription(BaseModel):
    description: str
    threshold: int

class MetricsModel(BaseModel):
    informative: MetricDescription
    coherent: MetricDescription
    concise: MetricDescription
    engaging: MetricDescription

class LLMCriticModel(BaseModel):
    input: str
    metrics: MetricsModel
    max_score: int

class TextToSpeechModel(BaseModel):
    input: str

class SpeechToTextModel(BaseModel):
    input: str

class QARelevanceModel(BaseModel):
    question: str
    answer: str

class DetectHallucinationsModel(BaseModel):
    input: str
    response: str

class DetectPromptInjectionModel(BaseModel):
    input: str
