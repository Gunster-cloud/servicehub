/**
 * Login Page
 */

import React, { useState, useContext, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Container,
  Box,
  TextField,
  Button,
  Typography,
  Alert,
  Card,
  CardContent,
} from '@mui/material';
import { AuthContext } from '../contexts/AuthContext';

const Login = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, error } = useContext(AuthContext);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);
  const [localError, setLocalError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  useEffect(() => {
    if (location.state?.registered) {
      setSuccessMessage('Cadastro realizado com sucesso! Faça login para continuar.');
      navigate(location.pathname, { replace: true });
    }
  }, [location, navigate]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setLocalError(null);

    try {
      await login(formData.email, formData.password);
      navigate('/dashboard');
    } catch (err) {
      setLocalError(err.message || 'Erro ao fazer login');
    } finally {
      setLoading(false);
    }
  };

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
              ServiceHub
            </Typography>
            <Typography
              variant="body2"
              color="textSecondary"
              align="center"
              gutterBottom
            >
              Faça login para continuar
            </Typography>

            {successMessage && (
              <Alert severity="success" sx={{ mb: 2 }}>
                {successMessage}
              </Alert>
            )}

            {(error || localError) && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error?.detail || error?.message || localError}
              </Alert>
            )}

            <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3 }}>
              <TextField
                fullWidth
                label="Email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                margin="normal"
                required
              />

              <TextField
                fullWidth
                label="Senha"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                margin="normal"
                required
              />

              <Button
                fullWidth
                variant="contained"
                color="primary"
                type="submit"
                sx={{ mt: 3 }}
                disabled={loading}
              >
                {loading ? 'Entrando...' : 'Entrar'}
              </Button>

              <Typography variant="body2" align="center" sx={{ mt: 2 }}>
                Não tem conta?{' '}
                <Button
                  color="primary"
                  onClick={() => navigate('/register')}
                  sx={{ textTransform: 'none' }}
                >
                  Cadastre-se
                </Button>
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
};

export default Login;

