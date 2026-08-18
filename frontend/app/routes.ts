import { type RouteConfig, layout, index, route } from "@react-router/dev/routes";

export default [
  index("routes/home.tsx"),
  route("login", "routes/login.tsx"),
  route("signup", "routes/signup.tsx"),
  layout("routes/protected-layout.tsx", [
    route("auth", "routes/authenticated.tsx"),
  ]),
  route("health", "routes/health.tsx"),
] satisfies RouteConfig;
