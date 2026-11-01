import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';
const fonts={"NotoSans": "b85c38ecea8a7cfb39c24e395a4007474fa5a4fc864f6ee33309eb4948d232d5", "NotoSansDevanagari": "385e78e6359a9d88a0f243d53b1209d7548361ba2194e2b9ec779bcaa7e8949d"};
await fs.mkdir(new URL('./public/fonts/',import.meta.url),{recursive:true});
for(const [name,expected]of Object.entries(fonts)){
 const path=new URL('./public/fonts/'+name+'.ttf',import.meta.url);let bytes;
 try{bytes=await fs.readFile(path)}catch{}
 const valid=b=>b&&createHash('sha256').update(b).digest('hex')===expected;
 if(!valid(bytes)){const response=await fetch('https://raw.githubusercontent.com/notofonts/noto-fonts/main/hinted/ttf/'+name+'/'+name+'-Regular.ttf');if(!response.ok)throw Error('Unable to download '+name);bytes=Buffer.from(await response.arrayBuffer());if(!valid(bytes))throw Error('Font checksum changed: review upstream before updating the pinned hash.');await fs.writeFile(path,bytes)}
}
