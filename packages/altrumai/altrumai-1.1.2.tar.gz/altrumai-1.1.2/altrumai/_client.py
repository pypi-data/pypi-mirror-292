import httpx
from typing import Literal, List, Optional, Dict, Any, Generator
from tenacity import retry, wait_fixed, stop_after_attempt, retry_if_exception_type
from ._models import ChatCompletionMessage, EmbeddingsModel, ChatCompletionModel, PrivacyModel, ModerationsModel, CompetitorsModel, RestrictToTopicModel, SensitiveTopicsModel, DrugsCheckModel, DetectSecretsModel, CheckProfanityModel, GibberishTextModel, FinancialToneModel, NSFWTextModel, UnusualPromptModel, EvaluateResponseModel, EvaluatePolitenessModel, LLMCriticModel, MetricDescription, TextToSpeechModel, SpeechToTextModel, QARelevanceModel, DetectHallucinationsModel, DetectPromptInjectionModel
import logging

class BaseClient():
    """
    Base client for interacting with the AltrumAI API.

    Attributes:
        api_key (str): The API key for authentication.
        workspace (str): The workspace ID.
        base_url (str): The base URL for the API.
        headers (dict): The headers for HTTP requests.
    """
    def __init__(self, api_key: str, workspace: str, base_url: str = "https://api.altrum.ai/v1"):
        """
        Initializes the BaseClient with the provided API key and workspace.

        Args:
            api_key (str): The API key for authentication.
            workspace (str): The workspace ID.
            base_url (str): The base URL for the API.

        Raises:
            ValueError: If api_key or workspace is not provided.
        """
        # Required initialisations
        self.api_key = api_key
        self.workspace = workspace
        self.base_url = base_url
        self.headers = {"API-Key": f"{self.api_key}","Workspace-ID": self.workspace,"Connection": "keep-alive"}
        # Required validations
        if not self.api_key:
            raise ValueError("Please provide a valid AltrumAI API Key.")
        if not workspace:
            raise ValueError("Please provide a valid workspace ID.")

    @retry(
        wait=wait_fixed(2),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(httpx.RequestError),
    )
    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None) -> httpx.Response:
        """
        Performs a GET request to the specified endpoint.

        Args:
            endpoint (str): The API endpoint.
            params (dict, optional): The query parameters for the request.

        Returns:
            httpx.Response: The response from the server.

        Raises:
            RequestError: If there is a request error.
            HTTPStatusError: If the response status code indicates an error.
        """
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.get(f"{self.base_url}{endpoint}", params=params, headers=self.headers)
                response.raise_for_status()
                return response
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            raise

    @retry(
        wait=wait_fixed(2),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(httpx.RequestError),
    )
    def _post(self, endpoint: str, data: Dict[str, Any], timeout: Optional[float] = 60.0) -> httpx.Response:
        """
        Performs a POST request to the specified endpoint.

        Args:
            endpoint (str): The API endpoint.
            data (dict): The JSON payload for the request.

        Returns:
            httpx.Response: The response from the server.

        Raises:
            RequestError: If there is a request error.
            HTTPStatusError: If the response status code indicates an error.
        """
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.post(f"{self.base_url}{endpoint}", json=data, headers=self.headers)
                response.raise_for_status()
                return response
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            raise

    @retry(
        wait=wait_fixed(2),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(httpx.RequestError),
    )
    def _stream(self, endpoint: str, data: Dict[str, Any], timeout: Optional[float] = 60.0) -> Generator[str, None, None]:
        """
        Streams data asynchronously from the specified endpoint.

        Args:
            endpoint (str): The API endpoint.
            data (dict): The JSON payload for the request.

        Yields:
            str: The streamed data chunks.

        Raises:
            RequestError: If there is a request error.
            HTTPStatusError: If the response status code indicates an error.
        """
        try:
            with httpx.Client(timeout=timeout).stream('POST', f"{self.base_url}{endpoint}", json=data, headers=self.headers) as response:
                response.raise_for_status()
                for chunk in response.iter_text():
                    yield chunk
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            raise


class AltrumAI(BaseClient):
    def __init__(self, api_key: str, workspace: str, base_url: str = "https://api.altrum.ai/v1"):
        super().__init__(api_key, workspace, base_url)

    def chat_completion(self, model: Literal["mixtral-7b", "mistral-7b-chat", "zephyr-7b-alpha", "mistral-7b-chat-trt-llm"], messages:  List[ChatCompletionMessage], stream: bool = False, timeout: Optional[float] = None):
        """Generate streaming chat completions using a specified model."""
        data = ChatCompletionModel(model=model, messages=messages, stream=stream).model_dump()
        if stream:
            return self._stream(endpoint="/chat/completions", data=data, timeout=timeout)
        return self._post("/chat/completions", data, timeout=timeout)

    def create_embeddings(self, model: Literal["nomic-embed-v1.5"], inputs: List[str], dimensions: Literal[64, 128, 256, 512, 768], encoding_format: Literal["float", "base64"] = "float", timeout: Optional[float] = None):
        """Generate vector embeddings for a give text or list of texts"""
        data = EmbeddingsModel(model=model, inputs=inputs, dimensions=dimensions, encoding_format=encoding_format).dict()
        response = self._post("/embeddings", data, timeout=timeout)
        return response

    def privacy(self, input: str, compliance: List[str], custom: List[str], timeout: Optional[float] = None) -> httpx.Response:
        """Give list of privacy entities for given input text wrt given compliance and customs"""
        payload = PrivacyModel(input=input, compliance=compliance, custom=custom).model_dump()
        return self._post("/privacy", payload, timeout=timeout)

    def moderations(self, input: str, guardrails: List[str], timeout: Optional[float] = None) -> httpx.Response:
        """Detect toxicity and bias for moderations."""
        payload = ModerationsModel(input=input, guardrails=guardrails).model_dump()
        return self._post("/moderations", payload, timeout=timeout)

    def models(self, timeout: Optional[float] = None) -> httpx.Response:
        """Retrieve list of all available models"""
        return self._get("/models", timeout=timeout)

    def ping(self, timeout: Optional[float] = None) -> httpx.Response:
        """Verify WorkspaceID and API Key"""
        return self._get("/ping", timeout=timeout)

    def deployments(self, timeout: Optional[float] = None) -> httpx.Response:
        """Retrieve list of all the deployed models"""
        return self._get("/workspace/deployments", timeout=timeout)

    def check_competitor(self, input: str, competitors: List[str], timeout: Optional[float] = None) -> httpx.Response:
        """Detect competitors"""
        payload = CompetitorsModel(input=input, competitors=competitors).model_dump()
        return self._post("/check_competitor", payload, timeout=timeout)

    def restrict_to_topic(self, input: str, valid_topics: List[str], invalid_topics: List[str], threshold: float, timeout: Optional[float] = None) -> httpx.Response:
        """Restrict input to specific topics"""
        payload = RestrictToTopicModel(input=input, valid_topics=valid_topics, invalid_topics=invalid_topics, threshold=threshold).model_dump()
        return self._post("/restrict_to_topic", payload, timeout=timeout)

    def sensitive_topic(self, input: str, sensitive_topics: List[str], threshold: float, timeout: Optional[float] = None) -> httpx.Response:
        """Check for sensitive topics"""
        payload = SensitiveTopicsModel(input=input, sensitive_topics=sensitive_topics, threshold=threshold).model_dump()
        return self._post("/sensitive_topic", payload, timeout=timeout)

    def drugs_check(self, input: str, drugs: List[str], timeout: Optional[float] = None) -> httpx.Response:
        """Check for drugs in input"""
        payload = DrugsCheckModel(input=input, drugs=drugs).model_dump()
        return self._post("/drugs_check", payload, timeout=timeout)

    def detect_secrets(self, input: str, timeout: Optional[float] = None) -> httpx.Response:
        """Detect secrets in input"""
        payload = DetectSecretsModel(input=input).model_dump()
        return self._post("/detect_secrets", payload, timeout=timeout)

    def check_profanity(self, input: str, timeout: Optional[float] = None) -> httpx.Response:
        """Check for profanity in input"""
        payload = CheckProfanityModel(input=input).model_dump()
        return self._post("/check_profanity", payload, timeout=timeout)

    def gibberish_text(self, input: str, method: str, timeout: Optional[float] = None) -> httpx.Response:
        """Check for gibberish text in input"""
        payload = GibberishTextModel(input=input, method=method).model_dump()
        return self._post("/gibberish_text", payload, timeout=timeout)

    def financial_tone(self, input: str, timeout: Optional[float] = None) -> httpx.Response:
        """Check financial tone in input"""
        payload = FinancialToneModel(input=input).model_dump()
        return self._post("/financial_tone", payload, timeout=timeout)

    def nsfw_text(self, input: str, method: Literal["full", "sentence"], timeout: Optional[float] = None) -> httpx.Response:
        """Check for NSFW content in input"""
        payload = NSFWTextModel(input=input, method=method).model_dump()
        return self._post("/nsfw_text", payload, timeout=timeout)

    def unusual_prompt(self, input: str, timeout: Optional[float] = None) -> httpx.Response:
        """Check for unusual prompts in input"""
        payload = UnusualPromptModel(input=input).model_dump()
        return self._post("/unusual_prompt", payload, timeout=timeout)

    def evaluate_response(self, question: str, answer: str, timeout: Optional[float] = None) -> httpx.Response:
        """Evaluate the response for a given question"""
        payload = EvaluateResponseModel(question=question, answer=answer).model_dump()
        return self._post("/evaluate_response", payload, timeout=timeout)

    def evaluate_politeness(self, input: str, timeout: Optional[float] = None) -> httpx.Response:
        """Evaluate the politeness of the input"""
        payload = EvaluatePolitenessModel(input=input).model_dump()
        return self._post("/evaluate_politeness", payload, timeout=timeout)

    def llm_critic(self, input: str, metrics: Dict[str, MetricDescription], max_score: int, timeout: Optional[float] = None) -> httpx.Response:
        """Evaluate the input based on provided metrics"""
        payload = LLMCriticModel(input=input, metrics=metrics, max_score=max_score).model_dump()
        return self._post("/llm_critic", payload, timeout=timeout)

    def text_to_speech(self, input: str, timeout: Optional[float] = None) -> httpx.Response:
        """Convert text to speech"""
        payload = TextToSpeechModel(input=input).model_dump()
        return self._post("/text_to_speech", payload, timeout=timeout)

    def speech_to_text(self, input: str, timeout: Optional[float] = None) -> httpx.Response:
        """Convert speech to text"""
        payload = SpeechToTextModel(input=input).model_dump()
        return self._post("/speech_to_text", payload, timeout=timeout)

    def qa_relevance_llm(self, question: str, answer: str, timeout: Optional[float] = None) -> httpx.Response:
        """Evaluate the response for a given question"""
        payload = QARelevanceModel(question=question, answer=answer).model_dump()
        return self._post("/qa_relevance_llm", payload, timeout=timeout)

    def detect_hallucinations(self, input: str, response: str, timeout: Optional[float] = None) -> httpx.Response:
        """Detect hallucinations in the given response."""
        payload = DetectHallucinationsModel(input=input, response=response).model_dump()
        return self._post("/detect_hallucinations", payload, timeout=timeout)

    def detect_prompt_injection(self, input: str, timeout: Optional[float] = None) -> httpx.Response:
        """Detect prompt injection attempts."""
        payload = DetectPromptInjectionModel(input=input).model_dump()
        return self._post("/detect_prompt_injection", payload, timeout=timeout)

class AsyncBaseClient(BaseClient):
    def __init__(self, api_key: str, workspace: str, base_url: str = "https://api.altrum.ai/v1"):
        super().__init__(api_key, workspace, base_url)

    @retry(
        wait=wait_fixed(2),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(httpx.RequestError),
    )
    async def _aget(self, endpoint: str, params: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None) -> httpx.Response:
        """
        Performs an asynchronous GET request to the specified endpoint.

        Args:
            endpoint (str): The API endpoint.
            params (dict, optional): The query parameters for the request.

        Returns:
            httpx.Response: The response from the server.

        Raises:
            RequestError: If there is a request error.
            HTTPStatusError: If the response status code indicates an error.
        """
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(f"{self.base_url}{endpoint}", params=params, headers=self.headers)
                response.raise_for_status()
                return response
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            raise

    @retry(
        wait=wait_fixed(2),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(httpx.RequestError),
    )
    async def _apost(self, endpoint: str, data: Dict[str, Any], timeout: Optional[float] = None) -> httpx.Response:
        """
        Performs an asynchronous POST request to the specified endpoint.

        Args:
            endpoint (str): The API endpoint.
            data (dict): The JSON payload for the request.

        Returns:
            httpx.Response: The response from the server.

        Raises:
            RequestError: If there is a request error.
            HTTPStatusError: If the response status code indicates an error.
        """
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(f"{self.base_url}{endpoint}", json=data, headers=self.headers)
                response.raise_for_status()
                return response
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            raise

    @retry(
        wait=wait_fixed(2),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(httpx.RequestError),
    )
    async def _astream(self, endpoint: str, data: Dict[str, Any], timeout: Optional[float] = None) -> Generator[str, None, None]:
        """
        Streams data asynchronously from the specified endpoint.

        Args:
            endpoint (str): The API endpoint.
            data (dict): The JSON payload for the request.

        Yields:
            str: The streamed data chunks.

        Raises:
            RequestError: If there is a request error.
            HTTPStatusError: If the response status code indicates an error.
        """
        try:
            async with httpx.AsyncClient(timeout=timeout).stream('POST', f"{self.base_url}{endpoint}", json=data, headers=self.headers) as response:
                response.raise_for_status()
                async for chunk in response.aiter_text():
                    yield chunk
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            raise

class AsyncAltrumAI(AsyncBaseClient):
    def __init__(self, api_key: str, workspace: str, base_url: str = "https://api.altrum.ai/v1"):
        super().__init__(api_key, workspace, base_url)

    async def chat_completion(self, model: Literal["mixtral-7b", "mistral-7b-chat", "zephyr-7b-alpha", "mistral-7b-chat-trt-llm"], messages:  List[ChatCompletionMessage], stream: bool = False, timeout: Optional[float] = None):
        """Generate streaming chat completions using a specified model."""
        data = ChatCompletionModel(model=model, messages=messages, stream=stream).model_dump()
        if stream:
            return self._stream(endpoint="/chat/completions", data=data, timeout=timeout)
        return await self._apost("/chat/completions", data, timeout=timeout)

    async def privacy(self, input: str, compliance: List[str], custom: List[str], timeout: Optional[float] = None) -> httpx.Response:
        """Give list of privacy entities for given input text wrt given compliance and customs"""
        payload = PrivacyModel(input=input, compliance=compliance, custom=custom).model_dump()
        return await self._apost("/privacy", payload, timeout=timeout)

    async def moderations(self, input: str, guardrails: List[str], timeout: Optional[float] = None) -> httpx.Response:
        """Detect toxicity and bias for moderations."""
        payload = ModerationsModel(input=input, guardrails=guardrails).model_dump()
        return await self._apost("/moderations", payload, timeout=timeout)

    async def models(self, timeout: Optional[float] = None) -> httpx.Response:
        """Retrieve list of all available models"""
        return await self._aget("/models", timeout=timeout)

    async def ping(self, timeout: Optional[float] = None) -> httpx.Response:
        """Verify WorkspaceID and API Key"""
        return await self._aget("/ping", timeout=timeout)

    async def deployments(self, timeout: Optional[float] = None) -> httpx.Response:
        """Retrieve list of all the deployed models"""
        return await self._aget("/workspace/deployments", timeout=timeout)

    async def create_embeddings(self, model: Literal["nomic-embed-v1.5"], inputs: List[str], dimensions: Literal[64, 128, 256, 512, 768], encoding_format: Literal["float", "base64"] = "float", timeout: Optional[float] = None):
        """Generate vector embeddings for a give text or list of texts"""
        data = EmbeddingsModel(model=model, inputs=inputs, dimensions=dimensions, encoding_format=encoding_format).model_dump()
        return await self._apost("/embeddings", data, timeout=timeout)

    async def check_competitor(self, input: str, competitors: List[str], timeout: Optional[float] = None) -> httpx.Response:
        """Detect competitors"""
        payload = CompetitorsModel(input=input, competitors=competitors).model_dump()
        return await self._apost("/check_competitor", payload, timeout=timeout)

    async def restrict_to_topic(self, input: str, valid_topics: List[str], invalid_topics: List[str], threshold: float, timeout: Optional[float] = None) -> httpx.Response:
        """Restrict input to specific topics"""
        payload = RestrictToTopicModel(input=input, valid_topics=valid_topics, invalid_topics=invalid_topics, threshold=threshold).model_dump()
        return await self._apost("/restrict_to_topic", payload, timeout=timeout)

    async def sensitive_topic(self, input: str, sensitive_topics: List[str], threshold: float, timeout: Optional[float] = None) -> httpx.Response:
        """Check for sensitive topics"""
        payload = SensitiveTopicsModel(input=input, sensitive_topics=sensitive_topics, threshold=threshold).model_dump()
        return await self._apost("/sensitive_topic", payload, timeout=timeout)

    async def drugs_check(self, input: str, drugs: List[str], timeout: Optional[float] = None) -> httpx.Response:
        """Check for drugs in input"""
        payload = DrugsCheckModel(input=input, drugs=drugs).model_dump()
        return await self._apost("/drugs_check", payload, timeout=timeout)

    async def detect_secrets(self, input: str, timeout: Optional[float] = None) -> httpx.Response:
        """Detect secrets in input"""
        payload = DetectSecretsModel(input=input).model_dump()
        return await self._apost("/detect_secrets", payload, timeout=timeout)

    async def check_profanity(self, input: str, timeout: Optional[float] = None) -> httpx.Response:
        """Check for profanity in input"""
        payload = CheckProfanityModel(input=input).model_dump()
        return await self._apost("/check_profanity", payload, timeout=timeout)

    async def gibberish_text(self, input: str, method: str, timeout: Optional[float] = None) -> httpx.Response:
        """Check for gibberish text in input"""
        payload = GibberishTextModel(input=input, method=method).model_dump()
        return await self._apost("/gibberish_text", payload, timeout=timeout)

    async def financial_tone(self, input: str, timeout: Optional[float] = None) -> httpx.Response:
        """Check financial tone in input"""
        payload = FinancialToneModel(input=input).model_dump()
        return await self._apost("/financial_tone", payload, timeout=timeout)

    async def nsfw_text(self, input: str, method: Literal["full", "sentence"], timeout: Optional[float] = None) -> httpx.Response:
        """Check for NSFW content in input"""
        payload = NSFWTextModel(input=input, method=method).model_dump()
        return await self._apost("/nsfw_text", payload, timeout=timeout)

    async def unusual_prompt(self, input: str, timeout: Optional[float] = None) -> httpx.Response:
        """Check for unusual prompts in input"""
        payload = UnusualPromptModel(input=input).model_dump()
        return await self._apost("/unusual_prompt", payload, timeout=timeout)

    async def evaluate_response(self, question: str, answer: str, timeout: Optional[float] = None) -> httpx.Response:
        """Evaluate the response for a given question"""
        payload = EvaluateResponseModel(question=question, answer=answer).model_dump()
        return await self._apost("/evaluate_response", payload, timeout=timeout)

    async def evaluate_politeness(self, input: str, timeout: Optional[float] = None) -> httpx.Response:
        """Evaluate the politeness of the input"""
        payload = EvaluatePolitenessModel(input=input).model_dump()
        return await self._apost("/evaluate_politeness", payload, timeout=timeout)

    async def llm_critic(self, input: str, metrics: Dict[str, MetricDescription], max_score: int, timeout: Optional[float] = None) -> httpx.Response:
        """Evaluate the input based on provided metrics"""
        payload = LLMCriticModel(input=input, metrics=metrics, max_score=max_score).model_dump()
        return await self._apost("/llm_critic", payload, timeout=timeout)

    async def text_to_speech(self, input: str, timeout: Optional[float] = None) -> httpx.Response:
        """Convert text to speech"""
        payload = TextToSpeechModel(input=input).model_dump()
        return await self._apost("/text_to_speech", payload, timeout=timeout)

    async def speech_to_text(self, input: str, timeout: Optional[float] = None) -> httpx.Response:
        """Convert speech to text"""
        payload = SpeechToTextModel(input=input).model_dump()
        return await self._apost("/speech_to_text", payload, timeout=timeout)

    async def qa_relevance_llm(self, question: str, answer: str, timeout: Optional[float] = None) -> httpx.Response:
        """Evaluate the response for a given question"""
        payload = QARelevanceModel(question=question, answer=answer).model_dump()
        return await self._apost("/qa_relevance_llm", payload, timeout=timeout)

    async def detect_hallucinations(self, input: str, response: str, timeout: Optional[float] = None) -> httpx.Response:
        """Detect hallucinations in the given response."""
        payload = DetectHallucinationsModel(input=input, response=response).model_dump()
        return await self._apost("/detect_hallucinations", payload, timeout=timeout)

    async def detect_prompt_injection(self, input: str, timeout: Optional[float] = None) -> httpx.Response:
        """Detect prompt injection attempts."""
        payload = DetectPromptInjectionModel(input=input).model_dump()
        return await self._apost("/detect_prompt_injection", payload, timeout=timeout)


# Suggested Improvements:

# There are several improvements that could be made to this code, some of which are more critical than others. Here's a prioritised list of improvements:

# 1. **Error Handling**: Proper error handling should be implemented, especially for HTTP requests. Currently, the code assumes that HTTP requests will always succeed, which is not always the case. Error handling should include catching exceptions, handling non-200 status codes, and providing meaningful error messages to the user.
# 2. **Code Structure**: The code could be organised better to improve readability and maintainability. Consider splitting the code into multiple modules or classes based on functionality. Additionally, adhering to common Python style conventions (PEP 8) will make the code more consistent and easier to follow.
# 3. **Performance**: Depending on the usage patterns, there may be opportunities to optimise the code for better performance. This could include implementing caching mechanisms, optimising network requests, or reducing unnecessary overhead.
