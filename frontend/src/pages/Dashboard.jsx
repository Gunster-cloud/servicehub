/**
 * Dashboard Page
 */

import React, { useState, useEffect, useContext, useMemo } from 'react';
import {
  Container,
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  CircularProgress,
  Avatar,
  Stack,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';
import apiService from '../services/apiService';
import PeopleOutlineIcon from '@mui/icons-material/PeopleOutline';
import AssignmentOutlinedIcon from '@mui/icons-material/AssignmentOutlined';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import MonetizationOnOutlinedIcon from '@mui/icons-material/MonetizationOnOutlined';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';

const Dashboard = () => {
  const navigate = useNavigate();
  const { user, logout } = useContext(AuthContext);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await apiService.get('/analytics/dashboard/');
        setStats(response.data);
      } catch (error) {
        console.error('Error fetching stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const userInitials = useMemo(() => {
    if (!user) return 'SH';
    const name = `${user?.first_name || ''} ${user?.last_name || ''}`.trim();
    if (!name) {
      return (user?.username || 'SH').slice(0, 2).toUpperCase();
    }
    const initials = name
      .split(' ')
      .filter(Boolean)
      .map((part) => part[0])
      .join('');
    return initials.slice(0, 2).toUpperCase();
  }, [user]);

  const statCards = useMemo(
    () => [
      {
        title: 'Total de Clientes',
        value: stats?.total_clients ?? '—',
        icon: <PeopleOutlineIcon color="primary" sx={{ fontSize: 32 }} />,
        helper: '+12% vs mês passado',
      },
      {
        title: 'Orçamentos Pendentes',
        value: stats?.pending_quotes ?? '—',
        icon: <AssignmentOutlinedIcon color="warning" sx={{ fontSize: 32 }} />,
        helper: 'Revisar solicitações recentes',
      },
      {
        title: 'Orçamentos Aprovados',
        value: stats?.approved_quotes ?? '—',
        icon: <CheckCircleOutlineIcon color="success" sx={{ fontSize: 32 }} />,
        helper: '+5 novos nesta semana',
      },
      {
        title: 'Receita Total',
        value: stats?.total_revenue?.toLocaleString('pt-BR', {
          style: 'currency',
          currency: 'BRL',
          minimumFractionDigits: 2,
        }) ?? 'R$ 0,00',
        icon: <MonetizationOnOutlinedIcon color="secondary" sx={{ fontSize: 32 }} />,
        helper: 'Projeção mensal em alta',
      },
    ],
    [stats]
  );

  const quickActions = [
    {
      title: 'Clientes',
      description: 'Gerenciar clientes e contatos',
      action: () => navigate('/clients'),
    },
    {
      title: 'Orçamentos',
      description: 'Criar e gerenciar orçamentos',
      action: () => navigate('/quotes'),
    },
    {
      title: 'Serviços',
      description: 'Gerenciar serviços oferecidos',
      action: () => navigate('/services'),
    },
  ];

  const upcomingSchedule = [
    {
      title: 'Reunião com cliente ACME',
      date: 'Hoje · 15:00',
    },
    {
      title: 'Envio de orçamento - Projeto Alfa',
      date: 'Amanhã · 09:30',
    },
    {
      title: 'Revisar contratos em andamento',
      date: 'Sexta-feira · 11:00',
    },
  ];

  const highlights = [
    'Metas de receita acima do esperado nesta semana.',
    'Clientes respondendo mais rápido às propostas enviadas.',
    'Equipe com índice de satisfação em 96% neste mês.',
  ];

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        {/* Header */}
        <Box
          sx={{
            background: 'linear-gradient(135deg, #1976d2 0%, #1e88e5 40%, #42a5f5 100%)',
            borderRadius: 4,
            color: 'common.white',
            px: { xs: 3, md: 5 },
            py: { xs: 4, md: 5 },
            mb: 4,
            boxShadow: 6,
          }}
        >
          <Stack direction={{ xs: 'column', md: 'row' }} spacing={4} alignItems="center" justifyContent="space-between">
            <Stack direction="row" spacing={3} alignItems="center">
              <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', width: 72, height: 72, fontSize: 28 }}>
                {userInitials}
              </Avatar>
              <Box>
                <Typography variant="overline" sx={{ opacity: 0.8 }}>
                  Dashboard do ServiceHub
                </Typography>
                <Typography variant="h4" component="h1" fontWeight={700} gutterBottom>
                  Bem-vindo de volta, {user?.first_name || user?.username}!
                </Typography>
                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems={{ xs: 'flex-start', sm: 'center' }}>
                  <Chip icon={<TrendingUpIcon />} label="Relatórios atualizados" color="default" sx={{ bgcolor: 'rgba(255,255,255,0.16)', color: 'common.white' }} />
                  <Chip icon={<CalendarTodayIcon />} label="Agenda sincronizada" sx={{ bgcolor: 'rgba(255,255,255,0.16)', color: 'common.white' }} />
                </Stack>
              </Box>
            </Stack>
            <Button
              variant="contained"
              color="secondary"
              onClick={handleLogout}
              sx={{
                alignSelf: { xs: 'stretch', md: 'center' },
                px: 4,
                py: 1.5,
                fontWeight: 600,
                bgcolor: 'rgba(0,0,0,0.25)',
                '&:hover': {
                  bgcolor: 'rgba(0,0,0,0.35)',
                },
              }}
            >
              Sair
            </Button>
          </Stack>
        </Box>

        {/* Stats */}
        {loading ? (
          <Box display="flex" justifyContent="center" py={4}>
            <CircularProgress />
          </Box>
        ) : (
          <Grid container spacing={3} mb={4}>
            {statCards.map((card) => (
              <Grid key={card.title} item xs={12} sm={6} md={3}>
                <Card
                  sx={{
                    height: '100%',
                    borderRadius: 3,
                    boxShadow: 3,
                    '&:hover': { boxShadow: 6, transform: 'translateY(-2px)' },
                    transition: 'all 0.2s ease-in-out',
                  }}
                >
                  <CardContent>
                    <Stack direction="row" justifyContent="space-between" alignItems="flex-start" mb={2}>
                      <Box>
                        <Typography variant="subtitle2" sx={{ color: 'text.secondary', mb: 1 }}>
                          {card.title}
                        </Typography>
                        <Typography variant="h4" fontWeight={700}>
                          {card.value}
                        </Typography>
                      </Box>
                      {card.icon}
                    </Stack>
                    <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                      {card.helper}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}

        {/* Quick Actions & Highlights */}
        <Grid container spacing={3}>
          <Grid item xs={12} lg={8}>
            <Card sx={{ borderRadius: 3, boxShadow: 3 }}>
              <CardContent>
                <Stack direction="row" alignItems="center" justifyContent="space-between" mb={3}>
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      Ações Rápidas
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Acesse rapidamente as áreas mais utilizadas da plataforma
                    </Typography>
                  </Box>
                </Stack>
                <Grid container spacing={2}>
                  {quickActions.map((action) => (
                    <Grid key={action.title} item xs={12} md={4}>
                      <Card
                        variant="outlined"
                        sx={{
                          height: '100%',
                          borderRadius: 3,
                          borderColor: 'divider',
                          '&:hover': { borderColor: 'primary.main', boxShadow: 4 },
                          transition: 'all 0.2s ease-in-out',
                        }}
                      >
                        <CardContent>
                          <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                            {action.title}
                          </Typography>
                          <Typography variant="body2" color="text.secondary" paragraph>
                            {action.description}
                          </Typography>
                          <Button
                            endIcon={<ArrowForwardIcon />}
                            onClick={action.action}
                            variant="contained"
                            fullWidth
                          >
                            Acessar
                          </Button>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} lg={4}>
            <Stack spacing={3}>
              <Card sx={{ borderRadius: 3, boxShadow: 3 }}>
                <CardContent>
                  <Stack direction="row" alignItems="center" spacing={2} mb={2}>
                    <CalendarTodayIcon color="primary" />
                    <Typography variant="h6">Próximos compromissos</Typography>
                  </Stack>
                  <List disablePadding>
                    {upcomingSchedule.map((item, index) => (
                      <Box key={item.title}>
                        <ListItem disableGutters alignItems="flex-start">
                          <ListItemAvatar>
                            <Avatar sx={{ bgcolor: 'primary.light', color: 'primary.dark' }}>
                              {item.title.charAt(0)}
                            </Avatar>
                          </ListItemAvatar>
                          <ListItemText
                            primary={item.title}
                            secondary={item.date}
                            primaryTypographyProps={{ fontWeight: 600 }}
                          />
                        </ListItem>
                        {index < upcomingSchedule.length - 1 && <Divider variant="inset" component="li" />}
                      </Box>
                    ))}
                  </List>
                </CardContent>
              </Card>

              <Card sx={{ borderRadius: 3, boxShadow: 3 }}>
                <CardContent>
                  <Stack direction="row" alignItems="center" spacing={2} mb={2}>
                    <TrendingUpIcon color="success" />
                    <Typography variant="h6">Insights Rápidos</Typography>
                  </Stack>
                  <List disablePadding>
                    {highlights.map((highlight, index) => (
                      <Box key={highlight}>
                        <ListItem disableGutters>
                          <ListItemText primary={highlight} primaryTypographyProps={{ variant: 'body2' }} />
                        </ListItem>
                        {index < highlights.length - 1 && <Divider component="div" />}
                      </Box>
                    ))}
                  </List>
                </CardContent>
              </Card>
            </Stack>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default Dashboard;

