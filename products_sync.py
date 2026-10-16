# Sync product names/prices/files from /workspace/products/catalog.json (another worker's catalog) into data/products-config.json when it exists locally.
def _sync():
    import json,os
    src=os.environ.get('PRODUCTS_CATALOG','/workspace/products/catalog.json'); cfgp=os.path.join(ROOT,'data','products-config.json')
    if not os.path.exists(src): return
    cat=json.load(open(src)); items=cat.get('products',cat) if isinstance(cat,dict) else cat
    if isinstance(items,dict): items=[dict(v,slug=k) for k,v in items.items()]
    cfg=json.load(open(cfgp)); n=0
    def first(d,*ks):
        for k in ks:
            if d.get(k) not in (None,''): return d[k]
    for it in items:
        s=it.get('slug') or it.get('id')
        if s not in cfg['products']: continue
        c=cfg['products'][s]
        for dst,keys in (('name',('name','title')),('price',('price_inr','suggested_price_inr','price')),('price_usd',('price_usd','suggested_price_usd')),('file',('file','blob_path')),('unit',('unit',))):
            v=first(it,*keys)
            if isinstance(v,dict): v=first(v,'low','min','suggested')
            if v not in (None,''): c[dst]=v; n+=1
    json.dump(cfg,open(cfgp,'w'),indent=1,ensure_ascii=False); print('products catalog synced fields:',n)
_sync()
