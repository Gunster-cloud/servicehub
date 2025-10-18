/**
 * Schedule Page - Calendar and Appointments
 */

import React, { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  Chip,
} from '@mui/material';
import { Calendar, dateFnsLocalizer } from 'react-big-calendar';
import { format, parse, startOfWeek, getDay, addHours } from 'date-fns';
import ptBR from 'date-fns/locale/pt-BR';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import apiService from '../services/apiService';

const locales = {
  'pt-BR': ptBR,
};

const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek,
  getDay,
  locales,
});

const Schedule = () => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingEvent, setEditingEvent] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    client_id: '',
    service_id: '',
    start: new Date(),
    end: addHours(new Date(), 1),
    notes: '',
  });
  const [clients, setClients] = useState([]);
  const [services, setServices] = useState([]);

  useEffect(() => {
    fetchSchedules();
    fetchClients();
    fetchServices();
  }, []);

  const fetchSchedules = async () => {
    try {
      setLoading(true);
      const response = await apiService.get('/services/schedules/');
      const formattedEvents = response.data.map((schedule) => ({
        id: schedule.id,
        title: schedule.title,
        start: new Date(schedule.start_time),
        end: new Date(schedule.end_time),
        resource: schedule,
      }));
      setEvents(formattedEvents);
    } catch (error) {
      console.error('Error fetching schedules:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchClients = async () => {
    try {
      const response = await apiService.get('/clients/');
      setClients(response.data);
    } catch (error) {
      console.error('Error fetching clients:', error);
    }
  };

  const fetchServices = async () => {
    try {
      const response = await apiService.get('/services/');
      setServices(response.data);
    } catch (error) {
      console.error('Error fetching services:', error);
    }
  };

  const handleSelectSlot = (slotInfo) => {
    setFormData({
      ...formData,
      start: slotInfo.start,
      end: slotInfo.end,
    });
    setEditingEvent(null);
    setOpenDialog(true);
  };

  const handleSelectEvent = (event) => {
    setEditingEvent(event.resource);
    setFormData({
      title: event.title,
      client_id: event.resource.client_id,
      service_id: event.resource.service_id,
      start: event.start,
      end: event.end,
      notes: event.resource.notes || '',
    });
    setOpenDialog(true);
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSaveEvent = async () => {
    try {
      const payload = {
        title: formData.title,
        client_id: formData.client_id,
        service_id: formData.service_id,
        start_time: formData.start.toISOString(),
        end_time: formData.end.toISOString(),
        notes: formData.notes,
      };

      if (editingEvent) {
        await apiService.put(`/services/schedules/${editingEvent.id}/`, payload);
      } else {
        await apiService.post('/services/schedules/', payload);
      }

      fetchSchedules();
      setOpenDialog(false);
      setFormData({
        title: '',
        client_id: '',
        service_id: '',
        start: new Date(),
        end: addHours(new Date(), 1),
        notes: '',
      });
    } catch (error) {
      console.error('Error saving schedule:', error);
    }
  };

  const handleDeleteEvent = async () => {
    if (!editingEvent) return;

    try {
      await apiService.delete(`/services/schedules/${editingEvent.id}/`);
      fetchSchedules();
      setOpenDialog(false);
    } catch (error) {
      console.error('Error deleting schedule:', error);
    }
  };

  const eventStyleGetter = (event) => {
    let backgroundColor = '#3174ad';
    
    if (event.resource?.status === 'completed') {
      backgroundColor = '#4caf50';
    } else if (event.resource?.status === 'cancelled') {
      backgroundColor = '#f44336';
    }

    return {
      style: {
        backgroundColor,
        borderRadius: '5px',
        opacity: 0.8,
        color: 'white',
        border: '0px',
        display: 'block',
      },
    };
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" py={4}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        {/* Header */}
        <Box
          display="flex"
          justifyContent="space-between"
          alignItems="center"
          mb={4}
        >
          <h1>Agendamentos</h1>
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={() => {
              setEditingEvent(null);
              setFormData({
                title: '',
                client_id: '',
                service_id: '',
                start: new Date(),
                end: addHours(new Date(), 1),
                notes: '',
              });
              setOpenDialog(true);
            }}
          >
            Novo Agendamento
          </Button>
        </Box>

        {/* Calendar */}
        <Card>
          <CardContent>
            <Calendar
              localizer={localizer}
              events={events}
              startAccessor="start"
              endAccessor="end"
              style={{ height: 600 }}
              onSelectSlot={handleSelectSlot}
              onSelectEvent={handleSelectEvent}
              selectable
              popup
              eventPropGetter={eventStyleGetter}
              messages={{
                today: 'Hoje',
                previous: 'Anterior',
                next: 'Próximo',
                month: 'Mês',
                week: 'Semana',
                day: 'Dia',
                agenda: 'Agenda',
                date: 'Data',
                time: 'Hora',
                event: 'Evento',
                noEventsInRange: 'Nenhum evento neste período',
              }}
            />
          </CardContent>
        </Card>

        {/* Upcoming Events */}
        <Box mt={4}>
          <Typography variant="h6" gutterBottom>
            Próximos Agendamentos
          </Typography>
          <Grid container spacing={2}>
            {events
              .filter((e) => e.start > new Date())
              .sort((a, b) => a.start - b.start)
              .slice(0, 5)
              .map((event) => (
                <Grid item xs={12} sm={6} md={4} key={event.id}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6">{event.title}</Typography>
                      <Typography color="textSecondary">
                        {format(event.start, 'dd/MM/yyyy HH:mm')}
                      </Typography>
                      {event.resource?.status && (
                        <Chip
                          label={event.resource.status}
                          size="small"
                          sx={{ mt: 1 }}
                          color={
                            event.resource.status === 'completed'
                              ? 'success'
                              : 'default'
                          }
                        />
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              ))}
          </Grid>
        </Box>
      </Box>

      {/* Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingEvent ? 'Editar Agendamento' : 'Novo Agendamento'}
        </DialogTitle>
        <DialogContent sx={{ pt: 2 }}>
          <TextField
            fullWidth
            label="Título"
            name="title"
            value={formData.title}
            onChange={handleFormChange}
            margin="normal"
          />

          <FormControl fullWidth margin="normal">
            <InputLabel>Cliente</InputLabel>
            <Select
              name="client_id"
              value={formData.client_id}
              onChange={handleFormChange}
              label="Cliente"
            >
              {clients.map((client) => (
                <MenuItem key={client.id} value={client.id}>
                  {client.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl fullWidth margin="normal">
            <InputLabel>Serviço</InputLabel>
            <Select
              name="service_id"
              value={formData.service_id}
              onChange={handleFormChange}
              label="Serviço"
            >
              {services.map((service) => (
                <MenuItem key={service.id} value={service.id}>
                  {service.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <TextField
            fullWidth
            label="Data e Hora de Início"
            name="start"
            type="datetime-local"
            value={format(formData.start, "yyyy-MM-dd'T'HH:mm")}
            onChange={(e) =>
              setFormData({
                ...formData,
                start: new Date(e.target.value),
              })
            }
            margin="normal"
            InputLabelProps={{ shrink: true }}
          />

          <TextField
            fullWidth
            label="Data e Hora de Término"
            name="end"
            type="datetime-local"
            value={format(formData.end, "yyyy-MM-dd'T'HH:mm")}
            onChange={(e) =>
              setFormData({
                ...formData,
                end: new Date(e.target.value),
              })
            }
            margin="normal"
            InputLabelProps={{ shrink: true }}
          />

          <TextField
            fullWidth
            label="Observações"
            name="notes"
            value={formData.notes}
            onChange={handleFormChange}
            margin="normal"
            multiline
            rows={3}
          />
        </DialogContent>
        <DialogActions>
          {editingEvent && (
            <Button
              onClick={handleDeleteEvent}
              color="error"
              startIcon={<DeleteIcon />}
            >
              Deletar
            </Button>
          )}
          <Button onClick={() => setOpenDialog(false)}>Cancelar</Button>
          <Button onClick={handleSaveEvent} variant="contained" color="primary">
            Salvar
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Schedule;

