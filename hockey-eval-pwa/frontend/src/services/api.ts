const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

let authToken: string | null = null

export const setAuthToken = (token: string | null) => {
  authToken = token
}

const getHeaders = () => {
  const headers: HeadersInit = {
    'Content-Type': 'application/json'
  }
  
  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`
  }
  
  return headers
}

export interface Player {
  id: number
  name: string
  jersey_number: number | null
  position: string | null
  age_group: string | null
  team_id: number | null
  coach_id: number
  photo_url: string | null
  created_at: string
}

export interface Team {
  id: number
  name: string
  age_group: string | null
  season: string | null
  coach_id: number
  created_at: string
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
  id: number
  player_id: number
  evaluator_id: number
  evaluator_name: string
  date: string
  evaluation_type: string
  skating: number
  shooting: number
  passing: number
  puck_handling: number
  hockey_iq: number
  physicality: number
  notes: string | null
  strengths: string | null
  areas_for_improvement: string | null
}

export interface FeedbackTemplate {
  id: number
  name: string
  category: string | null
  text: string
  coach_id: number
  created_at: string
  times_used: number
}

export const api = {
  teams: {
    list: async (): Promise<Team[]> => {
      const response = await fetch(`${API_URL}/api/teams`, {
        headers: getHeaders()
      })
      if (!response.ok) throw new Error('Failed to fetch teams')
      return response.json()
    },
    
    create: async (team: { name: string; age_group?: string; season?: string }): Promise<Team> => {
      const response = await fetch(`${API_URL}/api/teams`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(team)
      })
      if (!response.ok) throw new Error('Failed to create team')
      return response.json()
    }
  },
  
  players: {
    list: async (teamId?: number, search?: string): Promise<Player[]> => {
      const params = new URLSearchParams()
      if (teamId) params.append('team_id', teamId.toString())
      if (search) params.append('search', search)
      
      const response = await fetch(`${API_URL}/api/players?${params}`, {
        headers: getHeaders()
      })
      if (!response.ok) throw new Error('Failed to fetch players')
      return response.json()
    },
    
    get: async (id: number): Promise<Player & { evaluations: Evaluation[] }> => {
      const response = await fetch(`${API_URL}/api/players/${id}`, {
        headers: getHeaders()
      })
      if (!response.ok) throw new Error('Failed to fetch player')
      return response.json()
    },
    
    create: async (player: {
      name: string
      jersey_number?: number
      position?: string
      age_group?: string
      team_id?: number
    }): Promise<Player> => {
      const response = await fetch(`${API_URL}/api/players`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(player)
      })
      if (!response.ok) throw new Error('Failed to create player')
      return response.json()
    },
    
    update: async (id: number, player: Partial<Player>): Promise<Player> => {
      const response = await fetch(`${API_URL}/api/players/${id}`, {
        method: 'PUT',
        headers: getHeaders(),
        body: JSON.stringify(player)
      })
      if (!response.ok) throw new Error('Failed to update player')
      return response.json()
    },
    
    delete: async (id: number): Promise<void> => {
      const response = await fetch(`${API_URL}/api/players/${id}`, {
        method: 'DELETE',
        headers: getHeaders()
      })
      if (!response.ok) throw new Error('Failed to delete player')
    },
    
    uploadPhoto: async (id: number, file: File): Promise<{ photo_url: string }> => {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await fetch(`${API_URL}/api/players/${id}/photo`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`
        },
        body: formData
      })
      if (!response.ok) throw new Error('Failed to upload photo')
      return response.json()
    },
    
    downloadPDF: async (id: number): Promise<Blob> => {
      const response = await fetch(`${API_URL}/api/players/${id}/pdf`, {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })
      if (!response.ok) throw new Error('Failed to download PDF')
      return response.blob()
    }
  },
  
  evaluations: {
    list: async (playerId?: number): Promise<Evaluation[]> => {
      const params = new URLSearchParams()
      if (playerId) params.append('player_id', playerId.toString())
      
      const response = await fetch(`${API_URL}/api/evaluations?${params}`, {
        headers: getHeaders()
      })
      if (!response.ok) throw new Error('Failed to fetch evaluations')
      return response.json()
    },
    
    create: async (evaluation: {
      player_id: number
      evaluator_name: string
      evaluation_type: string
      skills: SkillRating
      notes?: string
      strengths?: string
      areas_for_improvement?: string
    }): Promise<Evaluation> => {
      const response = await fetch(`${API_URL}/api/evaluations`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(evaluation)
      })
      if (!response.ok) throw new Error('Failed to create evaluation')
      return response.json()
    },
    
    createBulk: async (evaluations: Array<{
      player_id: number
      evaluator_name: string
      evaluation_type: string
      skills: SkillRating
      notes?: string
      strengths?: string
      areas_for_improvement?: string
    }>): Promise<Evaluation[]> => {
      const response = await fetch(`${API_URL}/api/evaluations/bulk`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(evaluations)
      })
      if (!response.ok) throw new Error('Failed to create bulk evaluations')
      return response.json()
    }
  },
  
  templates: {
    list: async (): Promise<FeedbackTemplate[]> => {
      const response = await fetch(`${API_URL}/api/feedback-templates`, {
        headers: getHeaders()
      })
      if (!response.ok) throw new Error('Failed to fetch templates')
      return response.json()
    },
    
    create: async (template: {
      name: string
      category?: string
      text: string
    }): Promise<FeedbackTemplate> => {
      const response = await fetch(`${API_URL}/api/feedback-templates`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(template)
      })
      if (!response.ok) throw new Error('Failed to create template')
      return response.json()
    },
    
    delete: async (id: number): Promise<void> => {
      const response = await fetch(`${API_URL}/api/feedback-templates/${id}`, {
        method: 'DELETE',
        headers: getHeaders()
      })
      if (!response.ok) throw new Error('Failed to delete template')
    }
  }
}
