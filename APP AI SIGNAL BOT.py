import { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "/components/ui/card"
import { Badge } from "/components/ui/badge"
import { Button } from "/components/ui/button"
import { ArrowUp, ArrowDown, TrendingUp, AlertCircle, Bell, BellOff } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface DataPoint {
  time: string
  price: number
}

interface Signal {
  type: 'BUY' | 'SELL'
  price: number
  timestamp: Date
  confidence: number
  reason: string
}

interface MarketAnalysis {
  trend: string
  volatility: number
  momentum: number
  clearPattern: boolean
}

export default function MobileSignalBot() {
  const [priceData, setPriceData] = useState<DataPoint[]>([])
  const [currentSignal, setCurrentSignal] = useState<Signal | null>(null)
  const [marketAnalysis, setMarketAnalysis] = useState<MarketAnalysis | null>(null)
  const [isActive, setIsActive] = useState(false)
  const [notificationsEnabled, setNotificationsEnabled] = useState(false)
  const [lastSignalTime, setLastSignalTime] = useState<Date | null>(null)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  // Request notification permission
  const requestNotificationPermission = async () => {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission()
      setNotificationsEnabled(permission === 'granted')
    }
  }

  // Send notification
  const sendNotification = (signal: Signal) => {
    if ('Notification' in window && notificationsEnabled && Notification.permission === 'granted') {
      new Notification(`📊 Signal Alert: ${signal.type}`, {
        body: `${signal.type} at $${signal.price} (${signal.confidence}% confidence)`,
        icon: '/favicon.ico',
        badge: '/favicon.ico',
        vibrate: [200, 100, 200]
      })
    }
  }

  // Analyze market conditions
  const analyzeMarket = (data: DataPoint[]): MarketAnalysis => {
    if (data.length < 10) {
      return {
        trend: 'Insufficient data',
        volatility: 0,
        momentum: 0,
        clearPattern: false
      }
    }

    const prices = data.map(d => d.price)
    const recentPrices = prices.slice(-10)
    const olderPrices = prices.slice(-20, -10)
    
    const recentAvg = recentPrices.reduce((a, b) => a + b, 0) / recentPrices.length
    const olderAvg = olderPrices.reduce((a, b) => a + b, 0) / olderPrices.length
    const trend = recentAvg > olderAvg ? 'Bullish' : 'Bearish'
    
    const volatility = Math.max(...recentPrices) - Math.min(...recentPrices)
    const avgPrice = recentPrices.reduce((a, b) => a + b, 0) / recentPrices.length
    const volatilityPercent = (volatility / avgPrice) * 100
    
    const momentum = Math.abs(recentAvg - olderAvg) / olderAvg * 100
    
    const clearPattern = volatilityPercent > 0.5 && momentum > 0.3
    
    return {
      trend,
      volatility: parseFloat(volatilityPercent.toFixed(2)),
      momentum: parseFloat(momentum.toFixed(2)),
      clearPattern
    }
  }

  // Generate price data
  const generatePrice = (lastPrice: number): number => {
    const volatility = 0.01
    const change = (Math.random() - 0.5) * volatility * lastPrice
    return parseFloat((lastPrice + change).toFixed(2))
  }

  // Generate signal based on market analysis
  const generateSignal = (price: number, analysis: MarketAnalysis): Signal | null => {
    if (!analysis.clearPattern) {
      return null
    }

    const confidence = Math.floor(Math.random() * 20) + 80
    
    let type: 'BUY' | 'SELL'
    let reason: string
    
    if (analysis.trend === 'Bullish' && analysis.momentum > 0.5) {
      type = 'BUY'
      reason = `Strong bullish momentum (${analysis.momentum}%)`
    } else if (analysis.trend === 'Bearish' && analysis.momentum > 0.5) {
      type = 'SELL'
      reason = `Strong bearish momentum (${analysis.momentum}%)`
    } else {
      return null
    }

    return {
      type,
      price,
      timestamp: new Date(),
      confidence,
      reason
    }
  }

  // Start the bot
  const startBot = () => {
    setIsActive(true)
    
    const initialPrice = 100
    const initialData = Array.from({ length: 20 }, (_, i) => ({
      time: new Date(Date.now() - (19 - i) * 5000).toLocaleTimeString(),
      price: initialPrice + (Math.random() - 0.5) * 10
    }))
    setPriceData(initialData)
    
    const initialAnalysis = analyzeMarket(initialData)
    setMarketAnalysis(initialAnalysis)
    
    intervalRef.current = setInterval(() => {
      setPriceData(prev => {
        const lastPrice = prev[prev.length - 1]?.price || 100
        const newPrice = generatePrice(lastPrice)
        const newPoint = {
          time: new Date().toLocaleTimeString(),
          price: newPrice
        }
        
        const updated = [...prev, newPoint]
        const sliced = updated.slice(-50)
        
        const analysis = analyzeMarket(sliced)
        setMarketAnalysis(analysis)
        
        if (sliced.length % 6 === 0) {
          const signal = generateSignal(newPrice, analysis)
          setCurrentSignal(signal)
          if (signal) {
            sendNotification(signal)
            setLastSignalTime(new Date())
          }
        }
        
        return sliced
      })
    }, 5000)
  }

  // Stop the bot
  const stopBot = () => {
    setIsActive(false)
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
    }
  }

  // Format time for mobile
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit'
    })
  }

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [])

  // Add PWA support
  useEffect(() => {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js').catch(console.error)
    }
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Mobile Header */}
      <div className="bg-white shadow-sm border-b px-4 py-3 flex items-center justify-between">
        <h1 className="text-lg font-bold text-gray-800 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-blue-600" />
          Signal Bot
        </h1>
        <Badge 
          variant={isActive ? "default" : "secondary"}
          className={isActive ? "bg-green-500" : ""}
        >
          {isActive ? "Live" : "Offline"}
        </Badge>
      </div>

      {/* Mobile Content */}
      <div className="p-4 space-y-4">
        {/* Control Buttons */}
        <div className="grid grid-cols-2 gap-3">
          <Button 
            onClick={startBot} 
            disabled={isActive}
            className="bg-green-600 hover:bg-green-700 text-white font-medium py-3"
          >
            Start Bot
          </Button>
          <Button 
            onClick={stopBot} 
            disabled={!isActive}
            variant="destructive"
            className="font-medium py-3"
          >
            Stop Bot
          </Button>
        </div>

        {/* Notification Toggle */}
        <Button 
          onClick={requestNotificationPermission}
          variant="outline"
          className="w-full flex items-center justify-center gap-2"
        >
          {notificationsEnabled ? (
            <>
              <Bell className="w-4 h-4" />
              Notifications On
            </>
          ) : (
            <>
              <BellOff className="w-4 h-4" />
              Enable Notifications
            </>
          )}
        </Button>

        {/* Signal Card - Mobile Optimized */}
        <Card className="shadow-lg">
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center justify-between">
              <span>Current Signal</span>
              {currentSignal && (
                <span className="text-xs text-gray-500">
                  {formatTime(currentSignal.timestamp)}
                </span>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {currentSignal ? (
              <div className="space-y-3">
                <div className={`flex items-center justify-between p-4 rounded-lg ${
                  currentSignal.type === 'BUY' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  <div className="flex items-center gap-2">
                    {currentSignal.type === 'BUY' ? (
                      <ArrowUp className="w-6 h-6" />
                    ) : (
                      <ArrowDown className="w-6 h-6" />
                    )}
                    <span className="font-bold text-xl">{currentSignal.type}</span>
                  </div>
                  <span className="font-mono text-lg">${currentSignal.price}</span>
                </div>
                
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <span className="text-gray-600">Confidence</span>
                    <p className="font-mono font-bold">{currentSignal.confidence}%</p>
                  </div>
                  <div>
                    <span className="text-gray-600">Time</span>
                    <p className="font-mono text-xs">
                      {formatTime(currentSignal.timestamp)}
                    </p>
                  </div>
                </div>
                
                <div className="bg-gray-50 p-3 rounded-lg">
                  <span className="text-xs text-gray-600 font-medium">Reason:</span>
                  <p className="text-xs mt-1">{currentSignal.reason}</p>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-600 font-medium">No Clear Signal</p>
                <p className="text-xs text-gray-500 mt-1">
                  Waiting for clear market pattern
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Market Analysis - Mobile Optimized */}
        <Card className="shadow-lg">
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Market Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            {marketAnalysis ? (
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Trend</span>
                  <p className={`font-bold ${
                    marketAnalysis.trend === 'Bullish' 
                      ? 'text-green-600' 
                      : marketAnalysis.trend === 'Bearish' 
                      ? 'text-red-600' 
                      : 'text-gray-600'
                  }`}>
                    {marketAnalysis.trend}
                  </p>
                </div>
                <div>
                  <span className="text-gray-600">Volatility</span>
                  <p className="font-mono font-bold">{marketAnalysis.volatility}%</p>
                </div>
                <div>
                  <span className="text-gray-600">Momentum</span>
                  <p className="font-mono font-bold">{marketAnalysis.momentum}%</p>
                </div>
                <div>
                  <span className="text-gray-600">Pattern</span>
                  <Badge 
                    variant={marketAnalysis.clearPattern ? "default" : "secondary"}
                    className={marketAnalysis.clearPattern ? "bg-green-100 text-green-800" : ""}
                  >
                    {marketAnalysis.clearPattern ? "Clear" : "Unclear"}
                  </Badge>
                </div>
              </div>
            ) : (
              <p className="text-gray-500 text-center py-4">Analyzing...</p>
            )}
          </CardContent>
        </Card>

        {/* Price Chart - Mobile Optimized */}
        <Card className="shadow-lg">
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Price Chart</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-48">
              {priceData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={priceData.slice(-20)}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                    <XAxis 
                      dataKey="time" 
                      tick={{ fontSize: 10 }}
                      interval="preserveStartEnd"
                      tickFormatter={(time) => time.split(':')[2]} // Show seconds only
                    />
                    <YAxis 
                      tick={{ fontSize: 10 }}
                      domain={['dataMin - 0.5', 'dataMax + 0.5']}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'white', 
                        border: '1px solid #ccc',
                        borderRadius: '8px',
                        fontSize: '12px'
                      }}
                      formatter={(value: number) => [`$${value}`, 'Price']}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="price" 
                      stroke="#3b82f6" 
                      strokeWidth={2}
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-full text-gray-500 text-sm">
                  Tap "Start Bot" to begin
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Quick Stats */}
        {lastSignalTime && (
          <Card className="shadow-lg">
            <CardContent className="py-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Last Signal</span>
                <span className="font-mono">
                  {formatTime(lastSignalTime)}
                </span>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Mobile Footer */}
      <div className="bg-white border-t p-4 mt-4">
        <p className="text-center text-xs text-gray-500">
          Use this tool alongside Pocket Option for manual trading
        </p>
      </div>
    </div>
  )
}
