import { useState } from 'react'
import { Plus, User } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Player } from '../hooks/useOfflineStorage'

interface PlayerListProps {
  players: Player[]
  addPlayer: (player: Player) => Promise<Player>
}

export default function PlayerList({ players, addPlayer }: PlayerListProps) {
  const [open, setOpen] = useState(false)
  const [newPlayer, setNewPlayer] = useState({
    name: '',
    jersey_number: '',
    position: '',
    age_group: '',
    team: ''
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    await addPlayer({
      name: newPlayer.name,
      jersey_number: newPlayer.jersey_number ? parseInt(newPlayer.jersey_number) : undefined,
      position: newPlayer.position || undefined,
      age_group: newPlayer.age_group || undefined,
      team: newPlayer.team || undefined
    })
    setOpen(false)
    setNewPlayer({ name: '', jersey_number: '', position: '', age_group: '', team: '' })
  }

  return (
    <div className="space-y-4">
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogTrigger asChild>
          <Button className="w-full">
            <Plus className="w-4 h-4 mr-2" />
            Add Player
          </Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add New Player</DialogTitle>
            <DialogDescription>
              Add a player to your roster. This will be saved locally.
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="name">Player Name *</Label>
              <Input
                id="name"
                value={newPlayer.name}
                onChange={(e) => setNewPlayer({ ...newPlayer, name: e.target.value })}
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="jersey">Jersey #</Label>
                <Input
                  id="jersey"
                  type="number"
                  value={newPlayer.jersey_number}
                  onChange={(e) => setNewPlayer({ ...newPlayer, jersey_number: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="position">Position</Label>
                <Input
                  id="position"
                  value={newPlayer.position}
                  onChange={(e) => setNewPlayer({ ...newPlayer, position: e.target.value })}
                  placeholder="Forward, Defense, Goalie"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="age_group">Age Group</Label>
                <Input
                  id="age_group"
                  value={newPlayer.age_group}
                  onChange={(e) => setNewPlayer({ ...newPlayer, age_group: e.target.value })}
                  placeholder="U10, U12, U14..."
                />
              </div>
              <div>
                <Label htmlFor="team">Team</Label>
                <Input
                  id="team"
                  value={newPlayer.team}
                  onChange={(e) => setNewPlayer({ ...newPlayer, team: e.target.value })}
                />
              </div>
            </div>
            <Button type="submit" className="w-full">Add Player</Button>
          </form>
        </DialogContent>
      </Dialog>

      <div className="space-y-2">
        {players.length === 0 ? (
          <div className="text-center py-8 text-slate-500">
            <User className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>No players yet. Add your first player to get started.</p>
          </div>
        ) : (
          players.map((player) => (
            <div key={player.id} className="flex items-center justify-between p-3 bg-white rounded-lg border">
              <div>
                <div className="font-semibold">{player.name}</div>
                <div className="text-sm text-slate-500">
                  {player.jersey_number && `#${player.jersey_number}`}
                  {player.position && ` • ${player.position}`}
                  {player.age_group && ` • ${player.age_group}`}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
