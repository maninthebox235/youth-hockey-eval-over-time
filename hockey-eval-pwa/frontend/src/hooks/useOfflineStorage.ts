import { useState, useEffect, useCallback } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export interface Player {
  id?: string
  name: string
  jersey_number?: number
  position?: string
  age_group?: string
  team?: string
}

export interface SkillRating {
  skating: number
  shooting: number
  passing: number
  puck_handling: number
  hockey_iq: number
  physicality: number
}

export interface Evaluation {
  id?: string
  player_id: string
  player_name: string
  date: string
  evaluator: string
  evaluation_type: string
  skills: SkillRating
  notes?: string
  strengths?: string
  areas_for_improvement?: string
}

export function useOfflineStorage() {
  const [players, setPlayers] = useState<Player[]>([])
  const [evaluations, setEvaluations] = useState<Evaluation[]>([])
  const [pendingSync, setPendingSync] = useState(0)

  useEffect(() => {
    const storedPlayers = localStorage.getItem('players')
    const storedEvaluations = localStorage.getItem('evaluations')
    
    if (storedPlayers) {
      setPlayers(JSON.parse(storedPlayers))
    }
    if (storedEvaluations) {
      setEvaluations(JSON.parse(storedEvaluations))
    }

    fetchData()
  }, [])

  const fetchData = async () => {
    if (!navigator.onLine) return

    try {
      const [playersRes, evaluationsRes] = await Promise.all([
        fetch(`${API_URL}/api/players`),
        fetch(`${API_URL}/api/evaluations`)
      ])

      if (playersRes.ok && evaluationsRes.ok) {
        const playersData = await playersRes.json()
        const evaluationsData = await evaluationsRes.json()
        
        setPlayers(playersData)
        setEvaluations(evaluationsData)
        
        localStorage.setItem('players', JSON.stringify(playersData))
        localStorage.setItem('evaluations', JSON.stringify(evaluationsData))
      }
    } catch (error) {
      console.error('Failed to fetch data:', error)
    }
  }

  const syncData = useCallback(async () => {
    if (!navigator.onLine) return

    try {
      const response = await fetch(`${API_URL}/api/sync`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ players, evaluations })
      })

      if (response.ok) {
        const data = await response.json()
        setPlayers(data.players)
        setEvaluations(data.evaluations)
        localStorage.setItem('players', JSON.stringify(data.players))
        localStorage.setItem('evaluations', JSON.stringify(data.evaluations))
        setPendingSync(0)
      }
    } catch (error) {
      console.error('Sync failed:', error)
    }
  }, [players, evaluations])

  const addPlayer = useCallback(async (player: Player) => {
    const newPlayer = { ...player, id: crypto.randomUUID() }
    const updatedPlayers = [...players, newPlayer]
    setPlayers(updatedPlayers)
    localStorage.setItem('players', JSON.stringify(updatedPlayers))
    setPendingSync(prev => prev + 1)

    if (navigator.onLine) {
      try {
        await fetch(`${API_URL}/api/players`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(newPlayer)
        })
        setPendingSync(prev => prev - 1)
      } catch (error) {
        console.error('Failed to sync player:', error)
      }
    }

    return newPlayer
  }, [players])

  const addEvaluation = useCallback(async (evaluation: Evaluation) => {
    const newEvaluation = { 
      ...evaluation, 
      id: crypto.randomUUID(),
      date: new Date().toISOString()
    }
    const updatedEvaluations = [...evaluations, newEvaluation]
    setEvaluations(updatedEvaluations)
    localStorage.setItem('evaluations', JSON.stringify(updatedEvaluations))
    setPendingSync(prev => prev + 1)

    if (navigator.onLine) {
      try {
        await fetch(`${API_URL}/api/evaluations`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(newEvaluation)
        })
        setPendingSync(prev => prev - 1)
      } catch (error) {
        console.error('Failed to sync evaluation:', error)
      }
    }

    return newEvaluation
  }, [evaluations])

  return {
    players,
    evaluations,
    addPlayer,
    addEvaluation,
    syncData,
    pendingSync
  }
}
