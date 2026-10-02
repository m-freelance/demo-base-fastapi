export const environment = {
  production: true,
  // Empty on purpose: requests resolve to /api/v1 on whatever origin serves
  // the app, so there is no hostname to guess and no mixed content over HTTPS.
  // The deployment has to proxy /api to the backend. See frontend/README.md.
  backendUrl: ''
};
