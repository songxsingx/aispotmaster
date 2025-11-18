import { useState, useEffect } from 'react'
import { apiClient } from '../api/client'

interface Trade {
  id: number
  trader_id: string
  strategy: string
  symbol: string
  action: string
  price: number
  amount: number
  cost: number
  fee_amount: number
  timestamp: number
  position_before: number
  position_after: number
}

interface Trader {
  id: string
  name: string
  strategy: string
  symbol: string
  status: string
  config: {
    amount: number
    grid_gap: number
    check_interval: number
  }
  created_at: number
  runtime_status?: {
    current_position: number
    last_price: number | null
  }
}

interface Balance {
  usdt: { free: number; used: number; total: number }
  btc: { free: number; used: number; total: number }
}

interface Props {
  traderId: string
  onBack: () => void
}

function TraderDetail({ traderId, onBack }: Props) {
  const [trader, setTrader] = useState<Trader | null>(null)
  const [trades, setTrades] = useState<Trade[]>([])
  const [balance, setBalance] = useState<Balance | null>(null)
  const [loading, setLoading] = useState(true)
  const [runningTime, setRunningTime] = useState<string>('')

  // 加载交易员信息
  const loadTrader = async () => {
    try {
      const response = await apiClient.get(`/api/traders/${traderId}`)
      setTrader(response.data.data)
    } catch (error) {
      console.error('加载交易员失败:', error)
    }
  }

  // 加载该交易员的交易历史
  const loadTrades = async () => {
    try {
      const response = await apiClient.get(`/api/trades?trader_id=${traderId}&limit=50`)
      setTrades(response.data.data)
    } catch (error) {
      console.error('加载交易历史失败:', error)
    } finally {
      setLoading(false)
    }
  }

  // 加载账户余额
  const loadBalance = async () => {
    try {
      const response = await apiClient.get('/api/balance')
      setBalance(response.data.data)
    } catch (error) {
      console.error('加载余额失败:', error)
    }
  }

  // 计算运行时长
  const calculateRunningTime = () => {
    if (!trader?.created_at) return ''
    
    const now = Math.floor(Date.now() / 1000)
    const elapsed = now - trader.created_at
    
    const days = Math.floor(elapsed / 86400)
    const hours = Math.floor((elapsed % 86400) / 3600)
    const minutes = Math.floor((elapsed % 3600) / 60)
    
    if (days > 0) {
      return `${days}天 ${hours}小时 ${minutes}分钟`
    } else if (hours > 0) {
      return `${hours}小时 ${minutes}分钟`
    } else {
      return `${minutes}分钟`
    }
  }

  // 初始加载数据
  useEffect(() => {
    loadTrader()
    loadTrades()
    loadBalance()
    
    // 每5秒刷新一次（符合PROJECT_SPEC.md规范）
    const interval = setInterval(() => {
      loadTrader()
      loadTrades()
      loadBalance()
    }, 5000)
    
    return () => clearInterval(interval)
  }, [traderId])
  
  // 运行时长独立更新
  useEffect(() => {
    // 立即计算一次
    setRunningTime(calculateRunningTime())
    
    // 每秒更新运行时长
    const timeInterval = setInterval(() => {
      setRunningTime(calculateRunningTime())
    }, 1000)
    
    return () => clearInterval(timeInterval)
  }, [trader])  // 依赖trader，当trader加载后启动

  if (loading) {
    return <div style={{ padding: '20px' }}>加载中...</div>
  }

  if (!trader) {
    return <div style={{ padding: '20px' }}>交易员不存在</div>
  }

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif', maxWidth: '1200px', margin: '0 auto' }}>
      {/* 返回按钮 */}
      <button 
        onClick={onBack}
        style={{
          padding: '10px 20px',
          marginBottom: '20px',
          backgroundColor: '#6c757d',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
          fontWeight: 'bold'
        }}
      >
        ← 返回交易员列表
      </button>

      {/* 交易员基本信息 */}
      <div style={{ padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '8px', marginBottom: '20px' }}>
        <h2 style={{ margin: '0 0 15px 0', color: '#2c3e50' }}>📊 {trader.name}</h2>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '15px' }}>
          <div>
            <span style={{ color: '#7f8c8d', fontSize: '14px' }}>交易员ID</span>
            <p style={{ margin: '5px 0 0 0', fontWeight: 'bold', color: '#2c3e50', fontSize: '13px' }}>{trader.id}</p>
          </div>
          
          <div>
            <span style={{ color: '#7f8c8d', fontSize: '14px' }}>策略类型</span>
            <p style={{ margin: '5px 0 0 0', fontWeight: 'bold', color: '#2c3e50' }}>
              {trader.strategy === 'grid' ? '🔲 网格策略' : trader.strategy}
            </p>
          </div>
          
          <div>
            <span style={{ color: '#7f8c8d', fontSize: '14px' }}>运行状态</span>
            <p style={{ margin: '5px 0 0 0', fontWeight: 'bold' }}>
              <span style={{ 
                color: trader.status === 'running' ? '#27ae60' : '#e74c3c',
                padding: '3px 10px',
                backgroundColor: trader.status === 'running' ? '#d4edda' : '#f8d7da',
                borderRadius: '4px',
                fontSize: '14px'
              }}>
                {trader.status === 'running' ? '🟢 运行中' : '🔴 已停止'}
              </span>
            </p>
          </div>
          
          <div>
            <span style={{ color: '#7f8c8d', fontSize: '14px' }}>创建时间</span>
            <p style={{ margin: '5px 0 0 0', fontWeight: 'bold', color: '#2c3e50', fontSize: '13px' }}>
              {new Date(trader.created_at * 1000).toLocaleString('zh-CN')}
            </p>
          </div>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '15px', marginTop: '15px', paddingTop: '15px', borderTop: '1px solid #dee2e6' }}>
          <div>
            <span style={{ color: '#7f8c8d', fontSize: '14px' }}>运行时长</span>
            <p style={{ margin: '5px 0 0 0', fontWeight: 'bold', color: '#3498db' }}>
              ⏱️ {runningTime || '计算中...'}
            </p>
          </div>
          
          <div>
            <span style={{ color: '#7f8c8d', fontSize: '14px' }}>当前持仓</span>
            <p style={{ margin: '5px 0 0 0', fontWeight: 'bold', color: '#2c3e50' }}>
              {trader.runtime_status?.current_position?.toFixed(8) || '0.00000000'} BTC
              {trader.runtime_status?.current_position && trader.runtime_status.last_price ? (
                <span style={{ fontSize: '12px', color: '#7f8c8d', marginLeft: '5px' }}>
                  (≈ ${(trader.runtime_status.current_position * trader.runtime_status.last_price).toFixed(2)})
                </span>
              ) : null}
            </p>
          </div>
          
          <div>
            <span style={{ color: '#7f8c8d', fontSize: '14px' }}>USDT余额</span>
            <p style={{ margin: '5px 0 0 0', fontWeight: 'bold', color: '#27ae60' }}>
              💵 {balance?.usdt.free.toFixed(2) || '---'} USDT
            </p>
          </div>
          
          <div>
            <span style={{ color: '#7f8c8d', fontSize: '14px' }}>BTC余额</span>
            <p style={{ margin: '5px 0 0 0', fontWeight: 'bold', color: '#f39c12' }}>
              ₿ {balance?.btc.free.toFixed(8) || '---'} BTC
              {balance?.btc.free && trader.runtime_status?.last_price ? (
                <span style={{ fontSize: '12px', color: '#7f8c8d', marginLeft: '5px' }}>
                  (≈ ${(balance.btc.free * trader.runtime_status.last_price).toFixed(2)})
                </span>
              ) : null}
            </p>
          </div>
        </div>
      </div>

      {/* 策略配置 */}
      <div style={{ padding: '20px', backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #dee2e6', marginBottom: '20px' }}>
        <h3 style={{ margin: '0 0 15px 0', color: '#2c3e50' }}>⚙️ 策略配置</h3>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '15px' }}>
          <div>
            <span style={{ color: '#7f8c8d', fontSize: '14px' }}>交易对</span>
            <p style={{ margin: '5px 0 0 0', fontWeight: 'bold', color: '#2c3e50' }}>{trader.symbol}</p>
          </div>
          
          <div>
            <span style={{ color: '#7f8c8d', fontSize: '14px' }}>每次交易量</span>
            <p style={{ margin: '5px 0 0 0', fontWeight: 'bold', color: '#2c3e50' }}>
              {trader.config.amount} BTC
            </p>
          </div>
          
          <div>
            <span style={{ color: '#7f8c8d', fontSize: '14px' }}>网格间隔</span>
            <p style={{ margin: '5px 0 0 0', fontWeight: 'bold', color: '#2c3e50' }}>
              {trader.config.grid_gap}%
            </p>
          </div>
          
          <div>
            <span style={{ color: '#7f8c8d', fontSize: '14px' }}>检查间隔</span>
            <p style={{ margin: '5px 0 0 0', fontWeight: 'bold', color: '#2c3e50' }}>
              {trader.config.check_interval}秒
            </p>
          </div>
        </div>
      </div>

      {/* 交易历史 */}
      <div style={{ padding: '20px', backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #dee2e6' }}>
        <h3 style={{ margin: '0 0 15px 0', color: '#2c3e50' }}>📜 交易历史（共{trades.length}笔）</h3>
        
        {trades.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ backgroundColor: '#f8f9fa' }}>
                  <th style={{ padding: '10px', textAlign: 'left', borderBottom: '2px solid #dee2e6' }}>时间</th>
                  <th style={{ padding: '10px', textAlign: 'left', borderBottom: '2px solid #dee2e6' }}>操作</th>
                  <th style={{ padding: '10px', textAlign: 'right', borderBottom: '2px solid #dee2e6' }}>价格</th>
                  <th style={{ padding: '10px', textAlign: 'right', borderBottom: '2px solid #dee2e6' }}>数量</th>
                  <th style={{ padding: '10px', textAlign: 'right', borderBottom: '2px solid #dee2e6' }}>成交额</th>
                  <th style={{ padding: '10px', textAlign: 'right', borderBottom: '2px solid #dee2e6' }}>手续费</th>
                  <th style={{ padding: '10px', textAlign: 'right', borderBottom: '2px solid #dee2e6' }}>持仓后</th>
                </tr>
              </thead>
              <tbody>
                {trades.map((trade) => (
                  <tr key={trade.id} style={{ borderBottom: '1px solid #dee2e6' }}>
                    <td style={{ padding: '10px', fontSize: '13px' }}>
                      {new Date(trade.timestamp).toLocaleString('zh-CN')}
                    </td>
                    <td style={{ padding: '10px' }}>
                      <span style={{ 
                        color: trade.action === 'buy' ? '#27ae60' : '#e74c3c',
                        fontWeight: 'bold'
                      }}>
                        {trade.action === 'buy' ? '🟢 买入' : '🔴 卖出'}
                      </span>
                    </td>
                    <td style={{ padding: '10px', textAlign: 'right', fontSize: '13px' }}>
                      ${trade.price.toLocaleString()}
                    </td>
                    <td style={{ padding: '10px', textAlign: 'right', fontSize: '13px' }}>
                      {trade.amount.toFixed(8)}
                    </td>
                    <td style={{ padding: '10px', textAlign: 'right', fontSize: '13px' }}>
                      ${trade.cost.toFixed(2)}
                    </td>
                    <td style={{ padding: '10px', textAlign: 'right', fontSize: '13px', color: '#e67e22' }}>
                      ${trade.fee_amount.toFixed(2)}
                    </td>
                    <td style={{ padding: '10px', textAlign: 'right', fontSize: '13px', fontWeight: 'bold' }}>
                      {trade.position_after.toFixed(8)} BTC
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p style={{ color: '#7f8c8d', textAlign: 'center', padding: '40px 20px' }}>
            暂无交易记录
          </p>
        )}
      </div>
    </div>
  )
}

export default TraderDetail
