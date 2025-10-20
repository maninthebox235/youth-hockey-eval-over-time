import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Evaluation } from '../hooks/useOfflineStorage'

interface ComparisonChartsProps {
  evaluations: Evaluation[]
  playerName: string
}

export default function ComparisonCharts({ evaluations, playerName }: ComparisonChartsProps) {
  const sortedEvaluations = [...evaluations].sort((a, b) => 
    new Date(a.date).getTime() - new Date(b.date).getTime()
  )

  const progressData = sortedEvaluations.map((evaluation) => ({
    date: new Date(evaluation.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    skating: evaluation.skating,
    shooting: evaluation.shooting,
    passing: evaluation.passing,
    puck_handling: evaluation.puck_handling,
    hockey_iq: evaluation.hockey_iq,
    physicality: evaluation.physicality,
    average: (evaluation.skating + evaluation.shooting + evaluation.passing + evaluation.puck_handling + evaluation.hockey_iq + evaluation.physicality) / 6
  }))

  const latestEval = sortedEvaluations[sortedEvaluations.length - 1]
  const radarData = latestEval ? [
    { skill: 'Skating', value: latestEval.skating },
    { skill: 'Shooting', value: latestEval.shooting },
    { skill: 'Passing', value: latestEval.passing },
    { skill: 'Puck Handling', value: latestEval.puck_handling },
    { skill: 'Hockey IQ', value: latestEval.hockey_iq },
    { skill: 'Physicality', value: latestEval.physicality }
  ] : []

  if (evaluations.length === 0) {
    return (
      <div className="text-center py-8 text-slate-500">
        <p>No evaluations available for comparison charts.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Progress Over Time</CardTitle>
          <CardDescription>
            Track {playerName}'s skill development across evaluations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={progressData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis domain={[0, 10]} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="skating" stroke="#3b82f6" strokeWidth={2} />
              <Line type="monotone" dataKey="shooting" stroke="#ef4444" strokeWidth={2} />
              <Line type="monotone" dataKey="passing" stroke="#10b981" strokeWidth={2} />
              <Line type="monotone" dataKey="puck_handling" stroke="#f59e0b" strokeWidth={2} />
              <Line type="monotone" dataKey="hockey_iq" stroke="#8b5cf6" strokeWidth={2} />
              <Line type="monotone" dataKey="physicality" stroke="#ec4899" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Overall Average Progress</CardTitle>
          <CardDescription>
            Average rating across all skills over time
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={progressData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis domain={[0, 10]} />
              <Tooltip />
              <Line type="monotone" dataKey="average" stroke="#3b82f6" strokeWidth={3} />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {latestEval && (
        <Card>
          <CardHeader>
            <CardTitle>Current Skill Profile</CardTitle>
            <CardDescription>
              Latest evaluation snapshot
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="skill" />
                <PolarRadiusAxis domain={[0, 10]} />
                <Radar name={playerName} dataKey="value" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
