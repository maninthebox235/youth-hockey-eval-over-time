import { useState } from 'react'
import { Save } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Slider } from '@/components/ui/slider'
import { Player, Evaluation } from '../hooks/useOfflineStorage'

interface EvaluationFormProps {
  players: Player[]
  addEvaluation: (evaluation: any) => Promise<Evaluation>
}

export default function EvaluationForm({ players, addEvaluation }: EvaluationFormProps) {
  const [selectedPlayer, setSelectedPlayer] = useState<number | null>(null)
  const [evaluator, setEvaluator] = useState('')
  const [evaluationType, setEvaluationType] = useState('practice')
  const [skills, setSkills] = useState({
    skating: 5,
    shooting: 5,
    passing: 5,
    puck_handling: 5,
    hockey_iq: 5,
    physicality: 5
  })
  const [notes, setNotes] = useState('')
  const [strengths, setStrengths] = useState('')
  const [improvements, setImprovements] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedPlayer) return
    
    await addEvaluation({
      player_id: selectedPlayer,
      evaluator_name: evaluator,
      evaluation_type: evaluationType,
      skills,
      notes: notes || undefined,
      strengths: strengths || undefined,
      areas_for_improvement: improvements || undefined
    })
    
    setSelectedPlayer(null)
    setEvaluator('')
    setSkills({
      skating: 5,
      shooting: 5,
      passing: 5,
      puck_handling: 5,
      hockey_iq: 5,
      physicality: 5
    })
    setNotes('')
    setStrengths('')
    setImprovements('')
  }

  const skillLabels = {
    skating: 'Skating',
    shooting: 'Shooting',
    passing: 'Passing',
    puck_handling: 'Puck Handling',
    hockey_iq: 'Hockey IQ',
    physicality: 'Physicality'
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="player">Player *</Label>
          <Select 
            value={selectedPlayer?.toString() || ''} 
            onValueChange={(value) => setSelectedPlayer(parseInt(value))} 
            required
          >
            <SelectTrigger>
              <SelectValue placeholder="Select player" />
            </SelectTrigger>
            <SelectContent>
              {players.map((player) => (
                <SelectItem key={player.id} value={player.id.toString()}>
                  {player.name} {player.jersey_number && `(#${player.jersey_number})`}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div>
          <Label htmlFor="evaluator">Evaluator Name *</Label>
          <Input
            id="evaluator"
            value={evaluator}
            onChange={(e) => setEvaluator(e.target.value)}
            placeholder="Coach name"
            required
          />
        </div>
      </div>

      <div>
        <Label htmlFor="type">Evaluation Type</Label>
        <Select value={evaluationType} onValueChange={setEvaluationType}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="practice">Practice</SelectItem>
            <SelectItem value="game">Game</SelectItem>
            <SelectItem value="tryout">Tryout</SelectItem>
            <SelectItem value="scrimmage">Scrimmage</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-4">
        <h3 className="font-semibold text-lg">Skill Ratings (1-10)</h3>
        {Object.entries(skills).map(([key, value]) => (
          <div key={key} className="space-y-2">
            <div className="flex justify-between">
              <Label>{skillLabels[key as keyof typeof skillLabels]}</Label>
              <span className="text-sm font-semibold text-blue-600">{value}</span>
            </div>
            <Slider
              value={[value]}
              onValueChange={([newValue]) => setSkills({ ...skills, [key]: newValue })}
              min={1}
              max={10}
              step={1}
              className="w-full"
            />
          </div>
        ))}
      </div>

      <div>
        <Label htmlFor="strengths">Key Strengths</Label>
        <Textarea
          id="strengths"
          value={strengths}
          onChange={(e) => setStrengths(e.target.value)}
          placeholder="What did they do well?"
          rows={2}
        />
      </div>

      <div>
        <Label htmlFor="improvements">Areas for Improvement</Label>
        <Textarea
          id="improvements"
          value={improvements}
          onChange={(e) => setImprovements(e.target.value)}
          placeholder="What should they work on?"
          rows={2}
        />
      </div>

      <div>
        <Label htmlFor="notes">Additional Notes</Label>
        <Textarea
          id="notes"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Any other observations..."
          rows={3}
        />
      </div>

      <Button type="submit" className="w-full" size="lg">
        <Save className="w-4 h-4 mr-2" />
        Save Evaluation
      </Button>
    </form>
  )
}
