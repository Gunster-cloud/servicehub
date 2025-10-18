/**
 * Quotes Page - List, Create, Edit, Delete
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
  Chip,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import VisibilityIcon from '@mui/icons-material/Visibility';
import apiService from '../services/apiService';

const Quotes = () => {
  const [quotes, setQuotes] = useState([]);
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [formData, setFormData] = useState({
    client: '',
    title: '',
    description: '',
    total_value: '',
    validity_days: 30,
    status: 'draft',
  });

  // Fetch quotes and clients
  useEffect(() => {
    fetchQuotes();
    fetchClients();
  }, []);

  const fetchQuotes = async () => {
    try {
      setLoading(true);
      const response = await apiService.get('/quotes/');
      setQuotes(response.data.results || response.data);
      setError(null);
    } catch (err) {
      setError('Erro ao carregar orçamentos');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchClients = async () => {
    try {
      const response = await apiService.get('/clients/');
      setClients(response.data.results || response.data);
    } catch (err) {
      console.error('Erro ao carregar clientes:', err);
    }
  };

  const handleOpenDialog = (quote = null) => {
    if (quote) {
      setEditingId(quote.id);
      setFormData(quote);
    } else {
      setEditingId(null);
      setFormData({
        client: '',
        title: '',
        description: '',
        total_value: '',
        validity_days: 30,
        status: 'draft',
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
        await apiService.put(`/quotes/${editingId}/`, formData);
        setSuccess('Orçamento atualizado com sucesso!');
      } else {
        await apiService.post('/quotes/', formData);
        setSuccess('Orçamento criado com sucesso!');
      }
      handleCloseDialog();
      fetchQuotes();
    } catch (err) {
      setError(err.response?.data?.message || 'Erro ao salvar orçamento');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Tem certeza que deseja deletar este orçamento?')) {
      try {
        await apiService.delete(`/quotes/${id}/`);
        setSuccess('Orçamento deletado com sucesso!');
        fetchQuotes();
      } catch (err) {
        setError('Erro ao deletar orçamento');
      }
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      draft: 'default',
      sent: 'info',
      approved: 'success',
      rejected: 'error',
    };
    return colors[status] || 'default';
  };

  const getStatusLabel = (status) => {
    const labels = {
      draft: 'Rascunho',
      sent: 'Enviado',
      approved: 'Aprovado',
      rejected: 'Rejeitado',
    };
    return labels[status] || status;
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
          <h1>Orçamentos</h1>
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
          >
            Novo Orçamento
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
                  <TableCell>Título</TableCell>
                  <TableCell>Cliente</TableCell>
                  <TableCell>Valor</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Data</TableCell>
                  <TableCell align="right">Ações</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {quotes.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      Nenhum orçamento encontrado
                    </TableCell>
                  </TableRow>
                ) : (
                  quotes.map((quote) => (
                    <TableRow key={quote.id}>
                      <TableCell>{quote.title}</TableCell>
                      <TableCell>
                        {clients.find((c) => c.id === quote.client)?.name || 'N/A'}
                      </TableCell>
                      <TableCell>
                        R$ {parseFloat(quote.total_value).toFixed(2)}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={getStatusLabel(quote.status)}
                          color={getStatusColor(quote.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {new Date(quote.created_at).toLocaleDateString('pt-BR')}
                      </TableCell>
                      <TableCell align="right">
                        <Tooltip title="Visualizar">
                          <IconButton size="small">
                            <VisibilityIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Editar">
                          <IconButton
                            size="small"
                            onClick={() => handleOpenDialog(quote)}
                          >
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Deletar">
                          <IconButton
                            size="small"
                            onClick={() => handleDelete(quote.id)}
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
          <h2>{editingId ? 'Editar Orçamento' : 'Novo Orçamento'}</h2>
          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
            <TextField
              fullWidth
              select
              label="Cliente"
              name="client"
              value={formData.client}
              onChange={handleChange}
              margin="normal"
              required
              SelectProps={{
                native: true,
              }}
            >
              <option value="">Selecione um cliente</option>
              {clients.map((client) => (
                <option key={client.id} value={client.id}>
                  {client.name}
                </option>
              ))}
            </TextField>
            <TextField
              fullWidth
              label="Título"
              name="title"
              value={formData.title}
              onChange={handleChange}
              margin="normal"
              required
            />
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
            <TextField
              fullWidth
              label="Valor Total"
              name="total_value"
              type="number"
              value={formData.total_value}
              onChange={handleChange}
              margin="normal"
              required
              inputProps={{ step: '0.01' }}
            />
            <TextField
              fullWidth
              label="Validade (dias)"
              name="validity_days"
              type="number"
              value={formData.validity_days}
              onChange={handleChange}
              margin="normal"
            />
            <TextField
              fullWidth
              select
              label="Status"
              name="status"
              value={formData.status}
              onChange={handleChange}
              margin="normal"
              SelectProps={{
                native: true,
              }}
            >
              <option value="draft">Rascunho</option>
              <option value="sent">Enviado</option>
              <option value="approved">Aprovado</option>
              <option value="rejected">Rejeitado</option>
            </TextField>

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

export default Quotes;

