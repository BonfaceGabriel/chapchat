import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";

const app = createApp(App);

app.use(createPinia()); // Create and use the Pinia instance
app.use(router); // Use the router

app.mount("#app");
