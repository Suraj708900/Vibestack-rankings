# November 2026 utility guides and Klap media

Run `python editorial/build-utility-guides.py` from the repository root to build the scoped HTML release. Article copy and SEO topics are in `utility-guides-20261102.json`; screenshots are original captures of the public tool interfaces under `assets/blog-guides-20261102/`.

The three public HTML snapshots in `templates/` preserve the actual live navigation, consent integrations and existing article/index content. The builder adds ten guides and Klap media without removing the old blog cards or article copy. Generated release files are ignored; published HTML is also preserved under the repository's normal `blog/` and `t/` paths.

The Klap video remains hosted by Klap with native playback controls, no autoplay, preload disabled and a direct fallback link. The product screenshot is attributed. These media additions do not certify Klap's advertised outcomes or change affiliate disclosures.

Deployment is by bounded file uploads, with backups and live content checks. Do not deploy the repository's older root Python/Vercel build over Hostinger. No new recurring job, payment, API subscription or database migration is needed.
