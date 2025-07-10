import { useEffect } from "react";
import useWebSocket from "react-use-websocket";
import { useAuthStore } from "../store/authStore";

export const useInboxSocket = () => {
  // Get the access token from our auth store
  const accessToken = useAuthStore((state) => state.accessToken);

  // Construct the WebSocket URL. It must use 'ws://' or 'wss://'
  // For local dev, it's 'ws://'. For deployed Render, it's 'wss://'.
  const wsProtocol = window.location.protocol === "https:" ? "wss" : "ws";
  // We get the hostname from the API base URL, but strip the http/s part
  const wsHost = import.meta.env.VITE_API_BASE_URL.replace(
    /^https?:\/\//,
    ""
  ).split("/api")[0];
  const socketUrl = `${wsProtocol}://${wsHost}/ws/inbox/`;

  // The useWebSocket hook from the library
  const { lastJsonMessage, sendJsonMessage } = useWebSocket(
    // Only try to connect if an accessToken exists
    accessToken ? socketUrl : null,
    {
      // We will send the JWT token as a query parameter for authentication
      // This is a common pattern for authenticating WebSocket connections
      queryParams: { token: accessToken },
      shouldReconnect: (_closeEvent) => true, // Automatically reconnect
    }
  );

  // This `useEffect` hook listens for incoming messages from the WebSocket
  useEffect(() => {
        if (lastJsonMessage !== null) {
            console.log("Received WebSocket message:", lastJsonMessage);

            // Destructure the event from the server
            const { type, payload } = lastJsonMessage;

            // (+) Handle the new_order event specifically
            if (type === 'new_order') {
                const order = payload; // The payload IS the order data
                // For now, a detailed alert proves the end-to-end connection works!
                alert(
                    `🎉 New Order Received! 🎉\n\n` +
                    `Order ID: ${order.id}\n` +
                    `Customer: ${order.customer_name}\n` +
                    `Total: KES ${order.total_amount}`
                );

                // TODO in next step: Instead of an alert, we'll use a toast notification
                // library and automatically update the orders list on the OrderPage.
            }
        }
    }, [lastJsonMessage]); // Rerun this effect whenever a new message arrives

  // Return a function that our app can use to send messages *to* the server
  // We don't need this yet for notifications, but it's essential for the live chat reply box.
  const sendMessage = (message) => {
    console.log("Sending message via WebSocket:", message);
    sendJsonMessage({ message });
  };

  return { sendMessage, lastJsonMessage };
};
