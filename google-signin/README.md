# Google sign-in configuration

Prepared configuration for AIUseFlow using the supplied public Google OAuth Client ID. No client secret is needed for the existing GIS popup ID-token flow.

## Scope
Three PHP files only: new public Client ID helper, providers configuration, and Google credential endpoint. Existing private configuration overrides the public fallback. No changes to account storage, passwords, checkout, prices, ad/consent scripts, or website design.

## Verified in staging
- Backup archive: seven entries restored in memory and checked against SHA-256; SQLite integrity check passed.
- Thirteen server checks passed, including valid signed fixture, invalid audiences/issuers/algorithms, expiration, key lookup, and live Google public-key retrieval.
- Six HTTP checks passed: provider configuration, GET rejection, missing Origin, missing/invalid credential, and live provider still disabled.
- Official Google button renders in staging.
- Staging does not create customer accounts or sessions.

## Validation still required
- Verify fresh hosting backup and restoration before production changes.
- Parse PHP and test staging providers, rejected invalid credentials and existing email login.
- Verify Google button on desktop and mobile.
- Complete an actual Google login with an account under the owner's control.
- Check Google Cloud Audience publishing/test user settings.
- Obtain explicit approval before production deployment.

Production deployment approved by the owner and completed on 3 November 2026. Three configuration files published with a fresh checksum-verified backup and SQLite integrity check. Five live HTTP checks passed. Real-account Google sign-in is pending owner testing. Existing cached provider responses may persist for up to five minutes.


## Final login page correction
A scoped CSS rule on login.html and signup.html now honors hidden attributes for unconfigured providers. This hides GitHub and Facebook until configured and leaves Google and email login available. Original page content, metadata, scripts and forms are byte-identical after removing this one added rule. A second fresh backup was verified before publication.
