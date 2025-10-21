import { ClipboardList, TrendingUp } from 'lucide-react'
import { Evaluation } from '../hooks/useOfflineStorage'

interface EvaluationHistoryProps {
  evaluations: Evaluation[]
}

export default function EvaluationHistory({ evaluations }: EvaluationHistoryProps) {
  const sortedEvaluations = [...evaluations].sort((a, b) => 
    new Date(b.date).getTime() - new Date(a.date).getTime()
  )

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getAverageRating = (evaluation: Evaluation) => {
    const values = [
      evaluation.skating,
      evaluation.shooting,
      evaluation.passing,
      evaluation.puck_handling,
      evaluation.hockey_iq,
      evaluation.physicality
    ].filter(v => v != null && !isNaN(v))

    if (values.length === 0) return '0.0'
    return (values.reduce((a, b) => a + b, 0) / values.length).toFixed(1)
  }

  return (
    <div className="space-y-4">
      {sortedEvaluations.length === 0 ? (
        <div className="text-center py-8 text-slate-500">
          <ClipboardList className="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p>No evaluations yet. Start evaluating players to see history here.</p>
        </div>
      ) : (
        sortedEvaluations.map((evaluation) => (
          <div key={evaluation.id} className="bg-white rounded-lg border p-4 space-y-3">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-semibold text-lg">Player #{evaluation.player_id}</h3>
                <p className="text-sm text-slate-500">
                  {formatDate(evaluation.date)} • {evaluation.evaluation_type}
                </p>
                <p className="text-sm text-slate-600">Evaluated by {evaluation.evaluator_name}</p>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-blue-600">
                  {getAverageRating(evaluation)}
                </div>
                <div className="text-xs text-slate-500">avg rating</div>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-2 text-sm">
              <div className="bg-slate-50 p-2 rounded">
                <div className="text-slate-600">Skating</div>
                <div className="font-semibold">{evaluation.skating}/10</div>
              </div>
              <div className="bg-slate-50 p-2 rounded">
                <div className="text-slate-600">Shooting</div>
                <div className="font-semibold">{evaluation.shooting}/10</div>
              </div>
              <div className="bg-slate-50 p-2 rounded">
                <div className="text-slate-600">Passing</div>
                <div className="font-semibold">{evaluation.passing}/10</div>
              </div>
              <div className="bg-slate-50 p-2 rounded">
                <div className="text-slate-600">Puck Handling</div>
                <div className="font-semibold">{evaluation.puck_handling}/10</div>
              </div>
              <div className="bg-slate-50 p-2 rounded">
                <div className="text-slate-600">Hockey IQ</div>
                <div className="font-semibold">{evaluation.hockey_iq}/10</div>
              </div>
              <div className="bg-slate-50 p-2 rounded">
                <div className="text-slate-600">Physicality</div>
                <div className="font-semibold">{evaluation.physicality}/10</div>
              </div>
            </div>

            {evaluation.strengths && (
              <div className="bg-green-50 p-3 rounded">
                <div className="text-sm font-semibold text-green-800 mb-1">Strengths</div>
                <div className="text-sm text-green-700">{evaluation.strengths}</div>
              </div>
            )}

            {evaluation.areas_for_improvement && (
              <div className="bg-amber-50 p-3 rounded">
                <div className="text-sm font-semibold text-amber-800 mb-1 flex items-center gap-1">
                  <TrendingUp className="w-4 h-4" />
                  Areas for Improvement
                </div>
                <div className="text-sm text-amber-700">{evaluation.areas_for_improvement}</div>
              </div>
            )}

            {evaluation.notes && (
              <div className="bg-slate-50 p-3 rounded">
                <div className="text-sm font-semibold text-slate-700 mb-1">Notes</div>
                <div className="text-sm text-slate-600">{evaluation.notes}</div>
              </div>
            )}
          </div>
        ))
      )}
    </div>
  )
}
