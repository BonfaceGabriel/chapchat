import React, { useEffect, useState } from 'react';
import { Box, Typography, List, ListItemButton, ListItemText, Divider, TextField, IconButton, Switch, FormControlLabel } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import apiClient from '../services/api';
import { useInboxSocket } from '../hooks/useInboxSocket';

function InboxPage() {
  const [conversations, setConversations] = useState([]);
  const [selected, setSelected] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [takeover, setTakeover] = useState(false);

  const { lastJsonMessage, sendJsonMessage } = useInboxSocket();

  const fetchConversations = async () => {
    const resp = await apiClient.get('/whatsapp/conversations/');
    setConversations(resp.data);
  };

  const fetchMessages = async (conversationId) => {
    const resp = await apiClient.get(`/whatsapp/conversations/${conversationId}/messages/`);
    setMessages(resp.data);
  };

  useEffect(() => {
    fetchConversations();
  }, []);

  useEffect(() => {
    if (selected) {
      fetchMessages(selected.id);
    }
  }, [selected]);

  useEffect(() => {
    if (lastJsonMessage && lastJsonMessage.type === 'message') {
      const msg = lastJsonMessage.message;
      if (selected && msg.conversation === selected.id) {
        setMessages((prev) => [...prev, msg]);
      }
    }
  }, [lastJsonMessage]);

  const handleSend = async () => {
    if (!input || !selected) return;
    const resp = await apiClient.post(`/whatsapp/conversations/${selected.id}/messages/`, { content: input });
    setMessages((prev) => [...prev, resp.data]);
    setInput('');
  };

  return (
    <Box sx={{ display: 'flex', height: '80vh', bgcolor: '#fff' }}>
      <Box sx={{ width: 300, borderRight: '1px solid #ccc', overflowY: 'auto' }}>
        <Typography variant="h6" sx={{ p: 2 }}>Conversations</Typography>
        <List>
          {conversations.map((c) => (
            <ListItemButton key={c.id} selected={selected?.id === c.id} onClick={() => setSelected(c)}>
              <ListItemText primary={c.customer.name || c.customer.phone_number} secondary={c.last_message?.content} />
            </ListItemButton>
          ))}
        </List>
      </Box>
      <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        {selected ? (
          <>
            <Box sx={{ p: 2, borderBottom: '1px solid #ccc', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="h6">{selected.customer.name || selected.customer.phone_number}</Typography>
              <FormControlLabel control={<Switch checked={takeover} onChange={(e) => setTakeover(e.target.checked)} />} label="Take over" />
            </Box>
            <Box sx={{ flexGrow: 1, p: 2, overflowY: 'auto' }}>
              {messages.map((m) => (
                <Box key={m.id} sx={{ display: 'flex', justifyContent: m.sender === 'seller' ? 'flex-end' : 'flex-start', mb: 1 }}>
                  <Box sx={{ bgcolor: m.sender === 'seller' ? '#dcf8c6' : '#f1f0f0', p: 1.5, borderRadius: 2, maxWidth: '70%' }}>
                    <Typography variant="body2">{m.content}</Typography>
                  </Box>
                </Box>
              ))}
            </Box>
            <Divider />
            <Box sx={{ p: 1, display: 'flex' }}>
              <TextField fullWidth size="small" value={input} onChange={(e) => setInput(e.target.value)} onKeyPress={(e) => { if (e.key === 'Enter') handleSend(); }} />
              <IconButton color="primary" onClick={handleSend}><SendIcon /></IconButton>
            </Box>
          </>
        ) : (
          <Box sx={{ p: 4 }}><Typography>Select a conversation to start chatting.</Typography></Box>
        )}
      </Box>
    </Box>
  );
}

export default InboxPage;
