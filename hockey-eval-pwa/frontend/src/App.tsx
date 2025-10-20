import { useState, useEffect } from 'react'
import { Wifi, WifiOff, Plus, Users, ClipboardList } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import PlayerList from './components/PlayerList'
import EvaluationForm from './components/EvaluationForm'
import EvaluationHistory from './components/EvaluationHistory'
import { useOfflineStorage } from './hooks/useOfflineStorage'

function App() {
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const [activeTab, setActiveTab] = useState('players')
  const { players, evaluations, addPlayer, addEvaluation, syncData, pendingSync } = useOfflineStorage()

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true)
      syncData()
    }
    const handleOffline = () => setIsOnline(false)

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [syncData])

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-blue-600 text-white p-4 shadow-lg sticky top-0 z-50">
        <div className="container mx-auto flex justify-between items-center">
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold">🏒 Hockey Eval</h1>
          </div>
          <div className="flex items-center gap-2">
            {pendingSync > 0 && (
              <span className="text-sm bg-yellow-500 px-2 py-1 rounded">
                {pendingSync} pending
              </span>
            )}
            {isOnline ? (
              <Wifi className="w-5 h-5" />
            ) : (
              <WifiOff className="w-5 h-5 text-yellow-300" />
            )}
          </div>
        </div>
      </header>

      <main className="container mx-auto p-4 max-w-4xl">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3 mb-4">
            <TabsTrigger value="players" className="flex items-center gap-2">
              <Users className="w-4 h-4" />
              Players
            </TabsTrigger>
            <TabsTrigger value="evaluate" className="flex items-center gap-2">
              <Plus className="w-4 h-4" />
              Evaluate
            </TabsTrigger>
            <TabsTrigger value="history" className="flex items-center gap-2">
              <ClipboardList className="w-4 h-4" />
              History
            </TabsTrigger>
          </TabsList>

          <TabsContent value="players">
            <Card>
              <CardHeader>
                <CardTitle>Player Roster</CardTitle>
                <CardDescription>
                  Manage your team roster. Works offline.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <PlayerList players={players} addPlayer={addPlayer} />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="evaluate">
            <Card>
              <CardHeader>
                <CardTitle>Quick Evaluation</CardTitle>
                <CardDescription>
                  Evaluate players during practice or games. Data saves locally if offline.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <EvaluationForm players={players} addEvaluation={addEvaluation} />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="history">
            <Card>
              <CardHeader>
                <CardTitle>Evaluation History</CardTitle>
                <CardDescription>
                  View past evaluations and track progress over time.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <EvaluationHistory evaluations={evaluations} />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}

export default App
