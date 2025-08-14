"""
AI Provider Abstraction Layer
============================

Supports multiple AI providers including free alternatives to OpenAI
"""

import os
import json
import asyncio
import aiohttp
import requests
from typing import Optional, Dict, List, Any
from abc import ABC, abstractmethod
from dotenv import load_dotenv

load_dotenv()

class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    @abstractmethod
    async def generate_completion(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate text completion from prompt"""
        pass
    
    @abstractmethod
    async def generate_json_completion(self, prompt: str, temperature: float = 0.3) -> Dict:
        """Generate JSON response from prompt"""
        pass

class OllamaProvider(AIProvider):
    """Ollama provider - completely free, runs locally"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        self.base_url = base_url
        self.model = model
        self.available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if Ollama is running and model is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return any(model['name'].startswith(self.model) for model in models)
        except:
            pass
        return False
    
    async def generate_completion(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate completion using Ollama"""
        if not self.available:
            return self._get_mock_response(prompt)
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('response', '')
        except Exception as e:
            print(f"Ollama error: {e}")
            return self._get_mock_response(prompt)
        
        return self._get_mock_response(prompt)
    
    async def generate_json_completion(self, prompt: str, temperature: float = 0.3) -> Dict:
        """Generate JSON completion using Ollama"""
        json_prompt = f"{prompt}\n\nPlease respond with valid JSON only."
        response = await self.generate_completion(json_prompt, temperature)
        
        try:
            # Try to extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
        except:
            pass
        
        # Return mock data if parsing fails
        return self._get_mock_json_response(prompt)
    
    def _get_mock_response(self, prompt: str) -> str:
        """Generate mock response when Ollama is not available"""
        if "email" in prompt.lower():
            return """Subject: Streamline Your Authentication with Descope

Hi [Name],

I noticed your company is working on authentication solutions. Based on your GitHub activity, it looks like you're dealing with some common auth challenges.

Descope can help you implement enterprise-grade authentication in minutes instead of months. Our platform handles SSO, MFA, and user management out of the box.

Would you be interested in a 15-minute demo to see how we can simplify your auth stack?

Best regards,
[Your Name]"""
        
        elif "linkedin" in prompt.lower():
            return "Hi [Name], I saw your company is building auth solutions. Descope can help you implement enterprise SSO in minutes instead of months. Would love to show you a quick demo!"
        
        elif "video" in prompt.lower():
            return """[0:00] Hi [Name], I'm reaching out because I noticed your team is working on authentication.

[0:15] Based on your GitHub repo, it looks like you're building custom auth - that's exactly what Descope helps companies avoid.

[0:30] We've helped 500+ companies implement enterprise-grade authentication in minutes instead of months.

[0:45] I'd love to show you a 15-minute demo of how we can simplify your auth stack. Are you free this week?"""
        
        else:
            return "I understand you're looking for insights about authentication and security challenges. Based on the information provided, this appears to be a company that could benefit from improved identity management solutions."
    
    def _get_mock_json_response(self, prompt: str) -> Dict:
        """Generate mock JSON response"""
        if "github" in prompt.lower() or "signal" in prompt.lower():
            return [
                {
                    "signal_type": "auth_implementation",
                    "description": "Custom JWT implementation with potential security concerns",
                    "severity": 7,
                    "confidence": 0.8
                },
                {
                    "signal_type": "sso_requirement", 
                    "description": "GitHub issues requesting SSO implementation",
                    "severity": 8,
                    "confidence": 0.85
                }
            ]
        return {"response": "Mock JSON response generated"}

class GroqProvider(AIProvider):
    """Groq provider - free tier with good performance"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = "llama3-8b-8192"  # Free model
    
    async def generate_completion(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate completion using Groq"""
        if not self.api_key or self.api_key == "your_groq_api_key_here":
            return OllamaProvider()._get_mock_response(prompt)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": 1024
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['choices'][0]['message']['content']
        except Exception as e:
            print(f"Groq error: {e}")
            return OllamaProvider()._get_mock_response(prompt)
        
        return OllamaProvider()._get_mock_response(prompt)
    
    async def generate_json_completion(self, prompt: str, temperature: float = 0.3) -> Dict:
        """Generate JSON completion using Groq"""
        json_prompt = f"{prompt}\n\nRespond with valid JSON only."
        response = await self.generate_completion(json_prompt, temperature)
        
        try:
            return json.loads(response)
        except:
            return OllamaProvider()._get_mock_json_response(prompt)

class HuggingFaceProvider(AIProvider):
    """Hugging Face provider - free tier available"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api-inference.huggingface.co/models"
        self.model = "microsoft/DialoGPT-large"  # Free model
    
    async def generate_completion(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate completion using Hugging Face"""
        if not self.api_key or self.api_key == "your_hf_api_key_here":
            return OllamaProvider()._get_mock_response(prompt)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "temperature": temperature,
                "max_length": 512
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/{self.model}",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if isinstance(data, list) and len(data) > 0:
                            return data[0].get('generated_text', '')
        except Exception as e:
            print(f"Hugging Face error: {e}")
            return OllamaProvider()._get_mock_response(prompt)
        
        return OllamaProvider()._get_mock_response(prompt)
    
    async def generate_json_completion(self, prompt: str, temperature: float = 0.3) -> Dict:
        """Generate JSON completion using Hugging Face"""
        response = await self.generate_completion(prompt, temperature)
        
        try:
            return json.loads(response)
        except:
            return OllamaProvider()._get_mock_json_response(prompt)

class MockProvider(AIProvider):
    """Mock provider for demonstrations without any API keys"""
    
    async def generate_completion(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate mock completion"""
        return OllamaProvider()._get_mock_response(prompt)
    
    async def generate_json_completion(self, prompt: str, temperature: float = 0.3) -> Dict:
        """Generate mock JSON completion"""
        return OllamaProvider()._get_mock_json_response(prompt)

class AIClient:
    """Main AI client that handles provider selection and fallbacks"""
    
    def __init__(self):
        self.provider = self._initialize_provider()
        print(f"🤖 AI Provider: {type(self.provider).__name__}")
    
    def _initialize_provider(self) -> AIProvider:
        """Initialize the best available AI provider"""
        ai_provider = os.getenv('AI_PROVIDER', 'ollama').lower()
        
        if ai_provider == 'ollama':
            ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
            ollama_model = os.getenv('OLLAMA_MODEL', 'llama2')
            provider = OllamaProvider(ollama_url, ollama_model)
            if provider.available:
                return provider
            else:
                print("⚠️  Ollama not available, falling back to mock responses")
                print("💡 To use Ollama: install from https://ollama.ai and run 'ollama pull llama2'")
        
        elif ai_provider == 'groq':
            groq_key = os.getenv('GROQ_API_KEY')
            if groq_key and groq_key != 'your_groq_api_key_here':
                return GroqProvider(groq_key)
            else:
                print("⚠️  Groq API key not configured")
        
        elif ai_provider == 'huggingface':
            hf_key = os.getenv('HUGGINGFACE_API_KEY')
            if hf_key and hf_key != 'your_hf_api_key_here':
                return HuggingFaceProvider(hf_key)
            else:
                print("⚠️  Hugging Face API key not configured")
        
        elif ai_provider == 'openai':
            # Keep OpenAI support for those who want to use it
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key and openai_key != 'your_openai_api_key_here':
                try:
                    from openai import OpenAI
                    return OpenAIProvider(openai_key)
                except ImportError:
                    print("⚠️  OpenAI package not available")
        
        print("🎭 Using mock responses for demonstration")
        return MockProvider()
    
    async def generate_completion(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate text completion"""
        return await self.provider.generate_completion(prompt, temperature)
    
    async def generate_json_completion(self, prompt: str, temperature: float = 0.3) -> Dict:
        """Generate JSON completion"""
        return await self.provider.generate_json_completion(prompt, temperature)

class OpenAIProvider(AIProvider):
    """OpenAI provider for those who want to use the paid API"""
    
    def __init__(self, api_key: str):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
    
    async def generate_completion(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate completion using OpenAI"""
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        return response.choices[0].message.content
    
    async def generate_json_completion(self, prompt: str, temperature: float = 0.3) -> Dict:
        """Generate JSON completion using OpenAI"""
        response = await self.generate_completion(prompt, temperature)
        try:
            return json.loads(response)
        except:
            return {"error": "Failed to parse JSON response"}

# Global AI client instance
ai_client = AIClient()

async def test_ai_providers():
    """Test all available AI providers"""
    print("🧪 Testing AI Providers")
    print("=" * 25)
    
    test_prompt = "Write a short email about authentication challenges."
    
    # Test current provider
    print(f"\n🤖 Testing {type(ai_client.provider).__name__}:")
    response = await ai_client.generate_completion(test_prompt)
    print(f"Response length: {len(response)} characters")
    print(f"Sample: {response[:100]}...")
    
    # Test JSON generation
    json_prompt = "Generate a JSON object with signal information."
    json_response = await ai_client.generate_json_completion(json_prompt)
    print(f"JSON response: {type(json_response).__name__}")

if __name__ == "__main__":
    asyncio.run(test_ai_providers())
