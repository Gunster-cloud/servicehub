/**
 * Mercado Pago Payment Button Component
 */

import React, { useState } from 'react';
import { Button, Dialog, DialogTitle, DialogContent, DialogActions, CircularProgress, Alert } from '@mui/material';
import PaymentIcon from '@mui/icons-material/Payment';
import apiService from '../services/apiService';

const MercadoPagoButton = ({ amount, quoteId, clientId, onSuccess, onError }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);

  const handlePayment = async () => {
    try {
      setLoading(true);
      setError(null);

      // Create preference on backend
      const response = await apiService.post('/payments/mercadopago/create-preference/', {
        amount: amount,
        quote_id: quoteId,
        client_id: clientId,
        description: `Orçamento #${quoteId}`,
      });

      if (response.data.init_point) {
        // Redirect to Mercado Pago
        window.location.href = response.data.init_point;
      } else {
        setError('Erro ao criar preferência de pagamento');
      }
    } catch (err) {
      console.error('Error creating Mercado Pago preference:', err);
      setError(err.response?.data?.detail || 'Erro ao processar pagamento');
      if (onError) {
        onError(err);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Button
        variant="contained"
        color="primary"
        startIcon={<PaymentIcon />}
        onClick={() => setOpenDialog(true)}
        disabled={loading}
      >
        Pagar com Mercado Pago
      </Button>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Confirmar Pagamento</DialogTitle>
        <DialogContent sx={{ pt: 2 }}>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          
          <div style={{ marginBottom: '16px' }}>
            <p><strong>Valor:</strong> R$ {amount.toFixed(2)}</p>
            <p><strong>Método:</strong> Mercado Pago</p>
          </div>

          <p style={{ fontSize: '14px', color: '#666' }}>
            Você será redirecionado para o Mercado Pago para completar o pagamento.
          </p>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)} disabled={loading}>
            Cancelar
          </Button>
          <Button
            onClick={handlePayment}
            variant="contained"
            color="primary"
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Confirmar Pagamento'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default MercadoPagoButton;

