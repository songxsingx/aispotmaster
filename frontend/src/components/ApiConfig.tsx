import { useState, useEffect } from 'react'
import { apiClient } from '../api/client'

interface ConfigData {
  testnet: boolean
  has_api_key: boolean
  demo_mode: boolean
}

interface Props {
  onConfigUpdate?: () => void
}

function ApiConfig({ onConfigUpdate }: Props) {
  const [config, setConfig] = useState<ConfigData | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [apiKey, setApiKey] = useState('')
  const [apiSecret, setApiSecret] = useState('')
  const [testnet, setTestnet] = useState(true)
  const [saving, setSaving] = useState(false)

  const loadConfig = async () => {
    try {
      const response = await apiClient.get('/api/config')
      setConfig(response.data.data)
    } catch (error) {
      console.error('加载配置失败:', error)
    }
  }

  const handleSave = async () => {
    if (!apiKey || !apiSecret) {
      alert('请输入API Key和Secret')
      return
    }

    setSaving(true)
    try {
      await apiClient.post(`/api/config?api_key=${encodeURIComponent(apiKey)}&api_secret=${encodeURIComponent(apiSecret)}&testnet=${testnet}`)
      alert('API配置已保存！')
      setShowForm(false)
      setApiKey('')
      setApiSecret('')
      await loadConfig()
      onConfigUpdate?.()
    } catch (error: any) {
      alert('保存失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setSaving(false)
    }
  }

  useEffect(() => {
    loadConfig()
  }, [])

  return (
    <div style={{ 
      padding: '15px', 
      backgroundColor: config?.demo_mode ? '#fff3cd' : '#d4edda', 
      borderRadius: '8px',
      border: `2px solid ${config?.demo_mode ? '#ffc107' : '#28a745'}`,
      marginBottom: '20px'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h3 style={{ margin: '0 0 5px 0', fontSize: '16px' }}>
            {config?.demo_mode ? '⚠️ 演示模式' : '✅ 真实交易模式'}
          </h3>
          <p style={{ margin: 0, fontSize: '13px', color: '#666' }}>
            {config?.demo_mode ? (
              '当前使用模拟数据，点击配置按钮添加Gate.io API密钥以连接真实交易所'
            ) : (
              `已连接Gate.io ${config?.testnet ? '测试网' : '正式网'}`
            )}
          </p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          style={{
            padding: '8px 16px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: 'bold'
          }}
        >
          {showForm ? '取消' : '⚙️ 配置API'}
        </button>
      </div>

      {showForm && (
        <div style={{ 
          marginTop: '15px', 
          padding: '15px', 
          backgroundColor: 'white', 
          borderRadius: '6px',
          border: '1px solid #ddd'
        }}>
          <h4 style={{ margin: '0 0 10px 0' }}>Gate.io API 配置</h4>
          
          <div style={{ marginBottom: '10px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', fontSize: '13px' }}>
              API Key:
            </label>
            <input
              type="text"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="输入你的Gate.io API Key"
              style={{
                width: '100%',
                padding: '8px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '13px',
                boxSizing: 'border-box'
              }}
            />
          </div>

          <div style={{ marginBottom: '10px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', fontSize: '13px' }}>
              API Secret:
            </label>
            <input
              type="password"
              value={apiSecret}
              onChange={(e) => setApiSecret(e.target.value)}
              placeholder="输入你的Gate.io API Secret"
              style={{
                width: '100%',
                padding: '8px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '13px',
                boxSizing: 'border-box'
              }}
            />
          </div>

          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'flex', alignItems: 'center', fontSize: '13px', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={testnet}
                onChange={(e) => setTestnet(e.target.checked)}
                style={{ marginRight: '8px' }}
              />
              使用测试网（推荐新手使用）
            </label>
          </div>

          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              onClick={handleSave}
              disabled={saving}
              style={{
                flex: 1,
                padding: '10px',
                backgroundColor: saving ? '#95a5a6' : '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: saving ? 'not-allowed' : 'pointer',
                fontWeight: 'bold',
                fontSize: '14px'
              }}
            >
              {saving ? '保存中...' : '💾 保存配置'}
            </button>
          </div>

          <div style={{ 
            marginTop: '10px', 
            padding: '10px', 
            backgroundColor: '#e7f3ff', 
            borderRadius: '4px',
            fontSize: '12px',
            color: '#004085'
          }}>
            <strong>📌 提示：</strong>
            <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
              <li>前往 <a href="https://www.gate.io/myaccount/apiv4keys" target="_blank" rel="noopener noreferrer">Gate.io API管理页面</a> 创建API密钥</li>
              <li>测试网地址：<a href="https://www.gate.io/testnet" target="_blank" rel="noopener noreferrer">gate.io/testnet</a></li>
              <li>API密钥将保存在本地.env文件中</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}

export default ApiConfig
