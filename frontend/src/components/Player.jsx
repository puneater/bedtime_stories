import { useEffect, useMemo, useRef, useState } from 'react'
import { Card, Stack, Typography, IconButton, Button } from '@mui/material'
import PlayArrowIcon from '@mui/icons-material/PlayArrow'
import PauseIcon from '@mui/icons-material/Pause'
import ReplayIcon from '@mui/icons-material/Replay'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import EditNoteIcon from '@mui/icons-material/EditNote'
import { useSpeech } from '../hooks/useSpeech'   // <-- new hook below

// Split story into manageable utterances
function chunkText(text, maxLen = 220) {
  const sentences = (text || '').split(/(?<=[.!?])\s+/)
  const chunks = []
  let buf = ''
  for (const s of sentences) {
    if ((buf + ' ' + s).trim().length > maxLen) {
      if (buf) chunks.push(buf.trim())
      buf = s
    } else {
      buf = (buf + ' ' + s).trim()
    }
  }
  if (buf) chunks.push(buf.trim())
  return chunks
}

export default function Player({ story, onGenerate, onEdit }) {
  const { supported, voices, speak, pause, resume, cancel, speaking, paused } = useSpeech()
  const [isPlaying, setIsPlaying] = useState(false)
  const [index, setIndex] = useState(0)
  const chunks = useMemo(() => chunkText(story, 220), [story])
  const playingRef = useRef(false)

  // Stop speech on unmount or when story changes
  useEffect(() => () => { cancel(); setIsPlaying(false); setIndex(0) }, [cancel, story])

  // Autoplay current chunk when toggled on
  useEffect(() => {
    if (!supported || !isPlaying || !chunks.length) return
    const text = chunks[index]

    // pick a friendly English voice if available
    const preferred =
      voices.find(v => /english/i.test(v.lang) && /female|samantha|zira|google uk english female/i.test(v.name)) ||
      voices[0] || null

    playingRef.current = true
    speak({
      text,
      voice: preferred || undefined,
      rate: 1,
      pitch: 1,
      onEnd: () => {
        if (!playingRef.current) return
        if (index < chunks.length - 1) {
          setIndex(i => i + 1)
        } else {
          setIsPlaying(false)
          setIndex(0)
        }
      }
    })
  }, [supported, isPlaying, index, chunks, voices, speak])

  const handlePlay = () => {
    if (!story || !supported) return
    if (paused) {
      resume()
      setIsPlaying(true)
      return
    }
    setIsPlaying(true)
  }

  const handlePause = () => {
    pause()
    setIsPlaying(false)
  }

  const handleReplay = () => {
    playingRef.current = false
    cancel()
    setIndex(0)
    setIsPlaying(true)
  }

  return (
    <Card sx={{ p: 3, textAlign: 'center' }}>
      <Stack spacing={2} alignItems="center">
        <Typography variant="h5">Story Player</Typography>

        <div className="equalizer" aria-hidden={!isPlaying} style={{ opacity: isPlaying ? 1 : 0.25 }}>
          <div className="bar"/><div className="bar"/><div className="bar"/><div className="bar"/><div className="bar"/>
        </div>

        {!supported && (
          <Typography variant="body2" color="warning.main">
            Your browser doesn’t support speech playback. Try Chrome, Edge, or Safari.
          </Typography>
        )}

        <Stack direction="row" spacing={2} justifyContent="center" alignItems="center">
          <IconButton color="primary" size="large" onClick={handlePlay} aria-label="play" disabled={!supported}>
            <PlayArrowIcon fontSize="inherit" />
          </IconButton>
          <IconButton color="primary" size="large" onClick={handlePause} aria-label="pause" disabled={!supported}>
            <PauseIcon fontSize="inherit" />
          </IconButton>
          <IconButton color="primary" size="large" onClick={handleReplay} aria-label="replay" disabled={!supported}>
            <ReplayIcon fontSize="inherit" />
          </IconButton>
        </Stack>

        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mt: 2 }}>
          <Button startIcon={<AutoAwesomeIcon />} variant="contained" onClick={onGenerate}>Generate</Button>
          <Button startIcon={<EditNoteIcon />} variant="outlined" onClick={onEdit}>Edit</Button>
        </Stack>

        <Typography variant="caption" sx={{ opacity: 0.7 }}>
          Voice playback powered by the Web Speech API.
        </Typography>
      </Stack>
    </Card>
  )
}
