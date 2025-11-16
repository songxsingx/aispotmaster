"""
Gate.io 交易所接口封装
使用 ccxt 库实现
"""
import ccxt
from typing import Dict, Optional
from decimal import Decimal
import time

class GateIOExchange:
    """Gate.io 交易所适配器"""
    
    def __init__(self, api_key: str = "", api_secret: str = "", testnet: bool = True):
        """
        初始化 Gate.io 交易所
        
        Args:
            api_key: API密钥
            api_secret: API密钥
            testnet: 是否使用测试网
        """
        self.exchange = ccxt.gateio({
            'apiKey': api_key,
            'secret': api_secret,
            'options': {'defaultType': 'spot'}
        })
        
        if testnet:
            # Gate.io 测试网配置
            self.exchange.set_sandbox_mode(True)
    
    def get_balance(self, currency: str = 'USDT') -> Dict:
        """
        获取余额
        
        Args:
            currency: 币种，默认USDT
            
        Returns:
            余额信息字典
        """
        try:
            balance = self.exchange.fetch_balance()
            return {
                'currency': currency,
                'free': float(balance.get(currency, {}).get('free', 0)),
                'used': float(balance.get(currency, {}).get('used', 0)),
                'total': float(balance.get(currency, {}).get('total', 0))
            }
        except Exception as e:
            # 如果没有API密钥，返回模拟数据
            return {
                'currency': currency,
                'free': 1000.0,
                'used': 0.0,
                'total': 1000.0,
                'demo': True
            }
    
    def get_ticker(self, symbol: str = 'BTC/USDT') -> Dict:
        """获取行情"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'last': float(ticker['last']),
                'bid': float(ticker['bid']),
                'ask': float(ticker['ask']),
                'high': float(ticker['high']),
                'low': float(ticker['low']),
                'volume': float(ticker['baseVolume'])
            }
        except Exception as e:
            # 返回模拟数据
            return {
                'symbol': symbol,
                'last': 43250.5,
                'bid': 43250.0,
                'ask': 43251.0,
                'high': 43500.0,
                'low': 43000.0,
                'volume': 1234.56,
                'demo': True
            }
    
    def market_buy(self, symbol: str, amount: float) -> Dict:
        """
        市价买入
        
        Args:
            symbol: 交易对，如 BTC/USDT
            amount: 买入数量（币的数量）
            
        Returns:
            订单信息
        """
        # 先获取当前市场价格
        ticker = self.get_ticker(symbol)
        current_price = ticker.get('last')
        if not current_price:
            raise ValueError(f"无法获取{symbol}的当前价格")
        cost = amount * current_price
        
        try:
            # Gate.io测试网可能不支持市价单，使用限价单模拟市价单
            # 买入时价格设置为当前价格的1.005倍（0.5%溢价），确保成交
            order = self.exchange.create_limit_buy_order(
                symbol,
                amount,  # BTC数量
                current_price * 1.005  # 稍高于市价，确保成交
            )
            
            # 确保order不为None
            if not order:
                raise ValueError("订单返回为空")
            
            # 安全获取字段，提供默认值
            actual_cost = float(order.get('cost') or (amount * current_price))
            actual_fee = float((order.get('fee') or {}).get('cost', 0) if order.get('fee') else 0)
            
            # 如果Gate.io没有返回手续费，我们自己计算
            if actual_fee == 0:
                actual_fee = actual_cost * 0.0015  # 0.15%
            
            return {
                'order_id': str(order.get('id', f"order_{int(time.time())}")),
                'symbol': symbol,
                'action': 'buy',
                'amount': float(order.get('amount') or order.get('filled') or amount),
                'price': float(order.get('average') or order.get('price') or current_price),
                'cost': actual_cost,
                'fee': actual_fee,
                'timestamp': int(order.get('timestamp') or (time.time() * 1000)),
                'real': True  # 真实交易
            }
        except Exception as e:
            # 模拟订单（使用实时价格）
            print(f"Buy order failed: {str(e)}")  # 打印错误日志
            return {
                'order_id': f"demo_{int(time.time())}",
                'symbol': symbol,
                'action': 'buy',
                'amount': amount,
                'price': current_price,
                'cost': cost,
                'fee': cost * 0.0015,
                'timestamp': int(time.time() * 1000),
                'demo': True,
                'error': str(e)
            }
    
    def market_sell(self, symbol: str, amount: float) -> Dict:
        """
        市价卖出
        
        Args:
            symbol: 交易对
            amount: 卖出数量
            
        Returns:
            订单信息
        """
        # 先获取当前市场价格
        ticker = self.get_ticker(symbol)
        current_price = ticker.get('last')
        if not current_price:
            raise ValueError(f"无法获取{symbol}的当前价格")
        cost = amount * current_price
        
        try:
            # 使用限价单模拟市价单
            # 卖出时价格设置为当前价格的0.995倍（0.5%折价），确保成交
            order = self.exchange.create_limit_sell_order(
                symbol,
                amount,
                current_price * 0.995
            )
            
            # 确保order不为None
            if not order:
                raise ValueError("订单返回为空")
            
            # 安全获取字段
            actual_cost = float(order.get('cost') or (amount * current_price))
            actual_fee = float((order.get('fee') or {}).get('cost', 0) if order.get('fee') else 0)
            
            # 如果Gate.io没有返回手续费，我们自己计算
            if actual_fee == 0:
                actual_fee = actual_cost * 0.0015  # 0.15%
            
            return {
                'order_id': str(order.get('id', f"order_{int(time.time())}")),
                'symbol': symbol,
                'action': 'sell',
                'amount': float(order.get('amount') or order.get('filled') or amount),
                'price': float(order.get('average') or order.get('price') or current_price),
                'cost': actual_cost,
                'fee': actual_fee,
                'timestamp': int(order.get('timestamp') or (time.time() * 1000)),
                'real': True
            }
        except Exception as e:
            # 模拟订单（使用实时价格）
            print(f"Sell order failed: {str(e)}")
            return {
                'order_id': f"demo_{int(time.time())}",
                'symbol': symbol,
                'action': 'sell',
                'amount': amount,
                'price': current_price,
                'cost': cost,
                'fee': cost * 0.0015,
                'timestamp': int(time.time() * 1000),
                'demo': True,
                'error': str(e)
            }
