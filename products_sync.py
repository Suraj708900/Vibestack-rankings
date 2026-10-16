# Sync products from /workspace/products/catalog.json (local only) into data/products-config.json: names, INR/USD prices, taglines, descriptions, files, order. Adds new products.
def _sync():
    import json,os
    src=os.environ.get('PRODUCTS_CATALOG','/workspace/products/catalog.json'); cfgp=os.path.join(ROOT,'data','products-config.json')
    if not os.path.exists(src): return
    cat=json.load(open(src)); cat=cat.get('products',cat) if isinstance(cat,dict) else cat
    cfg=json.load(open(cfgp)); old=cfg['products']; new={}
    U={'monthly':'/month'}
    for it in cat:
        s=it['slug']; c=dict(old.get(s,{}))
        b=(it.get('billing') or '').strip()
        c.update(name=it['name'],price=it['price_inr'],price_usd=it['price_usd'],tagline=it.get('tagline',''),description=it.get('description',''),
                 file='products/'+os.path.basename(it['file']),cover='c-'+s,includes='Guide book included',
                 unit=U.get(b,(' per participant' if b.startswith('per participant') else (' '+b if b else ''))))
        new[s]=c
    cfg['products']=new
    cfg['_note']="Synced from /workspace/products/catalog.json by products_sync.py (prices marked 'suggested - Suraj to confirm' in the catalog). 'file' is the private Blob pathname delivered after payment. paypal_link is a template ({email},{item},{usd},{order}); can be swapped for a PayPal.me link later. All products are paid; the guide book is included with each."
    json.dump(cfg,open(cfgp,'w'),indent=1,ensure_ascii=False); print('products synced:',len(new))
_sync()
