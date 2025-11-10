import { AppBar, Toolbar, Typography, Stack } from '@mui/material'
import NightlightIcon from '@mui/icons-material/Nightlight'

export default function Header() {
  return (
    <AppBar
      position="sticky"
      elevation={0}
      className="header-blur"
      sx={{ backgroundColor: 'transparent', backdropFilter: 'blur(6px)', borderBottom: '1px solid rgba(255,255,255,0.06)' }}
    >
      <Toolbar sx={{ justifyContent: 'center', minHeight: 72 }}>
        <Stack direction="row" spacing={1.5} alignItems="center">
          <NightlightIcon sx={{ opacity: 0.9 }} />
          <Typography
            variant="h3"
            className="brand-title p-5 ps-1"
            sx={{
              fontFamily: `'Baloo 2', cursive`,
              letterSpacing: 0.4,
              userSelect: 'none',
            }}
          >
            Bedtime Stories
          </Typography>
        </Stack>
      </Toolbar>
    </AppBar>
  )
}
