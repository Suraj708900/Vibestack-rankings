# Google sign-in configuration

Prepared configuration for AIUseFlow using the supplied public Google OAuth Client ID. No client secret is needed for the existing GIS popup ID-token flow.

## Scope
Three PHP files only: new public Client ID helper, providers configuration, and Google credential endpoint. Existing private configuration overrides the public fallback. No changes to account storage, passwords, checkout, prices, ad/consent scripts, or website design.

## Validation still required
- Verify fresh hosting backup and restoration before production changes.
- Parse PHP and test staging providers, rejected invalid credentials and existing email login.
- Verify Google button on desktop and mobile.
- Complete an actual Google login with an account under the owner's control.
- Check Google Cloud Audience publishing/test user settings.
- Obtain explicit approval before production deployment.

Production has not been changed by this preparation.
