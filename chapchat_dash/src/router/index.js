// src/router/index.js

// WHAT: Import necessary functions and components.
// createRouter: The function to create the router instance.
// createWebHistory: The function to enable "history mode" (clean URLs without the #).
// We import the "page" components we are about to create.
import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue"; // Vue usually creates this
import LoginView from "../views/LoginView.vue"; // We will create this
import RegisterView from "../views/RegisterView.vue"; // We will create this
import DashboardView from "../views/DashboardView.vue"; // We will create this
import ProfileView from "../views/ProfileView.vue"; // We will create this
import ProductListView from "../views/ProductListView.vue"; // We will create this

// WHY: We define our routes in an array. Each route is an object with a path, a name, and a component.
// path: The URL path in the browser.
// name: A unique name for the route, useful for programmatic navigation (e.g., router.push({ name: 'home' })).
// component: The Vue component to display when this route is active.
const routes = [
  {
    path: "/",
    name: "home",
    component: HomeView, // Let's keep the default home view for now
  },
  {
    path: "/login",
    name: "login",
    component: LoginView,
  },
  {
    path: "/register",
    name: "register",
    component: RegisterView,
  },
  {
    // This is a nested route. The DashboardView will act as a layout for other dashboard pages.
    path: "/dashboard",
    name: "dashboard",
    component: DashboardView,
    // WHY: The 'meta' field allows us to add custom data to a route.
    // We use 'requiresAuth: true' to mark routes that a user must be logged in to see.
    meta: { requiresAuth: true },
    children: [
      // Child routes will be rendered inside DashboardView's <router-view>
      {
        path: "profile", // Path will be /dashboard/profile
        name: "dashboard-profile",
        component: ProfileView,
      },
      {
        path: "products", // Path will be /dashboard/products
        name: "dashboard-products",
        component: ProductListView,
      },
      // We will add more dashboard child routes here later (e.g., for products, orders)
    ],
  },
  // You can add a 404 Not Found route later
  // { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFoundView }
];

// WHAT: Create the router instance with our routes and history mode.
const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

// WHY: Implement a "Navigation Guard". This is a function that runs BEFORE every navigation.
// It's the perfect place to check if a user is allowed to access a route.
router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth);
  // We check localStorage directly. This is a quick check.
  // A more robust check might involve verifying the token is not expired.
  const token = localStorage.getItem("accessToken");

  if (requiresAuth && !token) {
    // If the route requires auth and there's no token, redirect to login.
    next({ name: "login" });
  } else {
    // Otherwise, allow the navigation.
    next();
  }
});

// WHAT: Export the router instance so our main.js can use it.
export default router;
