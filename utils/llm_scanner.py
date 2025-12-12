import logging
try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

logger = logging.getLogger(__name__)

class LLMScanner:
    def __init__(self, model_path="models/phi-3-mini-4k-instruct.Q4_K_M.gguf"):
        self.model = None
        if Llama:
            try:
                # n_ctx=2048 for reasonable context, n_threads=4 for Pi
                self.model = Llama(model_path=model_path, n_ctx=2048, n_threads=4, verbose=False)
            except Exception as e:
                logger.error(f"Failed to load LLM: {e}")
        else:
            logger.warning("llama-cpp-python not installed.")

    def analyze_text(self, text):
        if not self.model:
            return {"error": "LLM not loaded"}

        prompt = f"""
        Analyze the following product text and extract compliance details.
        Return JSON with keys: mrp, expiry, fssai, net_qty, ingredients_found (boolean).
        
        Text:
        {text[:1000]}
        
        JSON:
        """
        
        output = self.model(prompt, max_tokens=200, stop=["```", "}"])
        return output['choices'][0]['text']

# Usage:
# scanner = LLMScanner()
# result = scanner.analyze_text(extracted_text)
