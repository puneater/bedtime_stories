import { Card, Button, Grid, Stack, Typography } from '@mui/material'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import CategoryIcon from '@mui/icons-material/Category'
import PetsIcon from '@mui/icons-material/Pets'
import ScienceIcon from '@mui/icons-material/Science'
import EmojiEmotionsIcon from '@mui/icons-material/EmojiEmotions'
import FamilyRestroomIcon from '@mui/icons-material/FamilyRestroom'
import TravelExploreIcon from '@mui/icons-material/TravelExplore'
import NightlightIcon from '@mui/icons-material/Nightlight'
import QuizIcon from '@mui/icons-material/Quiz'

const ICONS = {
  'Magic Adventure': <AutoAwesomeIcon className="big-icon" />,
  'Epic Quest': <TravelExploreIcon className="big-icon" />,
  'Mystery': <CategoryIcon className="big-icon" />,
  'Funny': <EmojiEmotionsIcon className="big-icon" />,
  'Friends and Family': <FamilyRestroomIcon className="big-icon" />,
  'Furry Friends': <PetsIcon className="big-icon" />,
  'Space Adventure': <ScienceIcon className="big-icon" />,
  'Boo!': <NightlightIcon className="big-icon" />
}

export default function CategoryGrid({ categories, onPickCategory, onSurprise, onPrompt, className }) {
  const merged = `panel story-panel ${className || ''}`.trim()
  return (
    <Card sx={{ p: 4 }} className={merged}>
      <Stack spacing={3} className="stack-fill">
        <Typography variant="h4" textAlign="center">What story do you want to hear?</Typography>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} justifyContent="center">
          <Button variant="contained" size="large" startIcon={<AutoAwesomeIcon />} onClick={onSurprise}>Surprise me</Button>
          <Button variant="outlined" size="large" startIcon={<QuizIcon />} onClick={onPrompt}>Tell me a little and I'll create it</Button>
        </Stack>
        <Grid container spacing={2}>
          {categories.map((c) => (
            <Grid item xs={6} sm={4} md={3} key={c}>
              <Button
                fullWidth
                variant="contained"
                color="secondary"
                size="large"
                onClick={() => onPickCategory(c)}
                startIcon={ICONS[c] ?? <CategoryIcon className="big-icon" />}
              >
                {c}
              </Button>
            </Grid>
          ))}
        </Grid>
      </Stack>
    </Card>
  )
}
