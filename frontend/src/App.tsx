import { useState } from 'react'
import Trading from './pages/Trading'
import Traders from './pages/Traders'

function App() {
  const [currentPage, setCurrentPage] = useState<'trading' | 'traders'>('trading')

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
      {currentPage === 'trading' ? <Trading /> : <Traders />}
    </div>
  )
}

export default App
