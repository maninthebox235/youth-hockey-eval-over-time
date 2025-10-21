import { useState, useEffect } from 'react'
import { Wifi, WifiOff, Plus, Users, ClipboardList, LogOut } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import PlayerList from './components/PlayerList'
import EvaluationForm from './components/EvaluationForm'
import EvaluationHistory from './components/EvaluationHistory'
import { useOfflineStorage } from './hooks/useOfflineStorage'
import { useAuth } from './contexts/AuthContext'
import { setAuthToken } from './services/api'
import Auth from './components/Auth'

function App() {
  const { user, token, logout, isLoading } = useAuth()
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const [activeTab, setActiveTab] = useState('players')
  const { players, evaluations, addPlayer, addEvaluation, syncData, pendingSync } = useOfflineStorage()

  useEffect(() => {
    if (token) {
      setAuthToken(token)
    }
  }, [token])

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

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return <Auth />
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-blue-600 text-white p-4 shadow-lg sticky top-0 z-50">
        <div className="container mx-auto flex justify-between items-center">
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold">🏒 Hockey Eval</h1>
            <span className="text-sm opacity-75">
              {user.full_name || user.username}
            </span>
          </div>
          <div className="flex items-center gap-4">
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
            <Button
              variant="ghost"
              size="sm"
              onClick={logout}
              className="text-white hover:bg-blue-700"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
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
                <EvaluationHistory evaluations={evaluations} players={players} />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}

export default App
