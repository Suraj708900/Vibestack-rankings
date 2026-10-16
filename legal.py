# Legal pages content for build.py (plain HTML fragments). Not legal advice.
EMAIL='kamdevsuraj03@gmail.com'
UPD='16 Oct 2026'
NOTE=f'<p class="sub">Last updated {UPD}. This page is a plain-language summary provided for transparency and is not legal advice.</p>'
def S(h,*ps): return f'<h2>{h}</h2>'+''.join(f'<p>{p}</p>' for p in ps)
CONTACT=S('Contact',f'Questions about this page: <a href="mailto:{EMAIL}">{EMAIL}</a>.')
PAGES={
'privacy':('Privacy Policy','How VibeStack Rankings handles data: newsletter emails via Resend, Vercel analytics, first-party click tracking, cookies, affiliate links and your choices.',
 S('Who we are','VibeStack Rankings ("we", "us") is an independent directory of AI tools for builders, run by Suraj Kamdev.')+
 S('What we collect','<b>Newsletter:</b> if you subscribe, we store your email address with our email provider, Resend, to send the newsletter. Every email includes an unsubscribe link and you can unsubscribe at any time.',
   '<b>Analytics:</b> we use Vercel Web Analytics and Vercel Speed Insights to understand aggregate traffic and page performance. These are designed to work without third-party advertising cookies.',
   '<b>Click tracking:</b> we count clicks on outbound tool links (including /go/ links), promo impressions/clicks and promo-code copy events using our own first-party endpoint. These counts are aggregated and used to improve the site and report to partners in aggregate.',
   '<b>Submissions and email:</b> if you submit a tool or email us, we keep what you send so we can respond.')+
 S('Cookies and local storage','We do not use advertising cookies. The site may use browser storage (for example session storage) to avoid counting the same promo impression twice in one session. You can clear or block this in your browser.')+
 S('Affiliate and third-party links','Some outbound links are affiliate links. When you click through, the destination site and any affiliate network may set their own cookies and process data under their own privacy policies, which we do not control.')+
 S('Sharing','We do not sell your personal data. We share data only with the service providers needed to run the site (such as Vercel for hosting and analytics and Resend for email), or where required by law.')+
 S('Your choices','You can unsubscribe from the newsletter at any time, and you can email us to ask for access to or deletion of data we hold about you.')+
 S('Children','The site is not directed at children under 13 and we do not knowingly collect their data.')+
 S('Changes','We may update this policy; the date above shows the latest version.')+CONTACT),
'terms':('Terms of Use','Terms for using VibeStack Rankings: editorial rankings, affiliate links, sponsored and featured listings, promo codes, third-party sites and no warranty.',
 S('Acceptance','By using VibeStack Rankings you agree to these terms. If you do not agree, please do not use the site.')+
 S('Editorial content','Rankings, verdicts and guides are our opinions, based on our own research. Tool features and prices change often; always check the official site before you buy.')+
 S('Affiliate links','Some links, including links under /go/, are tracked and may be affiliate links. We may earn a commission if you buy through them, at no extra cost to you. Commissions never decide rankings.')+
 S('Promo codes and deals','Deals and promo codes are provided by third parties or found publicly. They may change, expire or not work for every account or region, and are not guaranteed.')+
 S('Featured and sponsored listings','Paid placements are always labelled as sponsored or featured. Paying for a placement does not change a tool\'s editorial ranking. We may decline or remove any placement, for example for misleading content.')+
 S('Third-party sites','We link to third-party websites and tools we do not control. We are not responsible for their content, products, pricing or policies.')+
 S('Acceptable use','Do not misuse the site: no scraping that harms performance, no attempts to manipulate click or submission data, and no unlawful activity.')+
 S('No warranty','The site is provided "as is" without warranties of any kind. To the extent permitted by law, we are not liable for losses arising from your use of the site or of any tool listed on it.')+
 S('Changes','We may update these terms; the date above shows the latest version.')+CONTACT),
'refund':('Refund Policy','Refund policy for paid featured and sponsored listings on VibeStack Rankings: when refunds apply, cancellations, and how to request one by email.',
 S('Scope','Using VibeStack Rankings is free. This policy covers only paid featured or sponsored listings purchased by tool makers. Prices and terms for each placement are agreed in writing before payment.')+
 S('Before a placement goes live','If you cancel before your placement is published, you can request a full refund.')+
 S('After a placement goes live','Once a placement is live, fees are generally non-refundable, because the slot was reserved for you. If we fail to run the placement as agreed (for example it is missing for part of the period because of our error), we will extend the placement or refund the affected portion.')+
 S('Removed placements','If we remove a placement because it breaks our guidelines (for example misleading claims), any refund is at our discretion. If we remove it for our own reasons, we will refund the unused portion.')+
 S('Affiliate purchases','Purchases you make on third-party sites through our links are handled by those companies. Refund requests for those products must go to the seller.')+
 S('How to request',f'Email <a href="mailto:{EMAIL}">{EMAIL}</a> with your placement details. We aim to reply within a few business days; approved refunds go back to the original payment method.')),
'disclaimer':('Disclaimer','VibeStack Rankings disclaimer: opinions not advice, affiliate commissions, sponsored listings labelled, promo codes not guaranteed, no warranty on accuracy.',
 S('Opinions, not advice','Content on VibeStack Rankings is for general information. It reflects our opinions and is not professional, financial, legal or security advice.')+
 S('Accuracy','We try to keep information current, but AI tools change quickly. Pricing, features and availability may be out of date; check the official source before relying on it.')+
 S('Directory listing stats','Directory listing stats (pricing, features, user counts, ratings and similar claims) are copied from each tool\'s own website, with a source link; GitHub figures come from GitHub and popularity ranks from the public Tranco list. We do not verify or estimate them.')+
 S('Affiliate disclosure','Some links are affiliate links and are tracked through /go/ redirects. We may earn a commission at no extra cost to you. Rankings are never sold.')+
 S('Sponsored and featured listings','Paid placements are always clearly labelled and do not affect editorial rankings.')+
 S('Promo codes','Promo codes and deals are not guaranteed and may expire or have conditions set by the vendor.')+
 S('Trademarks','Product names and logos belong to their owners. Their use here does not imply endorsement.')+
 S('No warranty','The site is provided "as is", without warranties. Use any listed tool at your own risk.')+CONTACT),
}
