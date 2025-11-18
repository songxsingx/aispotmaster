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
        self.last_valid_price = None  # ✅ 缓存最后的有效价格
        
        self.exchange = ccxt.gateio({
            'apiKey': api_key,
            'secret': api_secret,
            'options': {'defaultType': 'spot'}
        })
        
        if testnet:
            # Gate.io 测试网配置
            self.exchange.set_sandbox_mode(True)
    
    def get_balance(self, currency: Optional[str] = None) -> Dict:
        """
        获取余额
        
        Args:
            currency: 币种，默认None（返回所有币种）
            
        Returns:
            余额信息字典
        """
        try:
            balance = self.exchange.fetch_balance()
            
            # 如果指定了币种，只返回该币种
            if currency:
                return {
                    'currency': currency,
                    'free': float(balance.get(currency, {}).get('free', 0)),
                    'used': float(balance.get(currency, {}).get('used', 0)),
                    'total': float(balance.get(currency, {}).get('total', 0))
                }
            
            # 返回所有币种（为 grid.py 等策略使用）
            return balance
            
        except Exception as e:
            # 如果没有API密钥，返回模拟数据
            if currency:
                return {
                    'currency': currency,
                    'free': 1000.0,
                    'used': 0.0,
                    'total': 1000.0,
                    'demo': True
                }
            else:
                # 返回模拟的完整余额
                return {
                    'USDT': {'free': 1000.0, 'used': 0.0, 'total': 1000.0},
                    'BTC': {'free': 0.0, 'used': 0.0, 'total': 0.0},
                    'demo': True
                }
    
    def get_ticker(self, symbol: str = 'BTC/USDT') -> Dict:
        """获取行情 - 带重试机制和缓存"""
        max_retries = 3
        retry_delay = 1  # 秒
        
        for attempt in range(max_retries):
            try:
                ticker = self.exchange.fetch_ticker(symbol)
                
                # 验证数据完整性
                if not ticker or 'last' not in ticker:
                    raise ValueError("返回数据不完整")
                
                last_price = float(ticker['last'])
                
                # 验证价格合理性（BTC价格应该在10K-200K之间）
                if last_price < 10000 or last_price > 200000:
                    print(f"⚠️ 异常价格: ${last_price:,.2f}，重试中...")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                
                # 缓存最后的有效价格
                self.last_valid_price = last_price
                
                return {
                    'symbol': symbol,
                    'last': last_price,
                    'bid': float(ticker.get('bid', last_price)),
                    'ask': float(ticker.get('ask', last_price)),
                    'high': float(ticker.get('high', last_price)),
                    'low': float(ticker.get('low', last_price)),
                    'volume': float(ticker.get('baseVolume', 0))
                }
                
            except Exception as e:
                print(f"⚠️ 获取行情失败 (尝试{attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
        
        # 所有重试都失败，使用缓存的价格
        if hasattr(self, 'last_valid_price') and self.last_valid_price:
            print(f"⚠️ 使用缓存价格: ${self.last_valid_price:,.2f}")
            return {
                'symbol': symbol,
                'last': self.last_valid_price,
                'bid': self.last_valid_price,
                'ask': self.last_valid_price,
                'high': self.last_valid_price,
                'low': self.last_valid_price,
                'volume': 0,
                'cached': True
            }
        
        # 完全没有有效数据，抛出异常（不返回虚假的模拟价格）
        raise Exception(f"无法获取{symbol}的有效行情数据，且无缓存可用")
    
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
