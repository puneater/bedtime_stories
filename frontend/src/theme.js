import { createTheme } from '@mui/material/styles'

const theme = createTheme({
  palette: {
    mode: 'dark',
    background: { default: '#0b1020', paper: '#121629' },
    primary: { main: '#90caf9' },
    secondary: { main: '#f48fb1' }
  },
  typography: {
    fontFamily: 'Inter, system-ui, Avenir, Helvetica, Arial, sans-serif',
    h3: { fontWeight: 700 },
    button: { textTransform: 'none', fontWeight: 700 }
  },
  shape: { borderRadius: 16 }
})

export default theme
