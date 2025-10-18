/**
 * Services Page - List, Create, Edit, Delete
 */

import React, { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  TextField,
  CircularProgress,
  IconButton,
  Tooltip,
  Alert,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import apiService from '../services/apiService';

const Services = () => {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: '',
    base_price: '',
    unit: 'hour',
  });

  // Fetch services
  useEffect(() => {
    fetchServices();
  }, []);

  const fetchServices = async () => {
    try {
      setLoading(true);
      const response = await apiService.get('/services/');
      setServices(response.data.results || response.data);
      setError(null);
    } catch (err) {
      setError('Erro ao carregar serviços');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (service = null) => {
    if (service) {
      setEditingId(service.id);
      setFormData(service);
    } else {
      setEditingId(null);
      setFormData({
        name: '',
        description: '',
        category: '',
        base_price: '',
        unit: 'hour',
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingId(null);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        await apiService.put(`/services/${editingId}/`, formData);
        setSuccess('Serviço atualizado com sucesso!');
      } else {
        await apiService.post('/services/', formData);
        setSuccess('Serviço criado com sucesso!');
      }
      handleCloseDialog();
      fetchServices();
    } catch (err) {
      setError(err.response?.data?.message || 'Erro ao salvar serviço');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Tem certeza que deseja deletar este serviço?')) {
      try {
        await apiService.delete(`/services/${id}/`);
        setSuccess('Serviço deletado com sucesso!');
        fetchServices();
      } catch (err) {
        setError('Erro ao deletar serviço');
      }
    }
  };

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
          <h1>Serviços</h1>
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
          >
            Novo Serviço
          </Button>
        </Box>

        {/* Alerts */}
        {error && (
          <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        {success && (
          <Alert severity="success" onClose={() => setSuccess(null)} sx={{ mb: 2 }}>
            {success}
          </Alert>
        )}

        {/* Loading */}
        {loading ? (
          <Box display="flex" justifyContent="center" py={4}>
            <CircularProgress />
          </Box>
        ) : (
          /* Table */
          <TableContainer component={Paper}>
            <Table>
              <TableHead sx={{ backgroundColor: '#f5f5f5' }}>
                <TableRow>
                  <TableCell>Nome</TableCell>
                  <TableCell>Categoria</TableCell>
                  <TableCell>Preço Base</TableCell>
                  <TableCell>Unidade</TableCell>
                  <TableCell>Descrição</TableCell>
                  <TableCell align="right">Ações</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {services.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      Nenhum serviço encontrado
                    </TableCell>
                  </TableRow>
                ) : (
                  services.map((service) => (
                    <TableRow key={service.id}>
                      <TableCell>{service.name}</TableCell>
                      <TableCell>{service.category}</TableCell>
                      <TableCell>
                        R$ {parseFloat(service.base_price).toFixed(2)}
                      </TableCell>
                      <TableCell>{service.unit}</TableCell>
                      <TableCell>{service.description?.substring(0, 50)}...</TableCell>
                      <TableCell align="right">
                        <Tooltip title="Editar">
                          <IconButton
                            size="small"
                            onClick={() => handleOpenDialog(service)}
                          >
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Deletar">
                          <IconButton
                            size="small"
                            onClick={() => handleDelete(service.id)}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Box>

      {/* Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <Box sx={{ p: 3 }}>
          <h2>{editingId ? 'Editar Serviço' : 'Novo Serviço'}</h2>
          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Nome"
              name="name"
              value={formData.name}
              onChange={handleChange}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Categoria"
              name="category"
              value={formData.category}
              onChange={handleChange}
              margin="normal"
            />
            <TextField
              fullWidth
              label="Preço Base"
              name="base_price"
              type="number"
              value={formData.base_price}
              onChange={handleChange}
              margin="normal"
              required
              inputProps={{ step: '0.01' }}
            />
            <TextField
              fullWidth
              select
              label="Unidade"
              name="unit"
              value={formData.unit}
              onChange={handleChange}
              margin="normal"
              SelectProps={{
                native: true,
              }}
            >
              <option value="hour">Hora</option>
              <option value="day">Dia</option>
              <option value="unit">Unidade</option>
              <option value="project">Projeto</option>
            </TextField>
            <TextField
              fullWidth
              label="Descrição"
              name="description"
              value={formData.description}
              onChange={handleChange}
              margin="normal"
              multiline
              rows={4}
            />

            <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                color="primary"
                type="submit"
                fullWidth
              >
                {editingId ? 'Atualizar' : 'Criar'}
              </Button>
              <Button
                variant="outlined"
                onClick={handleCloseDialog}
                fullWidth
              >
                Cancelar
              </Button>
            </Box>
          </Box>
        </Box>
      </Dialog>
    </Container>
  );
};

export default Services;

