"""
AI交易决策提示词模板
"""
from typing import Dict, Any


def generate_trade_prompt(market_data: Dict[str, Any]) -> str:
    """
    生成交易决策提示词
    
    Args:
        market_data: 市场数据
        {
            'symbol': 'BTC/USDT',
            'price': 95000.0,
            'change_24h': 2.5,
            'high_24h': 96000.0,
            'low_24h': 93000.0,
            'position': 0.001,  # 当前持仓BTC数量
            'balance': 1000.0   # 当前USDT余额
        }
        
    Returns:
        提示词字符串
    """
    return f"""你是一个专业的加密货币交易顾问，请根据以下市场数据给出交易建议。

【当前市场数据】
- 交易对: {market_data['symbol']}
- 当前价格: ${market_data['price']:,.2f}
- 24h涨跌幅: {market_data['change_24h']:+.2f}%
- 24h最高价: ${market_data['high_24h']:,.2f}
- 24h最低价: ${market_data['low_24h']:,.2f}
- 当前持仓: {market_data['position']} BTC
- 可用余额: ${market_data['balance']:.2f} USDT

【决策要求】
1. 分析当前市场趋势（上涨/下跌/震荡）
2. 评估入场时机（买入/卖出/等待）
3. 给出决策置信度（0.0-1.0）

【回复格式（严格JSON）】
{{
  "action": "buy" 或 "sell" 或 "wait",
  "reasoning": "你的分析理由（50字以内）",
  "confidence": 0.75
}}

注意：
- action只能是buy、sell、wait三选一
- reasoning必须简洁明了
- confidence范围0.0-1.0，越接近1.0表示越确定
- 只返回JSON，不要其他文字
"""


def generate_coin_selection_prompt(coins_data: list) -> str:
    """
    生成币种选择提示词（Phase 4+功能）
    
    Args:
        coins_data: 币种数据列表
        
    Returns:
        提示词字符串
    """
    # Phase 3暂不实现，预留接口
    return ""
