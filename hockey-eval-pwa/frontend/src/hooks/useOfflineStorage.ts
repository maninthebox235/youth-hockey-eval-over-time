import { useState, useEffect, useCallback } from 'react'
import { api, Player, Evaluation, SkillRating } from '../services/api'

export type { Player, Evaluation, SkillRating }

export function useOfflineStorage() {
  const [players, setPlayers] = useState<Player[]>([])
  const [evaluations, setEvaluations] = useState<Evaluation[]>([])
  const [pendingSync, setPendingSync] = useState(0)
  const [isSyncing, setIsSyncing] = useState(false)

  const fetchData = useCallback(async () => {
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
  }, [])

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
  }, [fetchData])

  const syncData = useCallback(async () => {
    if (!navigator.onLine || isSyncing) return

    setIsSyncing(true)
    try {
      await fetchData()
      setPendingSync(0)
    } catch (error) {
      console.error('Sync failed:', error)
    } finally {
      setIsSyncing(false)
    }
  }, [fetchData, isSyncing])

  const addPlayer = useCallback(async (player: Omit<Player, 'id' | 'coach_id' | 'created_at'>) => {
    if (navigator.onLine) {
      try {
        const newPlayer = await api.players.create({
          name: player.name,
          jersey_number: player.jersey_number ?? undefined,
          position: player.position ?? undefined,
          age_group: player.age_group ?? undefined,
          team_id: player.team_id ?? undefined
        })
        const updatedPlayers = [...players, newPlayer]
        setPlayers(updatedPlayers)
        localStorage.setItem('players', JSON.stringify(updatedPlayers))
        return newPlayer
      } catch (error) {
        console.error('Failed to create player:', error)
        throw error
      }
    } else {
      // Use negative timestamp for offline IDs to avoid collision with server IDs
      const tempPlayer: Player = {
        ...player,
        id: -Date.now(),
        coach_id: -1,
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
      // Use negative timestamp for offline IDs
      const tempEvaluation: Evaluation = {
        id: -Date.now(),
        player_id: evaluation.player_id,
        evaluator_id: -1,
        evaluator_name: evaluation.evaluator_name,
        date: new Date().toISOString(),
        evaluation_type: evaluation.evaluation_type,
        skating: evaluation.skills.skating,
        shooting: evaluation.skills.shooting,
        passing: evaluation.skills.passing,
        puck_handling: evaluation.skills.puck_handling,
        hockey_iq: evaluation.skills.hockey_iq,
        physicality: evaluation.skills.physicality,
        notes: evaluation.notes ?? null,
        strengths: evaluation.strengths ?? null,
        areas_for_improvement: evaluation.areas_for_improvement ?? null
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
    pendingSync,
    isSyncing
  }
}
