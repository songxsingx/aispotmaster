"""交易员引擎 - 管理策略运行"""
import json
import sqlite3
import threading
import time
from typing import Dict, Optional
from core.exchange import GateIOExchange
from strategy.grid import GridStrategy
from config import settings


class TraderEngine:
    """交易员引擎"""
    
    def __init__(self):
        """初始化交易员引擎"""
        self.traders: Dict[str, threading.Thread] = {}  # trader_id -> thread
        self.strategies: Dict[str, GridStrategy] = {}  # trader_id -> strategy
        self.exchange = GateIOExchange(
            api_key=settings.gate_api_key,
            api_secret=settings.gate_api_secret,
            testnet=settings.gate_testnet
        )
        
        # ✅ Phase 3.5 - P2: 监控告警
        self.last_heartbeat: Dict[str, float] = {}  # trader_id -> timestamp
        self.alert_log: list = []  # 告警日志
        
        # 初始化数据库
        self._init_database()
        
        # 启动监控线程
        self._start_monitor()
    
    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        
        # 执行traders表迁移
        with open('data/migrations/002_traders.sql', 'r') as f:
            cursor.executescript(f.read())
        
        # ✅ Phase 3.5 - P0: 执行持仓追踪迁移（忽略重复字段错误）
        try:
            # 读取并执行迁移脚本，但忽略ALTER TABLE重复错误
            with open('data/migrations/003_position_tracking.sql', 'r') as f:
                migration_sql = f.read()
                # 逐条执行SQL，忽略重复字段错误
                for statement in migration_sql.split(';'):
                    statement = statement.strip()
                    if statement and not statement.startswith('--'):
                        try:
                            cursor.execute(statement)
                        except sqlite3.OperationalError as e:
                            # 忽略"duplicate column"错误
                            if 'duplicate column' not in str(e).lower():
                                print(f"⚠️ 数据库迁移警告: {e}")
            conn.commit()
            print("✅ 持仓追踪迁移完成")
        except Exception as e:
            print(f"⚠️ 持仓追踪迁移失败: {e}")
        
        # 重置所有running状态为stopped（因为后端重启后线程丢失）
        cursor.execute("UPDATE traders SET status = 'stopped' WHERE status = 'running'")
        
        conn.commit()
        conn.close()
    
    def create_trader(self, trader_id: str, name: str, strategy: str, symbol: str, config: Dict) -> Dict:
        """
        创建交易员
        
        Args:
            trader_id: 交易员ID
            name: 交易员名称
            strategy: 策略类型（目前只支持'grid'）
            symbol: 交易对
            config: 策略配置
            
        Returns:
            交易员信息
        """
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO traders (id, name, strategy, symbol, status, config)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (trader_id, name, strategy, symbol, 'stopped', json.dumps(config)))
        
        conn.commit()
        conn.close()
        
        return {
            'id': trader_id,
            'name': name,
            'strategy': strategy,
            'symbol': symbol,
            'status': 'stopped',
            'config': config
        }
    
    def get_trader(self, trader_id: str) -> Optional[Dict]:
        """获取交易员信息"""
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM traders WHERE id = ?', (trader_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            'id': row[0],
            'name': row[1],
            'strategy': row[2],
            'symbol': row[3],
            'status': row[4],
            'config': json.loads(row[5]),
            'created_at': row[6],
            'updated_at': row[7]
        }
    
    def list_traders(self) -> list:
        """获取所有交易员"""
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM traders ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        traders = []
        for row in rows:
            trader = {
                'id': row[0],
                'name': row[1],
                'strategy': row[2],
                'symbol': row[3],
                'status': row[4],
                'config': json.loads(row[5]),
                'created_at': row[6],
                'updated_at': row[7]
            }
            
            # 如果正在运行，添加实时状态
            if row[0] in self.strategies:
                trader['runtime_status'] = self.strategies[row[0]].get_status()
            
            traders.append(trader)
        
        return traders
    
    def start_trader(self, trader_id: str) -> bool:
        """
        启动交易员
        
        Args:
            trader_id: 交易员ID
            
        Returns:
            是否启动成功
        """
        # 检查是否已经在运行
        if trader_id in self.traders and self.traders[trader_id].is_alive():
            return False
        
        # 获取交易员配置
        trader = self.get_trader(trader_id)
        if not trader:
            return False
        
        # 创建策略实例
        if trader['strategy'] == 'grid':
            strategy = GridStrategy(
                trader_id=trader_id,
                symbol=trader['symbol'],
                config=trader['config'],
                exchange=self.exchange
            )
        else:
            return False
        
        # 在新线程中运行策略
        thread = threading.Thread(target=strategy.run, daemon=True)
        thread.start()
        
        # 保存引用
        self.traders[trader_id] = thread
        self.strategies[trader_id] = strategy
        
        # ✅ Phase 3.5 - P2: 初始化心跳
        self.update_heartbeat(trader_id)
        
        # 更新数据库状态
        self._update_trader_status(trader_id, 'running')
        
        return True
    
    def stop_trader(self, trader_id: str) -> bool:
        """
        停止交易员
        
        Args:
            trader_id: 交易员ID
            
        Returns:
            是否停止成功
        """
        if trader_id not in self.strategies:
            return False
        
        # 停止策略
        self.strategies[trader_id].stop()
        
        # 等待线程结束（最多5秒）
        if trader_id in self.traders:
            self.traders[trader_id].join(timeout=5)
            del self.traders[trader_id]
        
        del self.strategies[trader_id]
        
        # 更新数据库状态
        self._update_trader_status(trader_id, 'stopped')
        
        return True
    
    def _update_trader_status(self, trader_id: str, status: str):
        """更新交易员状态"""
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE traders 
            SET status = ?, updated_at = strftime('%s', 'now')
            WHERE id = ?
        ''', (status, trader_id))
        
        conn.commit()
        conn.close()
    
    def delete_trader(self, trader_id: str) -> bool:
        """删除交易员"""
        # 如果正在运行，先停止
        if trader_id in self.strategies:
            self.stop_trader(trader_id)
        
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM traders WHERE id = ?', (trader_id,))
        affected = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return affected > 0
    
    def _start_monitor(self):
        """✅ Phase 3.5 - P2: 启动监控线程"""
        monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        monitor_thread.start()
        print("✅ 监控告警系统已启动")
    
    def _monitor_loop(self):
        """监控循环"""
        while True:
            try:
                self._check_balance_alert()
                self._check_position_alert()
                self._check_heartbeat_alert()
            except Exception as e:
                print(f"⚠️ 监控异常: {e}")
            
            time.sleep(60)  # 每分钟检查一次
    
    def _check_balance_alert(self):
        """✅ Phase 3.5 - P2: 余额预警"""
        try:
            balance = self.exchange.get_balance('USDT')
            usdt_free = balance.get('free', 0)
            
            if usdt_free < 10:
                alert_msg = f"⚠️ 余额预警: USDT余额不足 ({usdt_free:.2f} USDT < 10 USDT)"
                self._log_alert('balance', alert_msg)
        except Exception as e:
            print(f"余额检查失败: {e}")
    
    def _check_position_alert(self):
        """✅ Phase 3.5 - P2: 持仓异常预警"""
        try:
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            
            # 检查所有交易员的最新持仓
            cursor.execute("""
                SELECT trader_id, position_after 
                FROM trades 
                WHERE id IN (
                    SELECT MAX(id) FROM trades GROUP BY trader_id
                )
                AND position_after < 0
            """)
            
            negative_positions = cursor.fetchall()
            conn.close()
            
            for trader_id, position in negative_positions:
                alert_msg = f"🚨 持仓异常: {trader_id} 出现负持仓 ({position:.6f} BTC)"
                self._log_alert('position', alert_msg)
        except Exception as e:
            print(f"持仓检查失败: {e}")
    
    def _check_heartbeat_alert(self):
        """✅ Phase 3.5 - P2: 心跳检测"""
        current_time = time.time()
        
        for trader_id, strategy in self.strategies.items():
            if trader_id in self.last_heartbeat:
                elapsed = current_time - self.last_heartbeat[trader_id]
                
                # 5分钟无更新
                if elapsed > 300:
                    alert_msg = f"💔 心跳异常: {trader_id} 已 {int(elapsed/60)} 分钟无响应"
                    self._log_alert('heartbeat', alert_msg)
    
    def _log_alert(self, alert_type: str, message: str):
        """✅ Phase 3.5 - P2: 记录告警"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        alert_entry = {
            'type': alert_type,
            'message': message,
            'timestamp': timestamp
        }
        
        self.alert_log.append(alert_entry)
        print(f"[{timestamp}] {message}")
        
        # 保留最近100条告警
        if len(self.alert_log) > 100:
            self.alert_log = self.alert_log[-100:]
    
    def update_heartbeat(self, trader_id: str):
        """✅ Phase 3.5 - P2: 更新心跳"""
        self.last_heartbeat[trader_id] = time.time()


# 全局交易员引擎实例
trader_engine = TraderEngine()
