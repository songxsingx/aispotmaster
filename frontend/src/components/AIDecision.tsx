import { useState } from 'react'
import { apiClient } from '../api/client'

interface AIDecisionData {
  action: 'buy' | 'sell' | 'wait'
  reasoning: string
  confidence: number
  market_data: {
    symbol: string
    price: number
    change_24h: number
    high_24h: number
    low_24h: number
    position: number
    balance: number
  }
}

function AIDecision() {
  const [decision, setDecision] = useState<AIDecisionData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const getAIDecision = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await apiClient.post('/api/ai/decide', {
        symbol: 'BTC/USDT'
      })
      setDecision(response.data.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'AI决策失败')
    } finally {
      setLoading(false)
    }
  }

  const getActionColor = (action: string) => {
    if (action === 'buy') return '#27ae60'
    if (action === 'sell') return '#e74c3c'
    return '#95a5a6'
  }

  const getActionText = (action: string) => {
    if (action === 'buy') return '🟢 买入'
    if (action === 'sell') return '🔴 卖出'
    return '⚪ 等待'
  }

  return (
    <div style={{ 
      padding: '20px', 
      backgroundColor: '#ffffff', 
      borderRadius: '8px', 
      border: '1px solid #ddd',
      marginBottom: '20px'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
        <h3 style={{ margin: 0 }}>🤖 AI交易建议</h3>
        <button
          onClick={getAIDecision}
          disabled={loading}
          style={{
            padding: '8px 16px',
            backgroundColor: loading ? '#95a5a6' : '#3498db',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontWeight: 'bold'
          }}
        >
          {loading ? '分析中...' : '🧠 获取AI建议'}
        </button>
      </div>

      {error && (
        <div style={{ 
          padding: '10px', 
          backgroundColor: '#ffe6e6', 
          borderRadius: '4px', 
          color: '#c0392b',
          marginBottom: '10px'
        }}>
          ⚠️ {error}
        </div>
      )}

      {decision && (
        <div>
          {/* AI决策结果 */}
          <div style={{ 
            padding: '15px', 
            backgroundColor: '#f8f9fa', 
            borderRadius: '8px',
            marginBottom: '15px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
              <span style={{ fontSize: '14px', color: '#7f8c8d' }}>AI决策：</span>
              <strong style={{ 
                fontSize: '18px', 
                color: getActionColor(decision.action),
                padding: '4px 12px',
                borderRadius: '4px',
                backgroundColor: 'white'
              }}>
                {getActionText(decision.action)}
              </strong>
              <span style={{ 
                fontSize: '12px', 
                color: '#7f8c8d',
                marginLeft: 'auto'
              }}>
                置信度: {(decision.confidence * 100).toFixed(0)}%
              </span>
            </div>

            <div style={{ 
              padding: '10px', 
              backgroundColor: 'white', 
              borderRadius: '4px',
              borderLeft: '3px solid #3498db'
            }}>
              <div style={{ fontSize: '13px', color: '#7f8c8d', marginBottom: '5px' }}>💡 AI分析：</div>
              <div style={{ fontSize: '14px', color: '#2c3e50', lineHeight: '1.6' }}>
                {decision.reasoning}
              </div>
            </div>
          </div>

          {/* 市场数据 */}
          <div style={{ 
            padding: '15px', 
            backgroundColor: '#ecf0f1', 
            borderRadius: '8px'
          }}>
            <div style={{ fontSize: '13px', color: '#7f8c8d', marginBottom: '10px' }}>📊 参考数据：</div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
              <div>
                <div style={{ fontSize: '11px', color: '#95a5a6' }}>当前价格</div>
                <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#2c3e50' }}>
                  ${decision.market_data.price.toLocaleString()}
                </div>
              </div>
              <div>
                <div style={{ fontSize: '11px', color: '#95a5a6' }}>24h涨跌</div>
                <div style={{ 
                  fontSize: '14px', 
                  fontWeight: 'bold',
                  color: decision.market_data.change_24h >= 0 ? '#27ae60' : '#e74c3c'
                }}>
                  {decision.market_data.change_24h >= 0 ? '+' : ''}
                  {decision.market_data.change_24h.toFixed(2)}%
                </div>
              </div>
              <div>
                <div style={{ fontSize: '11px', color: '#95a5a6' }}>24h波动</div>
                <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#2c3e50' }}>
                  ${decision.market_data.low_24h.toLocaleString()} - ${decision.market_data.high_24h.toLocaleString()}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {!decision && !loading && !error && (
        <div style={{ 
          padding: '40px', 
          textAlign: 'center', 
          color: '#95a5a6',
          fontSize: '14px'
        }}>
          点击上方按钮获取AI交易建议
        </div>
      )}
    </div>
  )
}

export default AIDecision
