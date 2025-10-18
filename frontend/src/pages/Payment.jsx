/**
 * Payment Page - Multiple Payment Methods
 */

import React, { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Divider,
  Alert,
  CircularProgress,
  Chip,
} from '@mui/material';
import PaymentIcon from '@mui/icons-material/Payment';
import CreditCardIcon from '@mui/icons-material/CreditCard';
import { useParams } from 'react-router-dom';
import apiService from '../services/apiService';
import MercadoPagoButton from '../components/MercadoPagoButton';

const Payment = () => {
  const { quoteId } = useParams();
  const [quote, setQuote] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedMethod, setSelectedMethod] = useState(null);
  const [paymentStatus, setPaymentStatus] = useState(null);

  useEffect(() => {
    fetchQuote();
    checkPaymentStatus();
  }, [quoteId]);

  const fetchQuote = async () => {
    try {
      setLoading(true);
      const response = await apiService.get(`/quotes/${quoteId}/`);
      setQuote(response.data);
    } catch (error) {
      console.error('Error fetching quote:', error);
    } finally {
      setLoading(false);
    }
  };

  const checkPaymentStatus = async () => {
    try {
      const response = await apiService.get(`/payments/status/${quoteId}/`);
      setPaymentStatus(response.data);
    } catch (error) {
      console.error('Error checking payment status:', error);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" py={4}>
        <CircularProgress />
      </Box>
    );
  }

  if (!quote) {
    return (
      <Container>
        <Alert severity="error">Orçamento não encontrado</Alert>
      </Container>
    );
  }

  const paymentMethods = [
    {
      id: 'mercadopago',
      name: 'Mercado Pago',
      description: 'Cartão de crédito, débito ou dinheiro',
      icon: <PaymentIcon sx={{ fontSize: 40 }} />,
      available: true,
    },
    {
      id: 'stripe',
      name: 'Stripe',
      description: 'Cartão de crédito internacional',
      icon: <CreditCardIcon sx={{ fontSize: 40 }} />,
      available: true,
    },
    {
      id: 'paypal',
      name: 'PayPal',
      description: 'Conta PayPal ou cartão',
      icon: <PaymentIcon sx={{ fontSize: 40 }} />,
      available: true,
    },
  ];

  return (
    <Container maxWidth="md">
      <Box sx={{ py: 4 }}>
        {/* Header */}
        <Typography variant="h4" gutterBottom>
          Pagamento do Orçamento
        </Typography>

        {/* Payment Status */}
        {paymentStatus && paymentStatus.status === 'paid' && (
          <Alert severity="success" sx={{ mb: 4 }}>
            ✓ Este orçamento já foi pago em {new Date(paymentStatus.paid_at).toLocaleDateString('pt-BR')}
          </Alert>
        )}

        {/* Quote Summary */}
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Typography color="textSecondary" gutterBottom>
                  Número do Orçamento
                </Typography>
                <Typography variant="h6">#{quote.id}</Typography>
              </Grid>

              <Grid item xs={12} sm={6}>
                <Typography color="textSecondary" gutterBottom>
                  Cliente
                </Typography>
                <Typography variant="h6">{quote.client?.name || 'N/A'}</Typography>
              </Grid>

              <Grid item xs={12} sm={6}>
                <Typography color="textSecondary" gutterBottom>
                  Descrição
                </Typography>
                <Typography>{quote.description || 'Sem descrição'}</Typography>
              </Grid>

              <Grid item xs={12} sm={6}>
                <Typography color="textSecondary" gutterBottom>
                  Status
                </Typography>
                <Chip
                  label={quote.status}
                  color={quote.status === 'approved' ? 'success' : 'default'}
                />
              </Grid>

              <Grid item xs={12}>
                <Divider />
              </Grid>

              <Grid item xs={12} sm={6}>
                <Typography color="textSecondary" gutterBottom>
                  Valor do Orçamento
                </Typography>
                <Typography variant="body1">
                  R$ {quote.total_value?.toFixed(2) || '0.00'}
                </Typography>
              </Grid>

              <Grid item xs={12} sm={6}>
                <Typography color="textSecondary" gutterBottom>
                  Valor a Pagar
                </Typography>
                <Typography variant="h5" color="primary">
                  R$ {quote.total_value?.toFixed(2) || '0.00'}
                </Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Payment Methods */}
        <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
          Escolha o Método de Pagamento
        </Typography>

        <Grid container spacing={3}>
          {paymentMethods.map((method) => (
            <Grid item xs={12} sm={6} md={4} key={method.id}>
              <Card
                sx={{
                  cursor: method.available ? 'pointer' : 'default',
                  border: selectedMethod === method.id ? '2px solid #1976d2' : '1px solid #e0e0e0',
                  backgroundColor: selectedMethod === method.id ? '#f5f5f5' : 'white',
                  transition: 'all 0.3s ease',
                  '&:hover': method.available ? {
                    boxShadow: 3,
                    transform: 'translateY(-4px)',
                  } : {},
                  opacity: method.available ? 1 : 0.5,
                }}
                onClick={() => method.available && setSelectedMethod(method.id)}
              >
                <CardContent sx={{ textAlign: 'center' }}>
                  <Box sx={{ mb: 2, color: 'primary.main' }}>
                    {method.icon}
                  </Box>
                  <Typography variant="h6" gutterBottom>
                    {method.name}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {method.description}
                  </Typography>
                  {!method.available && (
                    <Chip label="Indisponível" size="small" sx={{ mt: 1 }} />
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* Payment Action */}
        {selectedMethod && (
          <Box sx={{ mt: 4, p: 3, backgroundColor: '#f5f5f5', borderRadius: 1 }}>
            {selectedMethod === 'mercadopago' && (
              <MercadoPagoButton
                amount={quote.total_value}
                quoteId={quote.id}
                clientId={quote.client?.id}
                onSuccess={() => {
                  checkPaymentStatus();
                }}
              />
            )}

            {selectedMethod === 'stripe' && (
              <Button
                variant="contained"
                color="primary"
                fullWidth
                onClick={() => {
                  // Redirect to Stripe payment page
                  window.location.href = `/payments/stripe/${quote.id}`;
                }}
              >
                Pagar com Stripe
              </Button>
            )}

            {selectedMethod === 'paypal' && (
              <Button
                variant="contained"
                color="primary"
                fullWidth
                onClick={() => {
                  // Redirect to PayPal payment page
                  window.location.href = `/payments/paypal/${quote.id}`;
                }}
              >
                Pagar com PayPal
              </Button>
            )}
          </Box>
        )}

        {/* Additional Info */}
        <Box sx={{ mt: 4, p: 2, backgroundColor: '#e3f2fd', borderRadius: 1 }}>
          <Typography variant="body2" color="textSecondary">
            <strong>ℹ️ Informação:</strong> Seus dados de pagamento são processados de forma segura e criptografada.
            Nós não armazenamos informações de cartão de crédito.
          </Typography>
        </Box>
      </Box>
    </Container>
  );
};

export default Payment;

