#!/bin/bash
# 夜间监控脚本 - 记录所有重要事件

LOG_FILE="night_report_$(date +%Y%m%d).txt"

echo "==================================" > $LOG_FILE
echo "夜间交易报告 - $(date '+%Y-%m-%d %H:%M:%S')" >> $LOG_FILE
echo "==================================" >> $LOG_FILE
echo "" >> $LOG_FILE

# 记录初始状态
echo "【初始状态】" >> $LOG_FILE
grep "trader_1763316274" uvicorn.log | tail -3 >> $LOG_FILE
echo "" >> $LOG_FILE

# 持续监控（每5分钟检查一次）
while true; do
    sleep 300  # 5分钟
    
    # 检查新交易
    new_trades=$(grep "trader_1763316274" uvicorn.log | grep -E "买入成功|卖出成功" | tail -5)
    if [ ! -z "$new_trades" ]; then
        echo "【$(date '+%H:%M:%S') 检测到交易】" >> $LOG_FILE
        echo "$new_trades" >> $LOG_FILE
        echo "" >> $LOG_FILE
    fi
    
    # 检查异常
    errors=$(grep "trader_1763316274" uvicorn.log | grep -E "ERROR|Exception|失败" | tail -3)
    if [ ! -z "$errors" ]; then
        echo "【$(date '+%H:%M:%S') 检测到异常】" >> $LOG_FILE
        echo "$errors" >> $LOG_FILE
        echo "" >> $LOG_FILE
    fi
done
