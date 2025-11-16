"""
DeepSeek AI客户端
"""
import requests
import json
from typing import Dict, Any


class DeepSeekClient:
    """DeepSeek API客户端"""
    
    def __init__(self, api_key: str):
        """
        初始化DeepSeek客户端
        
        Args:
            api_key: DeepSeek API密钥
        """
        self.api_key = api_key
        self.base_url = 'https://api.deepseek.com/v1'
    
    def make_decision(self, prompt: str) -> Dict[str, Any]:
        """
        调用DeepSeek API进行决策
        
        Args:
            prompt: 提示词
            
        Returns:
            AI决策结果
            {
                'action': 'buy' | 'sell' | 'wait',
                'reasoning': '决策理由',
                'confidence': 0.0-1.0
            }
        """
        try:
            response = requests.post(
                f'{self.base_url}/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'deepseek-chat',
                    'messages': [{'role': 'user', 'content': prompt}],
                    'temperature': 0.7,
                    'max_tokens': 500
                },
                timeout=30
            )
            
            response.raise_for_status()
            ai_response = response.json()['choices'][0]['message']['content']
            
            # 解析AI返回的JSON
            decision = json.loads(ai_response)
            
            return {
                'action': decision.get('action', 'wait'),
                'reasoning': decision.get('reasoning', 'AI未提供理由'),
                'confidence': decision.get('confidence', 0.5)
            }
            
        except requests.exceptions.RequestException as e:
            print(f"DeepSeek API调用失败: {e}")
            # 返回默认决策（等待）
            return {
                'action': 'wait',
                'reasoning': f'API调用失败: {str(e)}',
                'confidence': 0.0
            }
        except (json.JSONDecodeError, KeyError) as e:
            print(f"DeepSeek响应解析失败: {e}")
            return {
                'action': 'wait',
                'reasoning': f'响应解析失败: {str(e)}',
                'confidence': 0.0
            }
