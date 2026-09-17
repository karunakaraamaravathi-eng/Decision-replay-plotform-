import api from './axios';

export const getNotifications = async (unreadOnly = false, skip = 0, limit = 50) => {
  const res = await api.get('/notifications', {
    params: { unread_only: unreadOnly, skip, limit }
  });
  return res.data;
};

export const getUnreadCount = async () => {
  const res = await api.get('/notifications/unread-count');
  return res.data;
};

export const markNotificationRead = async (id) => {
  const res = await api.patch(`/notifications/${id}/read`);
  return res.data;
};

export const markAllNotificationsRead = async () => {
  const res = await api.post('/notifications/mark-all-read');
  return res.data;
};
