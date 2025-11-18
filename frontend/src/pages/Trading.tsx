import { useState, useEffect } from 'react'
import { apiClient } from '../api/client'
import ApiConfig from '../components/ApiConfig'
import AIDecision from '../components/AIDecision'

interface Balance {
  currency: string
  free: number
  used: number
  total: number
  demo?: boolean
}

interface Ticker {
  symbol: string
  last: number
  bid: number
  ask: number
  high: number
  low: number
  volume: number
  demo?: boolean
}

interface Trade {
  id: number
  trader_id?: string
  strategy?: string
  symbol: string
  action: string
  price: number
  amount: number
  cost: number
  fee_amount: number
  timestamp: number
}

function Trading() {
  const [usdtBalance, setUsdtBalance] = useState<Balance | null>(null)
  const [btcBalance, setBtcBalance] = useState<Balance | null>(null)
  const [ticker, setTicker] = useState<Ticker | null>(null)
  const [trades, setTrades] = useState<Trade[]>([])
  const [loading, setLoading] = useState(false)
  const [amount, setAmount] = useState('0.001')

  // 加载余额
  const loadBalance = async () => {
    try {
      const response = await apiClient.get('/api/balance')
      setUsdtBalance(response.data.data.usdt)
      setBtcBalance(response.data.data.btc)
    } catch (error) {
      console.error('加载余额失败:', error)
    }
  }

  // 加载行情
  const loadTicker = async () => {
    try {
      const response = await apiClient.get('/api/ticker')
      setTicker(response.data.data)
    } catch (error) {
      console.error('加载行情失败:', error)
    }
  }

  // 加载交易历史（仅手动交易）
  const loadTrades = async () => {
    try {
      // ✅ 只加载手动交易记录
      const response = await apiClient.get('/api/trades?trader_id=manual')
      setTrades(response.data.data)
    } catch (error) {
      console.error('加载交易历史失败:', error)
    }
  }

  // 买入
  const handleBuy = async () => {
    if (loading) return
    setLoading(true)
    try {
      await apiClient.post(`/api/trade/buy?symbol=BTC/USDT&amount=${amount}`)
      alert('买入成功！')
      await Promise.all([loadBalance(), loadTrades()])
    } catch (error: any) {
      alert('买入失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  // 卖出
  const handleSell = async () => {
    if (loading) return
    setLoading(true)
    try {
      await apiClient.post(`/api/trade/sell?symbol=BTC/USDT&amount=${amount}`)
      alert('卖出成功！')
      await Promise.all([loadBalance(), loadTrades()])
    } catch (error: any) {
      alert('卖出失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadBalance()
    loadTicker()
    loadTrades()
    
    // 每5秒刷新一次（符合PROJECT_SPEC.md规范）
    const interval = setInterval(() => {
      loadBalance()
      loadTicker()
    }, 5000)
    
    return () => clearInterval(interval)
  }, [])

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif', maxWidth: '1200px', margin: '0 auto' }}>
      <h1>🚀 AI-Spot-Master 交易系统</h1>
      
      {/* API配置 */}
      <ApiConfig onConfigUpdate={() => {
        loadBalance()
        loadTicker()
      }} />
      
      {/* AI交易建议 */}
      <AIDecision />
      
      {/* 余额显示 */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginBottom: '20px' }}>
        <div style={{ padding: '20px', backgroundColor: '#f0f8ff', borderRadius: '8px', border: '1px solid #4a90e2' }}>
          <h3 style={{ margin: '0 0 10px 0', color: '#2c3e50' }}>💵 USDT 余额</h3>
          {usdtBalance ? (
            <div>
              <p style={{ fontSize: '24px', fontWeight: 'bold', margin: '5px 0', color: '#27ae60' }}>
                {usdtBalance.free.toFixed(2)} USDT
              </p>
              <p style={{ fontSize: '12px', color: '#7f8c8d', margin: 0 }}>
                冻结: {usdtBalance.used.toFixed(2)} | 总计: {usdtBalance.total.toFixed(2)}
                {usdtBalance.demo && <span style={{ color: '#e74c3c' }}> (演示模式)</span>}
              </p>
            </div>
          ) : (
            <p>加载中...</p>
          )}
        </div>

        <div style={{ padding: '20px', backgroundColor: '#fff8dc', borderRadius: '8px', border: '1px solid #f39c12' }}>
          <h3 style={{ margin: '0 0 10px 0', color: '#2c3e50' }}>₿ BTC 余额</h3>
          {btcBalance ? (
            <div>
              <p style={{ fontSize: '24px', fontWeight: 'bold', margin: '5px 0', color: '#f39c12' }}>
                {btcBalance.free.toFixed(8)} BTC
              </p>
              <p style={{ fontSize: '12px', color: '#7f8c8d', margin: 0 }}>
                冻结: {btcBalance.used.toFixed(8)} | 总计: {btcBalance.total.toFixed(8)}
                {btcBalance.demo && <span style={{ color: '#e74c3c' }}> (演示模式)</span>}
              </p>
            </div>
          ) : (
            <p>加载中...</p>
          )}
        </div>
      </div>

      {/* 行情显示 */}
      {ticker && (
        <div style={{ padding: '20px', backgroundColor: '#f5f5f5', borderRadius: '8px', marginBottom: '20px' }}>
          <h3 style={{ margin: '0 0 10px 0' }}>📈 BTC/USDT 行情</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px' }}>
            <div>
              <span style={{ color: '#7f8c8d' }}>最新价:</span>
              <strong style={{ marginLeft: '5px', fontSize: '18px' }}>${ticker.last.toLocaleString()}</strong>
            </div>
            <div>
              <span style={{ color: '#7f8c8d' }}>24h最高:</span>
              <strong style={{ marginLeft: '5px', color: '#27ae60' }}>${ticker.high.toLocaleString()}</strong>
            </div>
            <div>
              <span style={{ color: '#7f8c8d' }}>24h最低:</span>
              <strong style={{ marginLeft: '5px', color: '#e74c3c' }}>${ticker.low.toLocaleString()}</strong>
            </div>
            <div>
              <span style={{ color: '#7f8c8d' }}>24h成交量:</span>
              <strong style={{ marginLeft: '5px' }}>{ticker.volume.toFixed(2)} BTC</strong>
            </div>
          </div>
          {ticker.demo && <p style={{ fontSize: '12px', color: '#e74c3c', margin: '5px 0 0 0' }}>* 演示数据</p>}
        </div>
      )}

      {/* 交易操作 */}
      <div style={{ padding: '20px', backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #ddd', marginBottom: '20px' }}>
        <h3 style={{ margin: '0 0 15px 0' }}>💱 交易操作</h3>
        <div style={{ display: 'flex', gap: '15px', alignItems: 'flex-start' }}>
          <div>
            <label>
              数量:
              <input 
                type="number" 
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                step="0.001"
                min="0.001"
                style={{ 
                  marginLeft: '10px', 
                  padding: '8px 12px', 
                  fontSize: '16px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  width: '150px'
                }}
              />
              <span style={{ marginLeft: '5px', color: '#7f8c8d' }}>BTC</span>
            </label>
            
            {/* 成本预览 */}
            {ticker && amount && parseFloat(amount) > 0 && (
              <div style={{ 
                marginTop: '10px', 
                padding: '10px', 
                backgroundColor: '#f8f9fa', 
                borderRadius: '4px',
                fontSize: '13px',
                minWidth: '280px'
              }}>
                <div style={{ marginBottom: '5px' }}>
                  <span style={{ color: '#7f8c8d' }}>预估成本:</span>
                  <strong style={{ marginLeft: '8px', color: '#2c3e50' }}>
                    ≈ ${(parseFloat(amount) * ticker.last).toFixed(2)} USDT
                  </strong>
                </div>
                <div style={{ marginBottom: '5px' }}>
                  <span style={{ color: '#7f8c8d' }}>预估手续费:</span>
                  <strong style={{ marginLeft: '8px', color: '#e67e22' }}>
                    ≈ ${(parseFloat(amount) * ticker.last * 0.0015).toFixed(2)} USDT
                  </strong>
                  <span style={{ marginLeft: '5px', color: '#95a5a6', fontSize: '11px' }}>(0.15%)</span>
                </div>
                <div style={{ paddingTop: '5px', borderTop: '1px solid #dee2e6' }}>
                  <span style={{ color: '#7f8c8d' }}>总计花费:</span>
                  <strong style={{ marginLeft: '8px', color: '#27ae60', fontSize: '14px' }}>
                    ≈ ${(parseFloat(amount) * ticker.last * 1.0015).toFixed(2)} USDT
                  </strong>
                </div>
              </div>
            )}
          </div>
          
          <div style={{ display: 'flex', gap: '15px' }}>
            <button 
              onClick={handleBuy}
              disabled={loading}
            style={{
              padding: '10px 30px',
              fontSize: '16px',
              backgroundColor: loading ? '#95a5a6' : '#27ae60',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontWeight: 'bold'
            }}
          >
            {loading ? '处理中...' : '🟢 买入'}
          </button>
          
          <button 
            onClick={handleSell}
            disabled={loading}
            style={{
              padding: '10px 30px',
              fontSize: '16px',
              backgroundColor: loading ? '#95a5a6' : '#e74c3c',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontWeight: 'bold'
            }}
          >
            {loading ? '处理中...' : '🔴 卖出'}
          </button>
        </div>
        </div>
      </div>

      {/* 交易历史 */}
      <div style={{ padding: '20px', backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #ddd' }}>
        <h3 style={{ margin: '0 0 15px 0' }}>📊 交易历史</h3>
        {trades.length > 0 ? (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ backgroundColor: '#f8f9fa' }}>
                <th style={{ padding: '10px', textAlign: 'left', borderBottom: '2px solid #dee2e6' }}>时间</th>
                <th style={{ padding: '10px', textAlign: 'left', borderBottom: '2px solid #dee2e6' }}>交易对</th>
                <th style={{ padding: '10px', textAlign: 'left', borderBottom: '2px solid #dee2e6' }}>类型</th>
                <th style={{ padding: '10px', textAlign: 'left', borderBottom: '2px solid #dee2e6' }}>操作</th>
                <th style={{ padding: '10px', textAlign: 'right', borderBottom: '2px solid #dee2e6' }}>价格</th>
                <th style={{ padding: '10px', textAlign: 'right', borderBottom: '2px solid #dee2e6' }}>数量</th>
                <th style={{ padding: '10px', textAlign: 'right', borderBottom: '2px solid #dee2e6' }}>成交额</th>
                <th style={{ padding: '10px', textAlign: 'right', borderBottom: '2px solid #dee2e6' }}>手续费</th>
              </tr>
            </thead>
            <tbody>
              {trades.map((trade) => (
                <tr key={trade.id} style={{ borderBottom: '1px solid #dee2e6' }}>
                  <td style={{ padding: '10px' }}>
                    {new Date(trade.timestamp).toLocaleString('zh-CN')}
                  </td>
                  <td style={{ padding: '10px' }}>{trade.symbol}</td>
                  <td style={{ padding: '10px' }}>
                    <span style={{
                      padding: '2px 8px',
                      borderRadius: '4px',
                      fontSize: '12px',
                      backgroundColor: trade.trader_id === 'manual' ? '#e8f5e9' : '#fff3e0',
                      color: trade.trader_id === 'manual' ? '#2e7d32' : '#e65100',
                      fontWeight: 'bold'
                    }}>
                      {trade.trader_id === 'manual' ? '🔧 手动' : '🤖 自动'}
                    </span>
                  </td>
                  <td style={{ padding: '10px' }}>
                    <span style={{ 
                      color: trade.action === 'buy' ? '#27ae60' : '#e74c3c',
                      fontWeight: 'bold'
                    }}>
                      {trade.action === 'buy' ? '买入' : '卖出'}
                    </span>
                  </td>
                  <td style={{ padding: '10px', textAlign: 'right' }}>${trade.price.toLocaleString()}</td>
                  <td style={{ padding: '10px', textAlign: 'right' }}>{trade.amount.toFixed(8)}</td>
                  <td style={{ padding: '10px', textAlign: 'right' }}>${trade.cost.toFixed(2)}</td>
                  <td style={{ padding: '10px', textAlign: 'right' }}>${trade.fee_amount.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ color: '#7f8c8d', textAlign: 'center', padding: '20px' }}>暂无交易记录</p>
        )}
      </div>
    </div>
  )
}

export default Trading
