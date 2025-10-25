/**
 * Register Page
 */

import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  TextField,
  Button,
  Typography,
  Alert,
  MenuItem,
  Card,
  CardContent,
  Grid,
} from '@mui/material';
import { AuthContext } from '../contexts/AuthContext';

const ROLE_OPTIONS = [
  { value: 'admin', label: 'Administrador' },
  { value: 'manager', label: 'Gerenciador' },
  { value: 'salesperson', label: 'Vendedor' },
  { value: 'technician', label: 'Técnico' },
  { value: 'client', label: 'Cliente' },
];

const Register = () => {
  const navigate = useNavigate();
  const { register, error } = useContext(AuthContext);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: '',
    phone: '',
    role: 'salesperson',
    company_name: '',
  });
  const [loading, setLoading] = useState(false);
  const [localError, setLocalError] = useState(null);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setLocalError(null);

    try {
      await register(formData);
      navigate('/login', {
        replace: true,
        state: { registered: true },
      });
    } catch (err) {
      const detail = err?.detail || err?.message || 'Erro ao criar conta';
      setLocalError(detail);
    } finally {
      setLoading(false);
    }
  };

  const combinedError = error?.detail || error?.message || localError;

  return (
    <Container maxWidth="sm">
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
      >
        <Card sx={{ width: '100%' }}>
          <CardContent>
            <Typography variant="h4" component="h1" gutterBottom align="center">
              Crie sua conta
            </Typography>
            <Typography
              variant="body2"
              color="textSecondary"
              align="center"
              gutterBottom
            >
              Preencha os dados abaixo para começar a usar o ServiceHub.
            </Typography>

            {combinedError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {typeof combinedError === 'string'
                  ? combinedError
                  : 'Revise os campos informados e tente novamente.'}
              </Alert>
            )}

            <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3 }}>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Nome"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleChange}
                    required
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Sobrenome"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleChange}
                    required
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Nome de usuário"
                    name="username"
                    value={formData.username}
                    onChange={handleChange}
                    required
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Email"
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Senha"
                    name="password"
                    type="password"
                    value={formData.password}
                    onChange={handleChange}
                    required
                    inputProps={{ minLength: 8 }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Confirmar senha"
                    name="password_confirm"
                    type="password"
                    value={formData.password_confirm}
                    onChange={handleChange}
                    required
                    inputProps={{ minLength: 8 }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Telefone"
                    name="phone"
                    value={formData.phone}
                    onChange={handleChange}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    select
                    fullWidth
                    label="Função"
                    name="role"
                    value={formData.role}
                    onChange={handleChange}
                    helperText="Selecione o perfil de acesso"
                  >
                    {ROLE_OPTIONS.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </TextField>
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Empresa"
                    name="company_name"
                    value={formData.company_name}
                    onChange={handleChange}
                    placeholder="Nome da sua empresa (opcional)"
                  />
                </Grid>
              </Grid>

              <Button
                fullWidth
                variant="contained"
                color="primary"
                type="submit"
                sx={{ mt: 3 }}
                disabled={loading}
              >
                {loading ? 'Cadastrando...' : 'Criar conta'}
              </Button>

              <Typography variant="body2" align="center" sx={{ mt: 2 }}>
                Já tem conta?{' '}
                <Button
                  color="primary"
                  onClick={() => navigate('/login')}
                  sx={{ textTransform: 'none' }}
                >
                  Entrar
                </Button>
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
};

export default Register;
