import { useState } from 'react'
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, TextField, Stack, Typography } from '@mui/material'

export default function EditModal({ open, onClose, onSubmit }) {
  const [text, setText] = useState('')
  const limit = 300
  const count = text.length
  const remaining = limit - count

  const handleSubmit = () => {
    onSubmit(text)
    setText('')
  }

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>Edit the story</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 1 }}>
          <TextField
            autoFocus
            placeholder="e.g., Add a friendly dragon, make it a bit sillier, shorten the ending..."
            multiline
            minRows={3}
            value={text}
            onChange={(e) => {
              const v = e.target.value
              if (v.length <= limit) setText(v)
            }}
          />
          <Typography variant="body2" sx={{ textAlign: 'right', opacity: 0.8 }}>{remaining} characters left</Typography>
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button variant="contained" onClick={handleSubmit} disabled={count === 0}>Apply</Button>
      </DialogActions>
    </Dialog>
  )
}