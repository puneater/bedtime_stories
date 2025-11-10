import { Card, Button, Stack, Typography } from '@mui/material'
import ChildCareIcon from '@mui/icons-material/ChildCare'

export default function AgeGate({ onPick }) {
  return (
    <Card sx={{ p: 4, textAlign: 'center' }}>
      <Stack spacing={2} alignItems="center">
        <ChildCareIcon className="big-icon" fontSize="large" />
        <Typography variant="h4">How old is the listener?</Typography>
        <Typography variant="body1" sx={{ opacity: 0.8 }}>Pick an age bracket to tune the story.</Typography>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} justifyContent="center" sx={{ mt: 2 }}>
          <Button variant="contained" size="large" onClick={() => onPick('young')}>5–6</Button>
          <Button variant="contained" size="large" onClick={() => onPick('middle')}>7–8</Button>
          <Button variant="contained" size="large" onClick={() => onPick('older')}>9–10</Button>
        </Stack>
      </Stack>
    </Card>
  )
}