import os
import json
import re
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

# ================================================================================================
# Import your custom configs
# ================================================================================================
from config import (
    AZURE_DEPLOYMENT, AZURE_API_VERSION, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY,
    LLM_TEMPERATURE, LLM_MAX_RETRIES, LLM_MAX_TOKENS
)

# ================================================================================================
# Parser for llm output
# ================================================================================================

class SafeJSONParser:
    """Simple JSON parser that handles common LLM output formats"""
    
    def parse(self, text: str) -> Dict[str, Any]:
            raw = text.strip()

            # ----------------------------------------------
            # 1. Extract JSON from fenced code blocks
            # ----------------------------------------------
            if "```json" in raw:
                try:
                    raw = raw.split("```json")[1].split("```")[0].strip()
                except:
                    pass
            elif "```" in raw:
                try:
                    raw = raw.split("```")[1].split("```")[0].strip()
                except:
                    pass

            # ----------------------------------------------
            # 2. Try direct JSON parse
            # ----------------------------------------------
            try:
                return json.loads(raw)
            except:
                pass

            # ----------------------------------------------
            # 3. Try regex extraction of JSON object
            # ----------------------------------------------
            match = re.search(r"\{[\s\S]*\}", raw)
            if match:
                json_candidate = match.group(0)
                try:
                    return json.loads(json_candidate)
                except:
                    pass

            # ----------------------------------------------
            # 4. Clean trailing commas — regex cleanup
            #    Handles ", }", ",   }", ",]", ",   ]"
            # ----------------------------------------------

            cleaned = re.sub(r",\s*}", "}", raw)      # Remove trailing commas before }
            cleaned = re.sub(r",\s*]", "]", cleaned)  # Remove trailing commas before ]

            # ----------------------------------------------
            # 5. Additional cleanup — direct replace
            #    Handles exact ",}" and ",]"
            # ----------------------------------------------
            
            cleaned = cleaned.replace(",}", "}").replace(",]", "]")

            # Try parsing after cleanup
            try:
                return json.loads(cleaned)
            except:
                pass

            # ----------------------------------------------
            # 6. Final failure with verbose error report
            # ----------------------------------------------
            
            raise ValueError(
                "\n❌ LLM returned invalid JSON.\n"
                "-------- RAW LLM OUTPUT --------\n"
                f"{text}\n"
                "--------------------------------\n"
                "JSON extraction failed. Consider improving the prompt or parser."
            )

# ================================================================================================
# Generalized LLM client
# ================================================================================================

class LLMClient:
    """
    LLM client for any task
    """
    
    def __init__(
        self, 
        provider: str = "azure",
        deployment_name: Optional[str] = None,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        api_version: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_retries: Optional[int] = None,
        max_tokens: Optional[int] = None
    ):
        """
        Initialize LLM client with full control over configuration
        
        Args:
            provider: "azure" or "openai"
            deployment_name: Azure deployment name (for Azure)
            api_key: API key for the provider
            endpoint: Endpoint URL (for Azure)
            api_version: API version (for Azure)
            model: Model name (for OpenAI)
            temperature: LLM temperature
            max_retries: Number of retries
            max_tokens: Maximum tokens in response (Optional - some models don't support this)
        """
        self.provider = provider.lower()
        self.json_parser = SafeJSONParser()
        
        # Use provided values or fall back to config
        self.deployment_name = deployment_name or AZURE_DEPLOYMENT
        self.api_key = api_key or AZURE_OPENAI_API_KEY
        self.endpoint = endpoint or AZURE_OPENAI_ENDPOINT
        self.api_version = api_version or AZURE_API_VERSION
        self.model = model or "gpt-4"
        self.temperature = temperature if temperature is not None else LLM_TEMPERATURE
        self.max_retries = max_retries if max_retries is not None else LLM_MAX_RETRIES
        self.max_tokens = max_tokens  # Keep as None if not provided
        
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the LLM based on provider and configuration"""
        common_kwargs = {
            "temperature": self.temperature,
            "max_retries": self.max_retries,
        }
        
        # Only add max_tokens if it's provided (not None)
        if self.max_tokens is not None:
            common_kwargs["max_tokens"] = self.max_tokens
        
        if self.provider == "azure":
            # Validate required Azure parameters
            if not self.api_key:
                raise ValueError("Azure API key is required")
            if not self.deployment_name:
                raise ValueError("Azure deployment name is required")
            
            return AzureChatOpenAI(
                azure_deployment=self.deployment_name,
                api_version=self.api_version,
                azure_endpoint=self.endpoint,
                api_key=self.api_key,
                #response_format={ "type": "json_object" },
                **common_kwargs
            )
        else:  # openai
            if not self.api_key:
                raise ValueError("OpenAI API key is required")
                
            return ChatOpenAI(
                model=self.model,
                api_key=self.api_key,
                **common_kwargs
            )
    
    def call(self, system_prompt: str, user_prompt: str, template_format:Optional[str]=None, **kwargs) -> str:
        """
        Simple LLM call that returns text
        
        Args:
            system_prompt: System instructions
            user_prompt: User message with {variables}
            **kwargs: Variables to fill in the user_prompt
            
        Returns:
            Text response from LLM
        """
        
        # system_msg = SystemMessagePromptTemplate.from_template(system_prompt, template_format=template_format)
        # user_msg = HumanMessagePromptTemplate.from_template(user_prompt,template_format=template_format)
        
        if template_format:
            system_msg = SystemMessagePromptTemplate.from_template(system_prompt,template_format=template_format)
            user_msg = HumanMessagePromptTemplate.from_template(user_prompt,template_format=template_format)
        else:
            system_msg = SystemMessagePromptTemplate.from_template(system_prompt)
            user_msg = HumanMessagePromptTemplate.from_template(user_prompt)

        chat_prompt = ChatPromptTemplate.from_messages([system_msg, user_msg])
        
        chain = chat_prompt | self.llm
        response = chain.invoke(kwargs)
        return response.content
    
    def call_json(self, system_prompt: str, user_prompt: str, template_format:Optional[str]=None, **kwargs) -> Dict[str, Any]:
        """
        LLM call that returns parsed JSON
        
        Args:
            system_prompt: System instructions
            user_prompt: User message with {variables} with output json format
            **kwargs: Variables to fill in the user_prompt
            
        Returns:
            Parsed JSON response
        """

        # system_msg = SystemMessagePromptTemplate.from_template(system_prompt,template_format=template_format)
        # user_msg = HumanMessagePromptTemplate.from_template(user_prompt,template_format=template_format)
        if template_format:
            system_msg = SystemMessagePromptTemplate.from_template(system_prompt,template_format=template_format)
            user_msg = HumanMessagePromptTemplate.from_template(user_prompt,template_format=template_format)
        else:
            system_msg = SystemMessagePromptTemplate.from_template(system_prompt)
            user_msg = HumanMessagePromptTemplate.from_template(user_prompt)

        chat_prompt = ChatPromptTemplate.from_messages([system_msg, user_msg])
        
        chain = chat_prompt | self.llm
        response = chain.invoke(kwargs)
        
        return json.loads(response.content)
    
    def call_jsonr(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        LLM call that returns parsed JSON.
        We perform Python-side formatting and then send raw messages so no Jinja parsing occurs.
        """
        # Fill variables in user_prompt (if any)
        user_prompt_filled = user_prompt

        system_message = SystemMessage(content=system_prompt)
        human_message = HumanMessage(content=user_prompt_filled)

        # Call the LLM
        try:
            result = self.llm.invoke([system_message, human_message])
        except AttributeError:
            result = self.llm([system_message, human_message])
        except Exception:
            raise

        # Extract text (same logic as above)
        text = None
        if hasattr(result, "content"):
            text = result.content
        elif isinstance(result, (list, tuple)) and len(result) and hasattr(result[0], "content"):
            text = result[0].content
        elif hasattr(result, "generations"):
            try:
                text = result.generations[0][0].text
            except Exception:
                text = None
        elif hasattr(result, "choices"):
            try:
                text = result.choices[0].message["content"]
            except Exception:
                text = None

        if text is None:
            text = str(result)

        # Parse JSON using your SafeJSONParser
        return self.json_parser.parse(text)
    
    def create_chain(self, system_prompt: str, user_prompt: str, return_json: bool = False, template_format:Optional[str]=None):
        """
        Create a reusable chain for multiple calls
        
        Args:
            system_prompt: System instructions
            user_prompt: User message template (should contain JSON format instructions if return_json=True)
            return_json: Whether to parse output as JSON
            
        Returns:
            Chain function that takes kwargs and returns response
        """
        
        # system_msg = SystemMessagePromptTemplate.from_template(system_prompt,template_format=template_format)
        # user_msg = HumanMessagePromptTemplate.from_template(user_prompt,template_format=template_format)

        if template_format:
            system_msg = SystemMessagePromptTemplate.from_template(system_prompt,template_format=template_format)
            user_msg = HumanMessagePromptTemplate.from_template(user_prompt,template_format=template_format)
        else:
            system_msg = SystemMessagePromptTemplate.from_template(system_prompt)
            user_msg = HumanMessagePromptTemplate.from_template(user_prompt)

        chat_prompt = ChatPromptTemplate.from_messages([system_msg, user_msg])
        
        chain = chat_prompt | self.llm
        
        if return_json:
            def json_chain(kwargs):
                response = chain.invoke(kwargs)
                return self.json_parser.parse(response.content)
            return json_chain
        else:
            def text_chain(kwargs):
                response = chain.invoke(kwargs)
                return response.content
            return text_chain
        
    def update_config(self, **kwargs):
        """Update configuration and reinitialize LLM"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.llm = self._initialize_llm()

# ================================================================================================
# Factory functions for common use cases
# ================================================================================================

def create_azure_client(
    deployment_name: Optional[str] = None,
    api_key: Optional[str] = None,
    endpoint: Optional[str] = None,
    api_version: Optional[str] = None,
    temperature: Optional[float] = None,
    max_retries: Optional[int] = None,
    max_tokens: Optional[int] = None
) -> LLMClient:
    """Create an Azure OpenAI client"""
    return LLMClient(
        provider="azure",
        deployment_name=deployment_name,
        api_key=api_key,
        endpoint=endpoint,
        api_version=api_version,
        temperature=temperature,
        max_retries=max_retries,
        max_tokens=max_tokens
    )

def create_openai_client(
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    temperature: Optional[float] = None,
    max_retries: Optional[int] = None,
    max_tokens: Optional[int] = None
) -> LLMClient:
    """Create an OpenAI client"""
    return LLMClient(
        provider="openai",
        model=model,
        api_key=api_key,
        temperature=temperature,
        max_retries=max_retries,
        max_tokens=max_tokens
    )


# ================================================================================================
# Default instances using config
# ================================================================================================

# Create default client WITHOUT max_tokens since your model doesn't support it
default_azure_client = create_azure_client(max_tokens=None)
default_openai_client = create_openai_client()
default_client = default_azure_client  # Default is Azure client