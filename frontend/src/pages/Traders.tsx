import { useState, useEffect } from 'react'
import { apiClient } from '../api/client'

interface Trader {
  id: string
  name: string
  strategy: string
  symbol: string
  status: 'stopped' | 'running' | 'paused'
  config: {
    amount: number
    grid_gap: number
    check_interval: number
    stop_loss_pct?: number
    take_profit_pct?: number
  }
  created_at: number
  runtime_status?: {
    running: boolean
    last_price: number | null
    last_action: string | null
    trade_count: number
    current_position?: number
  }
}

interface TraderPnL {
  realized_pnl: number
  unrealized_pnl: number
  total_pnl: number
  pnl_pct: number
  total_cost: number
  current_value: number
  current_position: number
  current_price: number
}

interface Balance {
  usdt: { free: number; used: number; total: number }
  btc: { free: number; used: number; total: number }
}

interface Props {
  onViewDetail: (traderId: string) => void
}

function Traders({ onViewDetail }: Props) {
  const [traders, setTraders] = useState<Trader[]>([])
  const [loading, setLoading] = useState(false)
  const [showCreateForm, setShowCreateForm] = useState(true)  // 默认展开表单
  const [pnlData, setPnlData] = useState<Record<string, TraderPnL>>({})
  const [balance, setBalance] = useState<Balance | null>(null)
  const [currentTime, setCurrentTime] = useState(Date.now())
  
  // 表单状态
  const [name, setName] = useState('网格交易员')
  const [amount, setAmount] = useState('0.0005')
  const [gridGap, setGridGap] = useState('2.0')
  const [checkInterval, setCheckInterval] = useState('60')
  const [stopLoss, setStopLoss] = useState('')
  const [takeProfit, setTakeProfit] = useState('')
  const [showAdvanced, setShowAdvanced] = useState(false)  // 默认折叠高级选项

  // 加载交易员列表
  const loadTraders = async () => {
    try {
      const response = await apiClient.get('/api/traders')
      const tradersList = response.data.data
      setTraders(tradersList)
      
      // 加载每个交易员的盈亏数据
      for (const trader of tradersList) {
        loadPnL(trader.id)
      }
    } catch (error) {
      console.error('加载交易员失败:', error)
    }
  }

  // 加载盈亏数据
  const loadPnL = async (traderId: string) => {
    try {
      const response = await apiClient.get(`/api/traders/${traderId}/pnl`)
      setPnlData(prev => ({
        ...prev,
        [traderId]: response.data.data
      }))
    } catch (error) {
      console.error(`加载盈亏失败 (${traderId}):`, error)
    }
  }

  // ✅ Phase 3.5 - P2: 加载账户余额
  const loadBalance = async () => {
    try {
      const response = await apiClient.get('/api/balance')
      setBalance(response.data.data)
    } catch (error) {
      console.error('加载余额失败:', error)
    }
  }

  // ✅ Phase 3.5 - P2: 计算运行时长
  const formatRuntime = (createdAt: number) => {
    const seconds = Math.floor((currentTime - createdAt * 1000) / 1000)
    const days = Math.floor(seconds / 86400)
    const hours = Math.floor((seconds % 86400) / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    
    if (days > 0) return `${days}天${hours}小时`
    if (hours > 0) return `${hours}小时${minutes}分钟`
    return `${minutes}分钟`
  }

  // 创建交易员
  const handleCreate = async () => {
    if (!name.trim()) {
      alert('请输入交易员名称')
      return
    }

    setLoading(true)
    try {
      const config: any = {
        amount: parseFloat(amount),
        grid_gap: parseFloat(gridGap),
        check_interval: parseInt(checkInterval)
      }
      
      // 添加止损止盈（如果设置）
      if (stopLoss && parseFloat(stopLoss) < 0) {
        config.stop_loss_pct = parseFloat(stopLoss)
      }
      if (takeProfit && parseFloat(takeProfit) > 0) {
        config.take_profit_pct = parseFloat(takeProfit)
      }
      
      await apiClient.post('/api/traders', {
        name: name.trim(),
        strategy: 'grid',
        symbol: 'BTC/USDT',
        config
      })
      
      alert('交易员创建成功！')
      setShowCreateForm(false)
      setName('网格交易员')
      setStopLoss('')
      setTakeProfit('')
      await loadTraders()
    } catch (error: any) {
      alert('创建失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  // 启动交易员
  const handleStart = async (traderId: string) => {
    setLoading(true)
    try {
      await apiClient.post(`/api/traders/${traderId}/start`)
      alert('交易员已启动！')
      await loadTraders()
    } catch (error: any) {
      alert('启动失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  // 停止交易员
  const handleStop = async (traderId: string) => {
    setLoading(true)
    try {
      await apiClient.post(`/api/traders/${traderId}/stop`)
      alert('交易员已停止！')
      await loadTraders()
    } catch (error: any) {
      alert('停止失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  // 删除交易员
  const handleDelete = async (traderId: string, traderName: string) => {
    if (!confirm(`确定要删除交易员"${traderName}"吗？`)) {
      return
    }

    setLoading(true)
    try {
      await apiClient.delete(`/api/traders/${traderId}`)
      alert('交易员已删除！')
      await loadTraders()
    } catch (error: any) {
      alert('删除失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadTraders()
    loadBalance()
    
    // 每5秒刷新一次
    const interval = setInterval(() => {
      loadTraders()
      loadBalance()
      setCurrentTime(Date.now())
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>🤖 交易员管理</h1>
        <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
          {/* ✅ Phase 3.5 - P2: 账户余额显示 */}
          {balance && (
            <div style={{
              padding: '10px 20px',
              backgroundColor: '#f8f9fa',
              borderRadius: '6px',
              border: '1px solid #dee2e6',
              fontSize: '14px'
            }}>
              <span style={{ marginRight: '15px' }}>
                💵 USDT: <strong>{balance.usdt.free.toFixed(2)}</strong>
              </span>
              <span>
                ₿ BTC: <strong>{balance.btc.free.toFixed(6)}</strong>
              </span>
            </div>
          )}
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            style={{
              padding: '10px 20px',
              backgroundColor: showCreateForm ? '#95a5a6' : '#3498db',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: 'bold'
            }}
          >
            {showCreateForm ? '取消' : '➕ 创建交易员'}
          </button>
        </div>
      </div>

      {/* 创建表单 */}
      {showCreateForm && (
        <div style={{ 
          padding: '20px', 
          backgroundColor: '#f8f9fa', 
          borderRadius: '8px', 
          marginBottom: '20px',
          border: '1px solid #dee2e6'
        }}>
          <h3 style={{ margin: '0 0 15px 0' }}>创建新交易员</h3>
          
          <div style={{ display: 'grid', gap: '15px' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                交易员名称:
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="如：网格交易员1"
                style={{
                  width: '100%',
                  padding: '8px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  boxSizing: 'border-box'
                }}
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '15px' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', fontSize: '13px' }}>
                  每次交易量 (BTC):
                </label>
                <input
                  type="number"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  step="0.0001"
                  min="0.0001"
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    boxSizing: 'border-box'
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', fontSize: '13px' }}>
                  网格间隔 (%):
                </label>
                <input
                  type="number"
                  value={gridGap}
                  onChange={(e) => setGridGap(e.target.value)}
                  step="0.1"
                  min="0.1"
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    boxSizing: 'border-box'
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', fontSize: '13px' }}>
                  检查间隔 (秒):
                </label>
                <input
                  type="number"
                  value={checkInterval}
                  onChange={(e) => setCheckInterval(e.target.value)}
                  step="10"
                  min="10"
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    boxSizing: 'border-box'
                  }}
                />
              </div>
            </div>

            {/* ✅ Phase 3.5 - P1: 止损止盈配置（高级选项） */}
            <div>
              <button
                type="button"
                onClick={() => setShowAdvanced(!showAdvanced)}
                style={{
                  padding: '6px 12px',
                  backgroundColor: '#f8f9fa',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '13px',
                  marginBottom: '10px'
                }}
              >
                {showAdvanced ? '▼' : '▶'} 高级选项（止损止盈）
              </button>
              
              {showAdvanced && (
                <div style={{ 
                  padding: '15px', 
                  backgroundColor: '#fff3cd', 
                  borderRadius: '4px',
                  border: '1px solid #ffc107'
                }}>
                  <div style={{ marginBottom: '10px', fontSize: '13px', color: '#856404' }}>
                    ⚠️ 止损止盈触发后将自动卖出全部持仓并停止策略
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                    <div>
                      <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', fontSize: '13px' }}>
                        止损 (%)（负数，如-10）:
                      </label>
                      <input
                        type="number"
                        value={stopLoss}
                        onChange={(e) => setStopLoss(e.target.value)}
                        placeholder="不设置则留空"
                        step="1"
                        max="-1"
                        style={{
                          width: '100%',
                          padding: '8px',
                          border: '1px solid #ddd',
                          borderRadius: '4px',
                          boxSizing: 'border-box'
                        }}
                      />
                    </div>
                    <div>
                      <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', fontSize: '13px' }}>
                        止盈 (%)（正数，如20）:
                      </label>
                      <input
                        type="number"
                        value={takeProfit}
                        onChange={(e) => setTakeProfit(e.target.value)}
                        placeholder="不设置则留空"
                        step="1"
                        min="1"
                        style={{
                          width: '100%',
                          padding: '8px',
                          border: '1px solid #ddd',
                          borderRadius: '4px',
                          boxSizing: 'border-box'
                        }}
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>

            <button
              onClick={handleCreate}
              disabled={loading}
              style={{
                padding: '10px',
                backgroundColor: loading ? '#95a5a6' : '#27ae60',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: loading ? 'not-allowed' : 'pointer',
                fontWeight: 'bold'
              }}
            >
              {loading ? '创建中...' : '✅ 创建'}
            </button>
          </div>
        </div>
      )}

      {/* 交易员列表 */}
      <div style={{ display: 'grid', gap: '15px' }}>
        {traders.length === 0 ? (
          <div style={{ 
            padding: '40px', 
            textAlign: 'center', 
            backgroundColor: '#f8f9fa', 
            borderRadius: '8px',
            color: '#6c757d'
          }}>
            暂无交易员，点击上方按钮创建
          </div>
        ) : (
          traders.map((trader) => (
            <div
              key={trader.id}
              style={{
                padding: '20px',
                backgroundColor: 'white',
                borderRadius: '8px',
                border: `2px solid ${trader.status === 'running' ? '#27ae60' : '#ddd'}`,
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
                    <h3 style={{ margin: 0 }}>{trader.name}</h3>
                    <span
                      style={{
                        padding: '4px 12px',
                        borderRadius: '12px',
                        fontSize: '12px',
                        fontWeight: 'bold',
                        backgroundColor: trader.status === 'running' ? '#27ae60' : '#95a5a6',
                        color: 'white'
                      }}
                    >
                      {trader.status === 'running' ? '🟢 运行中' : '⚪ 已停止'}
                    </span>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '10px', marginBottom: '10px' }}>
                    <div>
                      <span style={{ color: '#7f8c8d', fontSize: '13px' }}>交易对:</span>
                      <div style={{ fontWeight: 'bold' }}>{trader.symbol}</div>
                    </div>
                    <div>
                      <span style={{ color: '#7f8c8d', fontSize: '13px' }}>创建时间:</span>
                      <div style={{ fontWeight: 'bold', fontSize: '12px' }}>
                        {new Date(trader.created_at * 1000).toLocaleString('zh-CN', {
                          month: '2-digit',
                          day: '2-digit',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </div>
                    </div>
                    <div>
                      <span style={{ color: '#7f8c8d', fontSize: '13px' }}>运行时长:</span>
                      <div style={{ fontWeight: 'bold', color: trader.status === 'running' ? '#27ae60' : '#7f8c8d' }}>
                        {formatRuntime(trader.created_at)}
                      </div>
                    </div>
                    <div>
                      <span style={{ color: '#7f8c8d', fontSize: '13px' }}>每次交易:</span>
                      <div style={{ fontWeight: 'bold' }}>{trader.config.amount} BTC</div>
                    </div>
                    <div>
                      <span style={{ color: '#7f8c8d', fontSize: '13px' }}>网格间隔:</span>
                      <div style={{ fontWeight: 'bold' }}>{trader.config.grid_gap}%</div>
                    </div>
                  </div>

                  {/* ✅ Phase 3.5 - P1: 盈亏显示 */}
                  {pnlData[trader.id] && (
                    <div style={{
                      padding: '12px',
                      backgroundColor: pnlData[trader.id].total_pnl >= 0 ? '#e8f5e9' : '#ffebee',
                      borderRadius: '6px',
                      marginBottom: '10px',
                      border: `2px solid ${pnlData[trader.id].total_pnl >= 0 ? '#4caf50' : '#f44336'}`
                    }}>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px', fontSize: '13px' }}>
                        <div>
                          <span style={{ color: '#7f8c8d' }}>总盈亏:</span>
                          <div style={{
                            fontWeight: 'bold',
                            fontSize: '16px',
                            color: pnlData[trader.id].total_pnl >= 0 ? '#2e7d32' : '#c62828'
                          }}>
                            {pnlData[trader.id].total_pnl >= 0 ? '+' : ''}{pnlData[trader.id].total_pnl.toFixed(2)} USDT
                          </div>
                        </div>
                        <div>
                          <span style={{ color: '#7f8c8d' }}>盈亏率:</span>
                          <div style={{
                            fontWeight: 'bold',
                            fontSize: '16px',
                            color: pnlData[trader.id].pnl_pct >= 0 ? '#2e7d32' : '#c62828'
                          }}>
                            {pnlData[trader.id].pnl_pct >= 0 ? '+' : ''}{pnlData[trader.id].pnl_pct.toFixed(2)}%
                          </div>
                        </div>
                        <div>
                          <span style={{ color: '#7f8c8d' }}>当前持仓:</span>
                          <div style={{ fontWeight: 'bold' }}>
                            {pnlData[trader.id].current_position.toFixed(6)} BTC
                          </div>
                        </div>
                        <div>
                          <span style={{ color: '#7f8c8d' }}>当前价值:</span>
                          <div style={{ fontWeight: 'bold' }}>
                            ${pnlData[trader.id].current_value.toFixed(2)}
                          </div>
                        </div>
                      </div>
                      <div style={{ marginTop: '8px', fontSize: '12px', color: '#666', borderTop: '1px solid #ddd', paddingTop: '8px' }}>
                        <span>已实现: {pnlData[trader.id].realized_pnl.toFixed(2)} USDT</span>
                        <span style={{ marginLeft: '15px' }}>未实现: {pnlData[trader.id].unrealized_pnl.toFixed(2)} USDT</span>
                        <span style={{ marginLeft: '15px' }}>总成本: {pnlData[trader.id].total_cost.toFixed(2)} USDT</span>
                      </div>
                    </div>
                  )}

                  {/* ✅ Phase 3.5 - P1: 止损止盈状态 */}
                  {(trader.config.stop_loss_pct || trader.config.take_profit_pct) && (
                    <div style={{
                      padding: '8px 12px',
                      backgroundColor: '#fff3cd',
                      borderRadius: '4px',
                      fontSize: '12px',
                      marginBottom: '10px',
                      border: '1px solid #ffc107'
                    }}>
                      {trader.config.stop_loss_pct && (
                        <span style={{ marginRight: '15px' }}>
                          🛡️ 止损: {trader.config.stop_loss_pct}%
                        </span>
                      )}
                      {trader.config.take_profit_pct && (
                        <span>
                          🎯 止盈: {trader.config.take_profit_pct}%
                        </span>
                      )}
                    </div>
                  )}

                  {trader.runtime_status && (
                    <div style={{ 
                      padding: '10px', 
                      backgroundColor: '#e8f5e9', 
                      borderRadius: '4px',
                      fontSize: '13px'
                    }}>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
                        <div>
                          <span style={{ color: '#7f8c8d' }}>上次价格:</span>
                          <strong style={{ marginLeft: '5px' }}>
                            {trader.runtime_status.last_price ? `$${trader.runtime_status.last_price.toLocaleString()}` : '-'}
                          </strong>
                        </div>
                        <div>
                          <span style={{ color: '#7f8c8d' }}>上次操作:</span>
                          <strong style={{ marginLeft: '5px', color: trader.runtime_status.last_action === 'buy' ? '#27ae60' : '#e74c3c' }}>
                            {trader.runtime_status.last_action === 'buy' ? '买入' : trader.runtime_status.last_action === 'sell' ? '卖出' : '-'}
                          </strong>
                        </div>
                        <div>
                          <span style={{ color: '#7f8c8d' }}>交易次数:</span>
                          <strong style={{ marginLeft: '5px' }}>{trader.runtime_status.trade_count}</strong>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                <div style={{ display: 'flex', gap: '10px', marginLeft: '20px', flexDirection: 'column' }}>
                  <button
                    onClick={() => onViewDetail(trader.id)}
                    style={{
                      padding: '8px 16px',
                      backgroundColor: '#3498db',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontWeight: 'bold',
                      whiteSpace: 'nowrap'
                    }}
                  >
                    📈 查看详情
                  </button>
                  
                  {trader.status === 'stopped' ? (
                    <button
                      onClick={() => handleStart(trader.id)}
                      disabled={loading}
                      style={{
                        padding: '8px 16px',
                        backgroundColor: loading ? '#95a5a6' : '#27ae60',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: loading ? 'not-allowed' : 'pointer',
                        fontWeight: 'bold'
                      }}
                    >
                      ▶️ 启动
                    </button>
                  ) : (
                    <button
                      onClick={() => handleStop(trader.id)}
                      disabled={loading}
                      style={{
                        padding: '8px 16px',
                        backgroundColor: loading ? '#95a5a6' : '#e74c3c',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: loading ? 'not-allowed' : 'pointer',
                        fontWeight: 'bold'
                      }}
                    >
                      ⏸️ 停止
                    </button>
                  )}
                  
                  <button
                    onClick={() => handleDelete(trader.id, trader.name)}
                    disabled={loading || trader.status === 'running'}
                    style={{
                      padding: '8px 16px',
                      backgroundColor: loading || trader.status === 'running' ? '#95a5a6' : '#e74c3c',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: loading || trader.status === 'running' ? 'not-allowed' : 'pointer',
                      fontWeight: 'bold'
                    }}
                  >
                    🗑️ 删除
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default Traders
