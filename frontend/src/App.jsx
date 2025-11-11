import { useEffect, useState } from 'react'
import { Container, Row, Col } from 'react-bootstrap'
import { Stack, Snackbar, Alert, Dialog, DialogTitle, DialogContent, DialogActions, Button, TextField } from '@mui/material'
import axios from 'axios'
import AgeGate from './components/AgeGate'
import CategoryGrid from './components/CategoryGrid'
import Player from './components/Player'
import EditModal from './components/EditModal'
import Header from './components/Header'   // ✅ re-add the header

// 🔸 read backend base from env (set in .env / .env.production)
const API_BASE = import.meta.env.VITE_API_TARGET
const api = axios.create({
  baseURL: API_BASE,         // e.g. https://your-backend.vercel.app
  withCredentials: false
})

export default function App() {
  const [ageBracket, setAgeBracket] = useState(null)
  const [categories, setCategories] = useState([])
  const [story, setStory] = useState('')
  const [audioUrl, setAudioUrl] = useState(null)
  const [_categoryPicked, setCategoryPicked] = useState(null)
  const [promptOpen, setPromptOpen] = useState(false)
  const [promptText, setPromptText] = useState('')
  const [toast, setToast] = useState(null)
  const [editOpen, setEditOpen] = useState(false)
  const [view, setView] = useState('create') // 'create' | 'play'
  const [isGenerating, setIsGenerating] = useState(false)
  const [controlsDisabled, setControlsDisabled] = useState(false)

  useEffect(() => {
    api.get('/api/categories').then(r => setCategories(r.data.categories)).catch(() => setCategories([]))
  }, [])

  const startGenerate = async ({ category = null, prompt = '' } = {}) => {
    try {
      setIsGenerating(true)
      setControlsDisabled(true)
      const { data } = await api.post('/api/generate', {
        ageBracket: ageBracket || 'middle',
        category,
        prompt
      })
      setStory(data.story)
      setCategoryPicked(data.category)
      setAudioUrl(data.audioUrl || null)
      setToast({ type: 'success', msg: `Story ready: ${data.category}` })
      setView('play')
    } catch (e) {
      setToast({ type: 'error', msg: e?.response?.data?.error || 'Failed to generate story' })
    } finally {
      setIsGenerating(false)
      setControlsDisabled(false)
    }
  }

  const applyEdit = async (feedback) => {
    try {
      setControlsDisabled(true)
      const { data } = await api.post('/api/revise', { story, feedback })
      setStory(data.story)
      setAudioUrl(data.audioUrl || null)
      setToast({ type: 'success', msg: 'Story updated' })
    } catch (e) {
      setToast({ type: 'error', msg: e?.response?.data?.error || 'Failed to update story' })
    } finally {
      setEditOpen(false)
      setControlsDisabled(false)
    }
  }

  const switchToPlay = () => setView('play')
  const switchToCreate = () => setView('create')

  const SwitchButton = () => (
    <div className="sticky-switch">
      <Button
        variant="contained"
        size="large"
        disabled={isGenerating || (!audioUrl && view === 'create')}
        onClick={() => {
          if (isGenerating) return
          if (view === 'create') switchToPlay(); else switchToCreate()
        }}
        sx={{ width: '100%', maxWidth: 980, backgroundColor: isGenerating ? '#9c8c3b' : undefined }}
      >
        {isGenerating ? 'Generating…' : (view === 'create' ? 'Play Story' : 'Create Story')}
      </Button>
    </div>
  )

  return (
    <>
      <Header /> {/* ✅ persistent, kid-friendly header */}

      <Container className="container-max" style={{ padding: '32px 16px' }}>
        <Row>
          <Col>
            {!ageBracket ? (
              <AgeGate onPick={setAgeBracket} />
            ) : (
              <Stack spacing={3}>
                {view === 'create' && (
                  <CategoryGrid
                    className="panel story-panel enter-top"
                    categories={categories}
                    onPickCategory={(c) => startGenerate({ category: c })}
                    onSurprise={() => startGenerate()}
                    onPrompt={() => setPromptOpen(true)}
                  />
                )}

                {view === 'play' && (
                  <Player
                    audioUrl={audioUrl}
                    onEdit={() => setEditOpen(true)}
                    controlsDisabled={controlsDisabled}
                  />
                )}

                <SwitchButton />
              </Stack>
            )}
          </Col>
        </Row>

        <Dialog open={promptOpen} onClose={() => setPromptOpen(false)} fullWidth maxWidth="sm">
          <DialogTitle>Tell me a little and I'll create it</DialogTitle>
          <DialogContent>
            <TextField
              fullWidth
              autoFocus
              placeholder="e.g., A brave kid astronaut and a sleepy alien"
              value={promptText}
              onChange={(e) => setPromptText(e.target.value)}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setPromptOpen(false)}>Cancel</Button>
            <Button variant="contained" onClick={() => { setPromptOpen(false); startGenerate({ prompt: promptText }) }}>Create</Button>
          </DialogActions>
        </Dialog>

        <EditModal open={editOpen} onClose={() => setEditOpen(false)} onSubmit={applyEdit} />

        <Snackbar open={!!toast} autoHideDuration={3000} onClose={() => setToast(null)}>
          {toast && <Alert severity={toast.type}>{toast.msg}</Alert>}
        </Snackbar>
      </Container>
    </>
  )
}
