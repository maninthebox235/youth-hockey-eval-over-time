import { useState, useEffect, useCallback } from 'react'
import { api, Player, Evaluation, SkillRating } from '../services/api'

export { Player, Evaluation, SkillRating }

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
      const [playersData, evaluationsData] = await Promise.all([
        api.players.list(),
        api.evaluations.list()
      ])
      
      setPlayers(playersData)
      setEvaluations(evaluationsData)
      
      localStorage.setItem('players', JSON.stringify(playersData))
      localStorage.setItem('evaluations', JSON.stringify(evaluationsData))
    } catch (error) {
      console.error('Failed to fetch data:', error)
    }
  }

  const syncData = useCallback(async () => {
    if (!navigator.onLine) return

    try {
      await fetchData()
      setPendingSync(0)
    } catch (error) {
      console.error('Sync failed:', error)
    }
  }, [])

  const addPlayer = useCallback(async (player: Omit<Player, 'id' | 'coach_id' | 'created_at'>) => {
    if (navigator.onLine) {
      try {
        const newPlayer = await api.players.create(player)
        const updatedPlayers = [...players, newPlayer]
        setPlayers(updatedPlayers)
        localStorage.setItem('players', JSON.stringify(updatedPlayers))
        return newPlayer
      } catch (error) {
        console.error('Failed to create player:', error)
        throw error
      }
    } else {
      const tempPlayer: Player = {
        ...player,
        id: Date.now(),
        coach_id: 0,
        photo_url: null,
        created_at: new Date().toISOString()
      }
      const updatedPlayers = [...players, tempPlayer]
      setPlayers(updatedPlayers)
      localStorage.setItem('players', JSON.stringify(updatedPlayers))
      setPendingSync(prev => prev + 1)
      return tempPlayer
    }
  }, [players])

  const addEvaluation = useCallback(async (evaluation: {
    player_id: number
    evaluator_name: string
    evaluation_type: string
    skills: SkillRating
    notes?: string
    strengths?: string
    areas_for_improvement?: string
  }) => {
    if (navigator.onLine) {
      try {
        const newEvaluation = await api.evaluations.create(evaluation)
        const updatedEvaluations = [...evaluations, newEvaluation]
        setEvaluations(updatedEvaluations)
        localStorage.setItem('evaluations', JSON.stringify(updatedEvaluations))
        return newEvaluation
      } catch (error) {
        console.error('Failed to create evaluation:', error)
        throw error
      }
    } else {
      const tempEvaluation: Evaluation = {
        ...evaluation,
        id: Date.now(),
        evaluator_id: 0,
        date: new Date().toISOString()
      }
      const updatedEvaluations = [...evaluations, tempEvaluation]
      setEvaluations(updatedEvaluations)
      localStorage.setItem('evaluations', JSON.stringify(updatedEvaluations))
      setPendingSync(prev => prev + 1)
      return tempEvaluation
    }
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
