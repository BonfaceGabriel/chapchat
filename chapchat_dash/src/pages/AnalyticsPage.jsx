import React, { useEffect, useState } from 'react';
import { Box, Typography, CircularProgress, Alert, Grid, Paper } from '@mui/material';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer,
} from 'recharts';
import apiClient from '../services/api';

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7f7f', '#8dd1e1', '#a4de6c'];

function AnalyticsPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await apiClient.get('/analytics/');
        setData(response.data);
      } catch {
        setError('Failed to load analytics');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;
  if (!data) return null;

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Analytics Overview</Typography>
      <Grid container spacing={4}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Monthly Sales</Typography>
            <Typography variant="body2" gutterBottom>Total revenue per month</Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={data.monthly_sales}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="total" stroke="#8884d8" />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Order Status Distribution</Typography>
            <Typography variant="body2" gutterBottom>Breakdown of order statuses</Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={Object.entries(data.status_distribution).map(([name, value]) => ({ name, value }))}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label
                >
                  {Object.keys(data.status_distribution).map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Top Products</Typography>
            <Typography variant="body2" gutterBottom>Best sellers by quantity</Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={data.top_products}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="quantity" fill="#82ca9d" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Totals</Typography>
            <Typography variant="body2" gutterBottom>{`Total orders: ${data.total_orders}`}</Typography>
            <Typography variant="body2" gutterBottom>{`Total sales: KES ${parseFloat(data.total_sales).toFixed(2)}`}</Typography>
            <Typography variant="body2" gutterBottom>{`Average order value: KES ${parseFloat(data.average_order_value).toFixed(2)}`}</Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default AnalyticsPage;
