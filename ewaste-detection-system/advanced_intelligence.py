from intelligence_layer import EWasteIntelligence
import requests
import json

class AdvancedIntelligence(EWasteIntelligence):
    
    def __init__(self, api_key=None):
        super().__init__()
        self.api_key = api_key
        # OpenRouter API Endpoint
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        # Using a reliable model alias - Gemini 2.0 Flash is fast and good for this
        self.model = "google/gemini-2.0-flash-001" 

    def analyze_with_ai(self, class_name, confidence, image=None):
        """
        Detects recycling advice using OpenRouter API if API key is present.
        If no API key, falls back to the static intelligence layer.
        """
        
        # Base static analysis
        static_analysis = self.analyze(class_name, confidence)
        
        if not self.api_key:
            return static_analysis

        try:
            prompt = f"""
            Analyze this E-Waste item: '{class_name}'.
            Provide a concise, 2-sentence expert recycling recommendation.
            Focus on maximizing value recovery (gold, copper) and safe disposal of hazardous components.
            Do NOT greet. Just give the advice.
            """
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8501", # For OpenRouter rankings
                "X-Title": "E-Waste Detection System"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                ai_advice = data['choices'][0]['message']['content'].strip()
                # Override/Append the AI suggestion
                static_analysis['ai_suggestion'] = ai_advice
            else:
                print(f"OpenRouter Error: {response.status_code} - {response.text}")
                static_analysis['ai_suggestion'] = "AI Unavailable (Check API Key)"
                
            return static_analysis
            
        except Exception as e:
            print(f"AI Generation Error: {e}")
            static_analysis['ai_suggestion'] = "AI Connection Failed"
            return static_analysis
