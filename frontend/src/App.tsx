import { useState } from 'react'
import Trading from './pages/Trading'
import Traders from './pages/Traders'
import TraderDetail from './pages/TraderDetail'

function App() {
  const [currentPage, setCurrentPage] = useState<'trading' | 'traders' | 'trader-detail'>('trading')
  const [selectedTraderId, setSelectedTraderId] = useState<string>('')

  // ✅ 进入交易员详情
  const handleViewTraderDetail = (traderId: string) => {
    setSelectedTraderId(traderId)
    setCurrentPage('trader-detail')
  }

  // ✅ 返回交易员列表
  const handleBackToTraders = () => {
    setCurrentPage('traders')
    setSelectedTraderId('')
  }

  return (
    <div>
      {/* 导航栏 */}
      <div style={{ 
        backgroundColor: '#2c3e50', 
        padding: '15px 20px', 
        display: 'flex', 
        gap: '20px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <button
          onClick={() => setCurrentPage('trading')}
          style={{
            padding: '10px 20px',
            backgroundColor: currentPage === 'trading' ? '#3498db' : 'transparent',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontWeight: 'bold',
            fontSize: '14px'
          }}
        >
          💱 手动交易
        </button>
        <button
          onClick={() => setCurrentPage('traders')}
          style={{
            padding: '10px 20px',
            backgroundColor: currentPage === 'traders' ? '#3498db' : 'transparent',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontWeight: 'bold',
            fontSize: '14px'
          }}
        >
          🤖 交易员管理
        </button>
      </div>

      {/* 页面内容 */}
      {currentPage === 'trading' && <Trading />}
      {currentPage === 'traders' && <Traders onViewDetail={handleViewTraderDetail} />}
      {currentPage === 'trader-detail' && selectedTraderId && (
        <TraderDetail traderId={selectedTraderId} onBack={handleBackToTraders} />
      )}
    </div>
  )
}

export default App
