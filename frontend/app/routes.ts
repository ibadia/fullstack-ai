import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  index("routes/home.tsx"),
  route("login", "routes/login.tsx"),
  route("signup", "routes/signup.tsx"),
  route("health", "routes/health.tsx"),
  route("/receipts", "routes/receipts.tsx"),
] satisfies RouteConfig;
