import { useCallback, useEffect, useRef, useState } from 'react'

// Robust, SSR-safe Web Speech synthesis hook
export function useSpeech() {
  const synth = typeof window !== 'undefined' ? window.speechSynthesis : null
  const [voices, setVoices] = useState([])
  const [paused, setPaused] = useState(false)
  const speakingRef = useRef(false)

  // Load voices; Chrome often populates asynchronously
  useEffect(() => {
    if (!synth) return
    const update = () => {
      const list = (synth.getVoices?.() || []).filter(Boolean) // drop undefined entries
      setVoices(list)
    }
    update()
    synth.onvoiceschanged = update  // wait for voices to load
    return () => { synth.onvoiceschanged = null }
  }, [synth])

  const speak = useCallback(({ text, voice, rate = 1, pitch = 1, onEnd }) => {
    if (!synth || !text) return
    const u = new SpeechSynthesisUtterance(text)
    if (voice) u.voice = voice
    u.rate = rate
    u.pitch = pitch
    u.onend = () => {
      speakingRef.current = false
      setPaused(false)
      onEnd && onEnd()
    }
    speakingRef.current = true
    setPaused(false)
    synth.speak(u)
  }, [synth])

  const pause = useCallback(() => { if (synth?.speaking && !synth.paused) { synth.pause(); setPaused(true) } }, [synth])
  const resume = useCallback(() => { if (synth?.paused) { synth.resume(); setPaused(false) } }, [synth])
  const cancel = useCallback(() => { if (synth) { synth.cancel(); speakingRef.current = false; setPaused(false) } }, [synth])

  return {
    supported: !!synth,
    voices,
    speak, pause, resume, cancel,
    speaking: speakingRef.current,
    paused
  }
}
