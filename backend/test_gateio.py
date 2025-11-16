#!/usr/bin/env python3
"""Gate.io API 测试脚本"""

import ccxt
from config import settings

def test_gateio_api():
    """测试Gate.io API各项功能"""
    
    print("=" * 60)
    print("Gate.io API 诊断测试")
    print("=" * 60)
    
    # 初始化交易所
    exchange = ccxt.gateio({
        'apiKey': settings.gate_api_key,
        'secret': settings.gate_api_secret,
        'options': {'defaultType': 'spot'}
    })
    
    if settings.gate_testnet:
        exchange.set_sandbox_mode(True)
        print("✅ 模式: 测试网")
    else:
        print("⚠️  模式: 正式网")
    
    print(f"📌 API Key: {settings.gate_api_key[:10]}...")
    print(f"📌 ccxt版本: {ccxt.__version__}")
    print()
    
    # 测试1: 查询余额
    print("【测试1】查询余额")
    try:
        balance = exchange.fetch_balance()
        print(f"✅ USDT: {balance.get('USDT', {}).get('free', 0)}")
        print(f"✅ BTC: {balance.get('BTC', {}).get('free', 0)}")
    except Exception as e:
        print(f"❌ 余额查询失败: {e}")
        return
    print()
    
    # 测试2: 获取行情
    print("【测试2】获取BTC/USDT行情")
    try:
        ticker = exchange.fetch_ticker('BTC/USDT')
        print(f"✅ 最新价: ${ticker['last']:,.2f}")
        print(f"✅ 买一价: ${ticker['bid']:,.2f}")
        print(f"✅ 卖一价: ${ticker['ask']:,.2f}")
    except Exception as e:
        print(f"❌ 行情查询失败: {e}")
        return
    print()
    
    # 测试3: 查询交易对信息
    print("【测试3】查询BTC/USDT交易规则")
    try:
        markets = exchange.load_markets()
        btc_market = markets.get('BTC/USDT')
        if btc_market:
            print(f"✅ 交易对: {btc_market['symbol']}")
            print(f"✅ 最小下单量: {btc_market['limits']['amount']['min']} BTC")
            print(f"✅ 最小成交额: {btc_market['limits']['cost']['min']} USDT")
            print(f"✅ 支持市价单: {btc_market.get('spot', True)}")
        else:
            print("❌ 未找到BTC/USDT交易对")
            return
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        return
    print()
    
    # 测试4: 尝试创建限价买单（小额测试）
    print("【测试4】测试限价买单 (0.0001 BTC)")
    try:
        current_price = ticker['last']
        test_amount = 0.0001  # 极小数量测试
        buy_price = current_price * 1.01  # 高于市价1%
        
        print(f"📊 数量: {test_amount} BTC")
        print(f"📊 价格: ${buy_price:,.2f}")
        print(f"📊 预估成本: ${test_amount * buy_price:.2f}")
        print()
        
        # 尝试创建订单
        order = exchange.create_limit_buy_order('BTC/USDT', test_amount, buy_price)
        
        if order:
            print(f"✅ 订单创建成功!")
            print(f"   订单ID: {order.get('id', 'N/A')}")
            print(f"   状态: {order.get('status', 'N/A')}")
            print(f"   数量: {order.get('amount', 'N/A')} BTC")
            print(f"   价格: ${order.get('price', 'N/A')}")
            
            # 取消测试订单
            try:
                exchange.cancel_order(order['id'], 'BTC/USDT')
                print(f"✅ 测试订单已取消")
            except:
                print(f"⚠️  未能取消订单，请手动处理")
        else:
            print(f"❌ 订单返回为空")
            
    except Exception as e:
        print(f"❌ 订单创建失败: {e}")
        print(f"   错误类型: {type(e).__name__}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == '__main__':
    test_gateio_api()
