import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import time
from .intent_config import IntentConfig

class IntentModel:
    def __init__(self):
        self.config = IntentConfig()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = None
        self.model = None
        self._load_model()
    
    def _load_model(self):
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.config.MODEL_PATH, local_files_only=True)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.config.MODEL_PATH, local_files_only=True)
            self.model.to(self.device)
            self.model.eval()
        except Exception as e:
            # 模型加载失败时不抛错，使用默认意图
            print(f"Intent model loading failed: {e}")
    
    def _batch_inference(self, texts):
        if not self.model or not self.tokenizer:
            return [self.config.DEFAULT_INTENT] * len(texts), [0.0] * len(texts)
        
        batch_size = self.config.BATCH_SIZE
        intents = []
        scores = []
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            inputs = self.tokenizer(
                batch_texts,
                padding=True,
                truncation=True,
                max_length=self.config.MAX_LENGTH,
                return_tensors="pt"
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=1).cpu().numpy()
                
                for prob in probabilities:
                    max_prob = max(prob)
                    max_idx = prob.argmax()
                    if max_prob >= self.config.CONFIDENCE_THRESHOLD:
                        intent = self.config.INTENT_CLASSES[max_idx]
                    else:
                        intent = self.config.DEFAULT_INTENT
                    intents.append(intent)
                    scores.append(float(max_prob))
        
        return intents, scores
    
    def predict(self, text):
        if not text:
            return {
                "intent": self.config.DEFAULT_INTENT,
                "score": 0.0,
                "model_use": False,
                "timestamp": int(time.time())
            }
        
        start_time = time.time()
        intents, scores = self._batch_inference([text])
        inference_time = (time.time() - start_time) * 1000  # 转换为毫秒
        
        # 超时处理
        if inference_time > self.config.INFERENCE_TIMEOUT:
            return {
                "intent": self.config.DEFAULT_INTENT,
                "score": 0.0,
                "model_use": False,
                "timestamp": int(time.time())
            }
        
        return {
            "intent": intents[0],
            "score": scores[0],
            "model_use": True,
            "timestamp": int(time.time())
        }
