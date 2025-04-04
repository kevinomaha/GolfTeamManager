import React from 'react';
import { 
  Container, 
  Box, 
  Typography, 
  Paper, 
  Grid, 
  Card, 
  CardContent, 
  CardHeader,
  Button,
  Divider
} from '@mui/material';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import EventIcon from '@mui/icons-material/Event';
import PeopleIcon from '@mui/icons-material/People';
import SwapHorizIcon from '@mui/icons-material/SwapHoriz';
import ScoreboardIcon from '@mui/icons-material/Scoreboard';

const Dashboard: React.FC = () => {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();

  // Extract user's name from Cognito attributes (would be implemented in a real app)
  const userName = user?.getUsername() || 'Golfer';

  const handleNavigate = (path: string) => {
    navigate(path);
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3}>
        {/* Welcome Section */}
        <Grid item xs={12}>
          <Paper 
            elevation={2} 
            sx={{ 
              p: 3, 
              display: 'flex', 
              flexDirection: 'column',
              borderRadius: 2
            }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography component="h1" variant="h4">
                Welcome, {userName}
              </Typography>
              <Button variant="outlined" color="primary" onClick={() => signOut()}>
                Sign Out
              </Button>
            </Box>
            <Typography variant="body1">
              Golf League Manager helps you keep track of your golf schedule, manage player swaps, record scores, and communicate with other players.
            </Typography>
          </Paper>
        </Grid>

        {/* Quick Access Cards */}
        <Grid item xs={12} md={6} lg={3}>
          <Card 
            sx={{ 
              height: '100%', 
              display: 'flex', 
              flexDirection: 'column',
              cursor: 'pointer',
              transition: 'transform 0.2s',
              '&:hover': {
                transform: 'scale(1.02)',
              },
            }}
            onClick={() => handleNavigate('/schedule')}
          >
            <CardHeader
              title="Schedule"
              titleTypographyProps={{ variant: 'h6' }}
              avatar={<EventIcon color="primary" />}
            />
            <Divider />
            <CardContent sx={{ flexGrow: 1 }}>
              <Typography variant="body2">
                View upcoming games and your personal schedule.
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6} lg={3}>
          <Card 
            sx={{ 
              height: '100%', 
              display: 'flex', 
              flexDirection: 'column',
              cursor: 'pointer',
              transition: 'transform 0.2s',
              '&:hover': {
                transform: 'scale(1.02)',
              },
            }}
            onClick={() => handleNavigate('/players')}
          >
            <CardHeader
              title="Players"
              titleTypographyProps={{ variant: 'h6' }}
              avatar={<PeopleIcon color="primary" />}
            />
            <Divider />
            <CardContent sx={{ flexGrow: 1 }}>
              <Typography variant="body2">
                View player directory and contact information.
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6} lg={3}>
          <Card 
            sx={{ 
              height: '100%', 
              display: 'flex', 
              flexDirection: 'column',
              cursor: 'pointer',
              transition: 'transform 0.2s',
              '&:hover': {
                transform: 'scale(1.02)',
              },
            }}
            onClick={() => handleNavigate('/swaps')}
          >
            <CardHeader
              title="Swap Requests"
              titleTypographyProps={{ variant: 'h6' }}
              avatar={<SwapHorizIcon color="primary" />}
            />
            <Divider />
            <CardContent sx={{ flexGrow: 1 }}>
              <Typography variant="body2">
                Request and manage date swaps with other players.
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6} lg={3}>
          <Card 
            sx={{ 
              height: '100%', 
              display: 'flex', 
              flexDirection: 'column',
              cursor: 'pointer',
              transition: 'transform 0.2s',
              '&:hover': {
                transform: 'scale(1.02)',
              },
            }}
            onClick={() => handleNavigate('/scores')}
          >
            <CardHeader
              title="Scores"
              titleTypographyProps={{ variant: 'h6' }}
              avatar={<ScoreboardIcon color="primary" />}
            />
            <Divider />
            <CardContent sx={{ flexGrow: 1 }}>
              <Typography variant="body2">
                Record scores and view performance statistics.
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Upcoming Games Section - This would be populated with real data in the full implementation */}
        <Grid item xs={12}>
          <Paper
            sx={{
              p: 3,
              display: 'flex',
              flexDirection: 'column',
              borderRadius: 2
            }}
          >
            <Typography component="h2" variant="h5" gutterBottom>
              Upcoming Games
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Your upcoming games will appear here once the schedule is set.
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;
