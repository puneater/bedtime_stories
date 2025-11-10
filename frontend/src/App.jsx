import { useEffect, useState } from 'react'
import { Container, Row, Col } from 'react-bootstrap'
import { Box, Stack, Snackbar, Alert, Dialog, DialogTitle, DialogContent, DialogActions, Button, TextField } from '@mui/material'
import axios from 'axios'
import AgeGate from './components/AgeGate'
import CategoryGrid from './components/CategoryGrid'
import Player from './components/Player'
import EditModal from './components/EditModal'

export default function App() {
  const [ageBracket, setAgeBracket] = useState(null)
  const [categories, setCategories] = useState([])
  const [story, setStory] = useState('')
  const [categoryPicked, setCategoryPicked] = useState(null)
  const [promptOpen, setPromptOpen] = useState(false)
  const [promptText, setPromptText] = useState('')
  const [toast, setToast] = useState(null)
  const [editOpen, setEditOpen] = useState(false)

  useEffect(() => {
    axios.get('/api/categories').then(r => setCategories(r.data.categories)).catch(() => setCategories([]))
  }, [])

  const startGenerate = async ({ category = null, prompt = '' } = {}) => {
    try {
      const { data } = await axios.post('/api/generate', {
        ageBracket: ageBracket || 'middle',
        category,
        prompt
      })
      setStory(data.story)
      setCategoryPicked(data.category)
      setToast({ type: 'success', msg: `Story ready: ${data.category}` })
    } catch (e) {
      setToast({ type: 'error', msg: 'Failed to generate story' })
    }
  }

  const applyEdit = async (feedback) => {
    try {
      const { data } = await axios.post('/api/revise', { story, feedback })
      setStory(data.story)
      setToast({ type: 'success', msg: 'Story updated' })
    } catch (e) {
      setToast({ type: 'error', msg: 'Failed to update story' })
    } finally {
      setEditOpen(false)
    }
  }

  return (
    <Container className="container-max" style={{ padding: '32px 16px' }}>
      <Row>
        <Col>
          {!ageBracket ? (
            <AgeGate onPick={setAgeBracket} />
          ) : (
            <Stack spacing={3}>
              <CategoryGrid
                categories={categories}
                onPickCategory={(c) => startGenerate({ category: c })}
                onSurprise={() => startGenerate()}
                onPrompt={() => setPromptOpen(true)}
              />

              {/* Player – speech only, no text shown */}
              <Player
                story={story}
                onGenerate={() => startGenerate({ category: categoryPicked })}
                onEdit={() => setEditOpen(true)}
              />
            </Stack>
          )}
        </Col>
      </Row>

      {/* Prompt dialog for "Tell me a little..." */}
      <Dialog open={promptOpen} onClose={() => setPromptOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>Tell me a little and I'll create it</DialogTitle>
        <DialogContent>
          <TextField fullWidth autoFocus placeholder="e.g., A brave kid astronaut and a sleepy alien" value={promptText} onChange={(e) => setPromptText(e.target.value)} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPromptOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => { setPromptOpen(false); startGenerate({ prompt: promptText })}}>Create</Button>
        </DialogActions>
      </Dialog>

      {/* Edit modal with 300 char limit */}
      <EditModal open={editOpen} onClose={() => setEditOpen(false)} onSubmit={applyEdit} />

      <Snackbar open={!!toast} autoHideDuration={3000} onClose={() => setToast(null)}>
        {toast && <Alert severity={toast.type}>{toast.msg}</Alert>}
      </Snackbar>
    </Container>
  )
}